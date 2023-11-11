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

from models import Usuario
from database import get_database


app = FastAPI()

app.mount("/static", StaticFiles(directory="public/dist"), name="static")

templates = Jinja2Templates(directory="public/templates")


@app.get("/", response_class=HTMLResponse, tags=["login"])
async def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/login/recover", response_class=HTMLResponse, tags=["login"])
async def recover(request: Request):
    return templates.TemplateResponse("recover.html", {"request": request})
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
