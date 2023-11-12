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
