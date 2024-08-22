# Api/routes/auth/auth.py
from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from db.connection import get_session
from sqlalchemy.orm import Session
from typing import Optional
from core.utils.serverStatus import serverStatus
from core.utils.userValidations import *
from Api.crud.auth import *

templates = Jinja2Templates(directory="public/templates")

router = APIRouter()

@router.get("/", tags=["routes"])
async def root():
    return RedirectResponse(url="/auth/login")


@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    alert = request.session.pop("alert", None)
    triedUser = request.session.pop("triedUser", None)
    return templates.TemplateResponse("./auth/login.html", {"request": request, "alert": alert, "triedUser": triedUser})

@router.get("/login/recover", response_class=HTMLResponse)
async def recover(request: Request):
    return templates.TemplateResponse("./auth/recover.html", {"request": request})

@router.post("/login")
async def login_post(
    request: Request,
    user: Optional[str] = Form(""),
    password: Optional[str] = Form(""),
    db: Session = Depends(get_session),
):
    request.session["triedUser"] = user

    # Verificar si el servidor de base de datos está disponible y acepta conexiones
    if not serverStatus(db, request):
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    # Validar usuario y contraseña usando userValidations
    if not userValidation(user, password, request):
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar el caracter del usuario (correo o cédula) usando verificateCharacter
    usuario = verificateCharacter(user, db)

    # Si el usuario no existe, mostrar mensaje de error
    if not checkUserExist(usuario, request):
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    # Verificar si el usuario tiene un rol válido   
    if checkRoleUser(usuario.rol, request):
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar si la contraseña no es nula
    if usuario.contrasena == None:
        alert = {"type": "pass", "message": "La contraseña que ingresaste es incorrecta.","link": "/login/recover"}
        request.session["alert"] = alert
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    # Verificar si la contraseña es correcta
    if not verifyPassword(password, usuario.contrasena, request):
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar si el usuario está inactivo
    if checkStatusUser(usuario.estado, request):
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    response = RedirectResponse(url="/home",status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="c_user",value=tokenConstructor(usuario.id_usuario))

    return response
