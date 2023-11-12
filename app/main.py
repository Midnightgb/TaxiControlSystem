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

from models import Usuario
from database import get_database


app = FastAPI()

app.mount("/static", StaticFiles(directory="public/dist"), name="static")

templates = Jinja2Templates(directory="public/templates")


@app.get("/", tags=["routes"])
async def root():
    return RedirectResponse(url="/login")


@app.get("/login", response_class=HTMLResponse, tags=["routes"])
async def login(request: Request, alert: str = None):
    print("alerta")
    print(alert)
    return templates.TemplateResponse("./auth/login.html", {"request": request, "alert": alert})


@app.get("/login/recover", response_class=HTMLResponse, tags=["routes"])
async def recover(request: Request):
    return templates.TemplateResponse("./auth/recover.html", {"request": request})

@app.post("/login", response_class=HTMLResponse, tags=["auth"])
async def login_post(
    request: Request,
    user: Optional[str] = Form(None),
    contrasena: Optional[str] = Form(None),
    db: Session = Depends(get_database)
):
    if not all([user, contrasena]):
        alert = {"tipo": "danger", "mensaje": "Todos los campos son requeridos", "class" : "error"}
        return RedirectResponse(url=f"/login?alert={alert}", status_code=status.HTTP_303_SEE_OTHER)
    
    if not user:
        alert = {"tipo": "danger", "mensaje": "El usuario es requerido", "class" : "error"}
        return RedirectResponse(url=f"/login?alert={alert}", status_code=status.HTTP_303_SEE_OTHER)
    if not contrasena:
        alert = {"tipo": "danger", "mensaje": "La contraseña es requerida", "class" : "error"}
        return RedirectResponse(url=f"/login?alert={alert}", status_code=status.HTTP_303_SEE_OTHER)
    
    if '@' in user:
        usuario = db.query(Usuario).filter(Usuario.correo == user).first()
    else:
        usuario = db.query(Usuario).filter(Usuario.cedula == user).first()

    if not usuario:
        alert = {"tipo": "danger", "mensaje": "Usuario incorrecto", "class" : "error"}
        return RedirectResponse(url=f"/login?alert={alert}", status_code=status.HTTP_303_SEE_OTHER)
    
    if not bcrypt.checkpw(contrasena.encode('utf-8'), usuario.contrasena.encode('utf-8')):
        alert = {"tipo": "danger", "mensaje": "Contraseña incorrecta", "class" : "error"}
        return RedirectResponse(url=f"/login?alert={alert}", status_code=status.HTTP_303_SEE_OTHER)

    if usuario.estado != 'Activo':
        alert = {"tipo": "danger", "mensaje": "Usuario inactivo", "class" : "error"}
        return RedirectResponse(url=f"/login?alert={alert}", status_code=status.HTTP_303_SEE_OTHER)
    
    #response = RedirectResponse(url="/home", status_code=status.HTTP_303_SEE_OTHER)

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


# -- PATH TO  PAYMENSTS -- #

@app.get("/PathPayments", response_class=HTMLResponse, tags=["payments"])
def payments(request: Request,
            db: Session = Depends(get_database)
            ):
    
    usuarios = db.query(Usuario).filter(Usuario.rol=="Conductor").all()

    return templatesReports.TemplateResponse("CreatePayments.html", {"request": request,"usuarios":usuarios})


@app.post("/CreatePayments", )
def CreatePyments(conductor: int = Form(...),
    valor: int = Form(...),
    fecha: str = Form(...),
    db: Session = Depends(get_database)
    ):

    try:
        report= Pago(conductor=conductor,valor=valor,fecha=fecha)
        db.add(report)
        db.commit()
        db.refresh(report)
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        
    except:
        raise HTTPException(status_code=400, detail="Error al crear el pago.")

    Response
# -- END OF THE ROUTE -- #
