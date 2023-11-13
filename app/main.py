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
from sqlalchemy.orm import Session, joinedload
import bcrypt
import os
from dotenv import load_dotenv
from functions import tokenConstructor, serverStatus
from models import Usuario
from datetime import date 
from models import Usuario, Pago, Taxi
from database import get_database
from starlette.middleware.sessions import SessionMiddleware


load_dotenv()
MIDDLEWARE_KEY = os.environ.get("MIDDLEWARE_KEY")

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
        alert = {"type": "general",
                 "message": "Error en conexión al servidor, contacte al proveedor del servicio."}
        request.session["alert"] = alert
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    if not user and not password:
        alert = {"type": "user",
                 "message": "El correo o la cédula que ingresaste no coincide con ningún usuario."}
        request.session["alert"] = alert
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    if '@' in user:
        usuario = db.query(Usuario).filter(Usuario.correo == user).first()
    else:
        usuario = db.query(Usuario).filter(Usuario.cedula == user).first()

    if not usuario:
        alert = {"type": "user",
                 "message": "El correo o la cédula que ingresaste no coincide con ningún usuario."}
        request.session["alert"] = alert
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    if not bcrypt.checkpw(password.encode('utf-8'), usuario.contrasena.encode('utf-8')):
        alert = {"type": "pass",
                 "message": "La contraseña que ingresaste es incorrecta.", "link": "/login/recover"}
        request.session["alert"] = alert
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    if usuario.estado == 'Inactivo':
        alert = {"type": "general",
                 "message": "El usuario se encuentra inactivo, contacte al proveedor del servicio."}
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
# -- PATH TO REDIRECT TO USER CREATION -- #


@app.get("/PathCreateUser", response_class=HTMLResponse, tags=["create"])
async def create(request: Request):
    return templates.TemplateResponse("CreateUser.html", {"request": request})
# -- END OF THE ROUTE -- #

# -- PATH TO PROCEED TO THE CREATION OF A NEW USER -- #


@app.post("/CreateUser", response_class=HTMLResponse)
async def CreateUser(
    request: Request,
    cedula: int = Form(...),
    nombre: str = Form(...),
    apellido: str = Form(...),
    correo: str = Form(...),
    contrasena: str = Form(...),
    rol: str = Form(...),
    db: Session = Depends(get_database)
):
    cedula_existente = db.query(Usuario).filter(
        Usuario.cedula == cedula).first()
    if cedula_existente:
        raise HTTPException(
            status_code=400, detail="La cédula ya está en uso.")

    correo_existente = db.query(Usuario).filter(
        Usuario.correo == correo).first()
    if correo_existente:
        raise HTTPException(
            status_code=400, detail="El correo ya está en uso.")

    nuevo_usuario = Usuario(cedula=cedula, nombre=nombre, apellido=apellido,
                            correo=correo, contrasena=contrasena, rol=rol, estado='Activo')
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return templates.TemplateResponse("index.html", {"request": request})


# -- MODULO 2-- #

@app.get("/register/daily/view", response_class=HTMLResponse, tags=["routes"])
async def registro_diario_view(request: Request):
    return templates.TemplateResponse("registrer_dialy.html", {"request": request})

@app.post("/register/daily", response_class=HTMLResponse)
async def registro_diario(
    request: Request,
    id_conductor: int = Form(...),
    valor: int = Form(...),
    estado: bool = Form(...),
    db: Session = Depends(get_database)
):
   
    fecha_actual = date.today()  # fecha actual
   
    pago_existente = db.query(Pago).filter(
        Pago.id_conductor == id_conductor,
        Pago.fecha == fecha_actual,
        Pago.cuota_diaria_registrada == True
    ).first()

    if pago_existente:
        raise HTTPException(status_code=400, detail="La cuota diaria ya ha sido registrada para este conductor hoy.")

    cuota_diaria_taxi = db.query(Taxi.cuota_diaria).filter(
        Taxi.id_conductor == id_conductor
    ).scalar()

   
    if valor < cuota_diaria_taxi:
        estado = False
        
    nuevo_pago = Pago(
        id_conductor=id_conductor,
        fecha=fecha_actual,
        valor=valor,
        estado=estado,
        cuota_diaria_registrada=True  
    )

    db.add(nuevo_pago)
    db.commit()
    db.refresh(nuevo_pago)

    return templates.TemplateResponse("index.html", {"request": request})
    
# -- FIN MODULO 2-- #




