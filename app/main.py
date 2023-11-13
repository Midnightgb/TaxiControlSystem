from typing import Optional
from fastapi import (
    FastAPI,
    Request,
    Form,
    status,
    Depends,
    HTTPException,
    Cookie,
    Query,
    Response,
)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet 
import bcrypt
import os 
from dotenv import load_dotenv

from functions import tokenConstructor, serverStatus, tokenDecoder
from models import Usuario, Empresa, Taxi
from database import get_database
from starlette.middleware.sessions import SessionMiddleware

load_dotenv()
MIDDLEWARE_KEY = os.environ.get("MIDDLEWARE_KEY")


# ============================ CRYPTOGRAPHY ============================ #
# Generar una clave para Fernet y crear el objeto Fernet
cipher_key = Fernet.generate_key()
cipher_suite = Fernet(cipher_key)
# ============================ ENDCRYPTOGRAPHY ============================ #

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=MIDDLEWARE_KEY)
app.mount("/static", StaticFiles(directory="public/dist"), name="static")
templates = Jinja2Templates(directory="public/templates")


@app.get("/", tags=["routes"])
async def root():
    return RedirectResponse(url="/login")

@app.get("/login", response_class=HTMLResponse, tags=["routes"])
async def login(request: Request):
    alert = request.session.pop("alert", None)
    return templates.TemplateResponse("./auth/login.html", {"request": request, "alert": alert})

@app.get("/login/recover", response_class=HTMLResponse, tags=["routes"])
async def recover(request: Request):
    return templates.TemplateResponse("./auth/recover.html", {"request": request})

@app.post("/login", tags=["auth"])
async def login_post(
    request: Request,
    user: Optional[str] = Form(""),
    password: Optional[str] = Form(""),
    db: Session = Depends(get_database),
):
    
    if not serverStatus(db):
        alert = {"type": "general","message": "Error en conexión al servidor, contacte al proveedor del servicio."}
        request.session["alert"] = alert
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    if not user and not password:
        alert = {"type": "user","message": "El correo o la cédula que ingresaste no coincide con ningún usuario."}
        request.session["alert"] = alert
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    if '@' in user:
        usuario = db.query(Usuario).filter(Usuario.correo == user).first()
    else:
        usuario = db.query(Usuario).filter(Usuario.cedula == user).first()

    if not usuario:
        alert = {"type": "user","message": "El correo o la cédula que ingresaste no coincide con ningún usuario."}
        request.session["alert"] = alert
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    if not bcrypt.checkpw(password.encode('utf-8'), usuario.contrasena.encode('utf-8')):
        alert = {"type": "pass","message": "La contraseña que ingresaste es incorrecta.", "link": "/login/recover"}
        request.session["alert"] = alert
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    if usuario.estado == 'Inactivo':
        alert = {"type": "general","message": "El usuario se encuentra inactivo, contacte al proveedor del servicio."}
        request.session["alert"] = alert
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    response = RedirectResponse(
        url="/home", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="c_user", value=tokenConstructor(usuario.id_usuario))
    return response

@app.get("/home", response_class=HTMLResponse, tags=["routes"])
async def home(request: Request):
    return templates.TemplateResponse("./index.html", {"request": request})



# ========================================== USERBLOCK ============================================ #

# -- PATH TO REDIRECT TO USER CREATION -- #
@app.get("/register/user", response_class=HTMLResponse, tags=["create"])
async def create(request: Request, c_user: str = Cookie(None), db: Session = Depends(get_database)):
    user_id = None

    if not serverStatus(db):
        alert = {"type": "general","message": "Error en conexión al servidor, contacte al proveedor del servicio."}
        request.session["alert"] = alert
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    if not c_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    token_payload = tokenDecoder(c_user)
    print("##########$$$$$$$$$$$$########## token ##########$$$$$$$$$$$$##########")
    print("Token decodificado:", token_payload)

    if not token_payload:
        alert = {"type": "general","message": "Su sesion ha expirado, por favor inicie sesión nuevamente."}
        request.session["alert"] = alert
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    user_id = int(token_payload["sub"])
    usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()

    if not usuario:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    empresas = db.query(Empresa).filter(Empresa.id_empresa == usuario.empresa_id).first()

    if not empresas:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse("CreateUser.html", {"request": request, "empresas": empresas, "usuario": usuario})
# -- END OF THE ROUTE -- #

# -- PATH TO PROCEED TO THE CREATION OF A NEW USER -- #
@app.post("/register/user", response_class=HTMLResponse)
async def CreateUser(
    request: Request,
    cedula: str = Form(...),
    nombre: str = Form(...),
    apellido: str = Form(...),
    correo: str = Form(...),
    contrasena: str = Form(...),
    rol: str = Form(...),
    empresa_id: int = Form(...),
    db: Session = Depends(get_database)
):
    try:
        cedula_existente = db.query(Usuario).filter(Usuario.cedula == cedula).first()
        if cedula_existente:
            raise HTTPException(status_code=400, detail="La cédula ya está en uso.")

        correo_existente = db.query(Usuario).filter(Usuario.correo == correo).first()
        if correo_existente:
            raise HTTPException(status_code=400, detail="El correo ya está en uso.")

        # Encriptar la contraseña antes de almacenarla
        hashed_password = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt())

        # Crear el nuevo usuario
        nuevo_usuario = Usuario(
            cedula=cedula,
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            contrasena=hashed_password,
            rol=rol,
            estado='Activo',
            empresa_id=empresa_id
        )
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)

        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear usuario: {str(e)}")
# -- END OF THE ROUTE -- #

# ========================================== END OF USERBLOCK ============================================ #

# ========================================== TAXIBLOCK ============================================ #

# -- PATH TO REDIRECT TO TAXI CREATION -- #
@app.get("/register/taxi", response_class=HTMLResponse, tags=["create"])
async def create(request: Request, c_user: str = Cookie(None), db: Session = Depends(get_database)):
    user_id = None
    try:
        if not c_user:
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

        token_payload = tokenDecoder(c_user)

        user_id = int(token_payload["sub"])

        usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()

        if not usuario:
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

        empresas = db.query(Empresa).filter(Empresa.id_empresa == usuario.empresa_id).all()

        if not empresas:
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

        return templates.TemplateResponse("CreateTaxi.html", {"request": request, "empresas": empresas})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener información del usuario y empresa: {str(e)}")
# -- END OF THE ROUTE -- #

# -- PATH TO PROCEED TO THE CREATION OF A NEW TAXI -- #
@app.post("/register/taxi", response_class=HTMLResponse)
async def create_taxi(
    request: Request,
    empresa_id: int = Form(...),
    placa: str = Form(...),
    modelo: str = Form(...),
    marca: str = Form(...),
    tipo_combustible: str = Form(...),
    cuota_diaria: int = Form(...),
    db: Session = Depends(get_database)
):
    try:

        if not serverStatus(db):
            alert = {"type": "general","message": "Error en conexión al servidor, contacte al proveedor del servicio."}
            request.session["alert"] = alert
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


        # Verificar si la placa ya existe en la base de datos
        if db.query(Taxi).filter(Taxi.placa == placa).first():
            raise HTTPException(status_code=400, detail="La placa ya está registrada.")
            
        # Si pasa las validaciones, proceder con la creación del nuevo taxi
        nuevo_taxi = Taxi(
            empresa_id=empresa_id,
            placa=placa,
            modelo=modelo,
            marca=marca,
            tipo_combustible=tipo_combustible,
            cuota_diaria=cuota_diaria
        )

        db.add(nuevo_taxi)
        db.commit()
        db.refresh(nuevo_taxi)

        return templates.TemplateResponse("index.html", {"request": request, "message": "Taxi creado con éxito"})
    except HTTPException as e:
        # Capturamos las excepciones específicas de FastAPI
        return templates.TemplateResponse("index.html", {"request": request, "error_message": e.detail})
    except Exception as e:
        # Capturamos otras excepciones y mostramos un mensaje genérico de error
        return templates.TemplateResponse("index.html", {"request": request, "error_message": "Error al procesar la solicitud."})
# -- END OF THE ROUTE -- #
