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
    UploadFile,
)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
import bcrypt
import os
from dotenv import load_dotenv
from datetime import date, datetime, timedelta
import calendar
from collections import defaultdict

from functions import *
from models import *

from database import get_database
from starlette.middleware.sessions import SessionMiddleware

from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy import or_, func,extract


load_dotenv()
MIDDLEWARE_KEY = os.environ.get("MIDDLEWARE_KEY")

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=MIDDLEWARE_KEY)
app.mount("/static", StaticFiles(directory="public/dist"), name="static")
templates = Jinja2Templates(directory="public/templates")

MONTHS_IN_SPANISH = {
    'January': 'Enero',
    'February': 'Febrero',
    'March': 'Marzo',
    'April': 'Abril',
    'May': 'Mayo',
    'June': 'Junio',
    'July': 'Julio',
    'August': 'Agosto',
    'September': 'Septiembre',
    'October': 'Octubre',
    'November': 'Noviembre',
    'December': 'Diciembre'
}

@app.get("/", tags=["routes"])
async def root():
    return RedirectResponse(url="/logout")


@app.get("/login", response_class=HTMLResponse, tags=["routes"])
async def login(request: Request):
    alert = request.session.pop("alert", None)
    triedUser = request.session.pop("triedUser", None)
    return templates.TemplateResponse("./auth/login.html", {"request": request, "alert": alert, "triedUser": triedUser})


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
    request.session["triedUser"] = user
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
    role = usuario.rol
    print(role)
    if role == Rol.Conductor:
        print('entro')
        alert = {"type": "user",
                 "message": "El correo o la cédula que ingresaste no coincide con ningún usuario."}
        request.session["alert"] = alert
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    if usuario.contrasena == None:
        alert = {"type": "pass", "message": "La contraseña que ingresaste es incorrecta.",
                 "link": "/login/recover"}
        request.session["alert"] = alert
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    if not bcrypt.checkpw(password.encode('utf-8'), usuario.contrasena.encode('utf-8')):
        alert = {"type": "pass", "message": "La contraseña que ingresaste es incorrecta.",
                 "link": "/login/recover"}
        request.session["alert"] = alert
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    if usuario.estado == Estado.Inactivo:
        alert = {"type": "general",
                 "message": "El usuario se encuentra inactivo, contacte al proveedor del servicio."}
        request.session["alert"] = alert
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    response = RedirectResponse(
        url="/home",
        status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="c_user",
        value=tokenConstructor(usuario.id_usuario))

    return response


@app.get("/home", response_class=HTMLResponse, tags=["routes"])
async def home(request: Request, c_user: str = Cookie(None), db: Session = Depends(get_database)):
    if not c_user:
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    checkTokenStatus = userStatus(c_user, request)
    if not checkTokenStatus["status"]:
        return checkTokenStatus["redirect"]

    if not serverStatus(db):
        alert = {"type": "general",
                 "message": "Error en conexión al servidor, contacte al proveedor del servicio."}
        request.session["alert"] = alert
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    UUID = checkTokenStatus["userid"]
    userData = db.query(Usuario).filter(Usuario.id_usuario == UUID).first()
    if not userData:
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    empresa = db.query(Empresa).filter(
        Empresa.id_empresa == userData.empresa_id).first()

    if not empresa:
        alert = {"type": "general",
                 "message": "Error al obtener información de la empresa."}
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    # Querys para obtener la información del dashboard
    assistantsInCompany = db.query(Usuario).filter(
        Usuario.rol == "Secretaria", Usuario.empresa_id == empresa.id_empresa).all()
    carsInCompany = db.query(Taxi).filter(
        Taxi.empresa_id == empresa.id_empresa).all()
    driversInCompany = db.query(Usuario).filter(
        Usuario.rol == "Conductor", Usuario.empresa_id == empresa.id_empresa).all()
    #falta filtrar por empresa los datos de ingresos y gastos
    incomeTodayInCompany = db.query(Pago).filter(Pago.fecha == date.today()).all()
    expensesTodayInCompany = db.query(Mantenimiento).filter(Mantenimiento.fecha == date.today()).all()
    monthlyReports = db.query(Reporte).filter(Empresa.id_empresa == empresa.id_empresa).all()
    

    expensesToday = 0
    for expense in expensesTodayInCompany:
        expensesToday += expense.costo

    incomeToday = 0
    for income in incomeTodayInCompany:
        incomeToday += income.valor
    numAssistants = 0
    numCars = 0
    numDrivers = 0

    for assistant in assistantsInCompany:
        numAssistants += 1
    for car in carsInCompany:
        numCars += 1
    for driver in driversInCompany:
        numDrivers += 1

    if incomeToday < expensesToday:
        src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAACXBIWXMAAAsTAAALEwEAmpwYAAAFfUlEQVR4nO2aW2xURRjHB4iX+GAMCvESoiagxlvUmBgTTXwxYqKWdudr0SLEGJv4AJxTsAjGFI0XAgrii0p4wCiCJQqRB4K37jm9BORiIkhALuFS2hAEb9wU6M98e3bDdm/tQnu23d1/Mg+7Z2a+mf/5vpn/fGeMSQJVVeMQmYnILEReRmQK1goijyPyCFVVdzB+/BWmWIG1exAhZ7H2PNYeRKQZkaWIzEGkkokTbzRDHYjs7pWA3OUA1n6JiIvIw9TVXWaGEhAZi8jrWDsPaxci8gnWLkPkK0TaYhMU+TcPQv5EZCXW1iIy0hQDMGYYItfH3rDIS1i7GJHvsfZoL2ScQySKtQ6VlaNNMQKR2xF5Me41+3KsI/8hsoZIpGLIhUk+oKbmtviuogvm2SyEHEFkPjU1Y0wxA5GRsZAR8RHpzuIVy6mufsAUOxC5Nb7YHswSIj8SiTxmih00Ng6nuvpprP0ui1e0Eok8akoBiNyHSFNMaPUkQolZoyrUlAJQuS3yaXzb7LlGWLuA2tqrTSkAkTuxdnWGNaILkedNqYBAcG3IQMS6fLbO2HojMilWjBlmhhLQwVv7QlwzJIfFX4jU9WVC8ckn2tWaoQgqKq6Jn0BTdwvdRW7K2VZkblKbuWYog+rqJ9I0hJ5FIpGnSoIAhe4GsdNqT/3QHT+cXW6KnYAEiESeRKQzJSzaqay8oSQIUCAyCpFvU0LiMJHIQyVBgAKREYi82yMkrD2NyLMlQUACuhBi7fEUKf1KyRCQJKf3poVEqRCgYMKEa+O5h0xJmOIggAvydlaWom7/d78TULeZq6b53Ot4VLgtTHZaqHNbmJUo8d+TY8+j3KP1zQCgh7zNr/SdAGlihNPKg47HTMdjrePR4fqQb9F22t6NMkP7034LRkBfzgLTooxzPeY6PgcvZsK9EuLT5XgsntbM3ZeUotdvDsF3jL4VkedyHp6mN3OL67HK9ejONviZLfDOJvh4G6zcBat2w9p9F4r+XrEreP72pqB+VjLUjscqtWsKDVfd0+d06iDntMPnO6G9EzpPwPlu8oLW13baXvvR/jKEyCnHxy3IxBthuOvxYfKA6n1Ysh12HINzeU64N2h/vx4L+q9PJ2KxjidUAup9XksexKKfoeMfQoHaWbg1jYRXQ5v8jDZGq/sljGtM9/cb7w1q74tdPdaFk1N9RoVCgOMxJWF4wZb847s/SXg/2RNamBwKAa7H7ITRr/dQUOgOkuQFs0P3gPlbwnf/BNTue0ke4PiEk/qe6jNKYy5heMUgWAMcnxP1zVxnwoKbFAZadFU+FNIuoHZ6xH5AQIMJE40wfPXedHGyZFuwXw+YDtiWblPHYSD8DxcA0Q5oaE0flCq3z3ZCWyccvkglqO1aO4N+MilBtet1BPVDn7wiMdjjZ2DZjnSFlnoWeOsn+OiXIHabUs4CTb/B8p3Bc62X6yygdtSe2k3AFAKk4I8z8MMheHNj/58EtTRuCMg6eirdYwYFAQl0x+WqhsfS7fDGxtzeke0tazttr/1of7miKNSJu82MdTz2qKtmehuZcPZ8cLrb/jtsPgLtXYG3JIr+1v/1edfJoH5foPZ1HDoeHVcoBDg+DYk3tW4/BcX6AwXYCp2yEqSsBN2yEqSsBCkrwQBlJRhHWQnGUVaCGVBWggOEshLcWs4JUs4J+gXKCbo+HwyGnKDjs6ggOUGFfp1N/kwWZk4w9nU4ynRTaMxo42bHo6m3+wH9lRNUO2pP7ZrBhHqPMbH7Ph77ByIn6Pp0Oh7zQsv8XMr6UB/lfg0P1+Ob2JWZHN6R9S0H7bS9q/2FfgegP9HYzJV6t6c+yjOuzyS9FRZLranH+DTEbon5TNLnTgt3af1Cjzkb/gfiRPzANCEGqwAAAABJRU5ErkJggg=="
    else:
        src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAACXBIWXMAAAsTAAALEwEAmpwYAAAF3UlEQVR4nO1bXWxURRS+gA+If/EHfMJfMBrQxMTokzE++abG2MRIadn5ufwo5d4FQeRhwSgh+IPog4YYQ6KIbhNJwGh8kN17W2q7M1uwFNLKT0BKK0rxgb9GoZ85e7tw96/bxXa3veyXzMP2zsyZc+acM+ecmRrGBEAEkck8yWuZEqtG2qi/AWOSEQTwJK/lWqLUxrSYZ1zPAuBKrjUCARiTaDe5lhsKN/F9cAVQBKFE6AGmRe91KYBQe2g617Ir2CYwDPNMyV99Tu8fpqR7XQhg0b5FM7gWHVeYV+IyS8hXiOnAC4D/wu9mWnZmHnlyWepb0AUgWsX9TMtuH5ODaeYDLwCu+JNMyz/8zHMlX8/sE1AB8CR/iWlx3qf2l7g263P6BVEATIs3yMn5mL9IAsnXN1ACqN1XexPTYmvm+S76Qtp8aiRh84TOBViCzWVKHszy9HsXJBbMHFnYbL46YbPBkBJ1XMlzWTv/w7zWpbcaQQZrZrcwLbZlhbSXmBLrqCZgBBlCi6eZkoeyVP5EKCGfMYIMU5vTKJ3N8vKk8jvmt712pxFkMG2+yJU8lsX4BabEIiPI4Ek+i5xabgorWkWbmGMEFYs7Ft/OldzIlBjIsHUlznJtNtREa6YYQUR9rH7qUDR3JrdwKRtNbd5jBBE1LfaNTIml5M3zqHsH0+azRhCxpHPJzUzLFRmZ29X4/CQ5uUgscoMRxOIk9yq0p/Ooej9dWNCxN5K5TI1pDS4esxy8YDehzmqCaTdhVboN/a5LfY/jUepvVAIRRCYLLZ5jSuzMPctTO/4nV3KNqc3bCs1RE8UUqxlPWA5WWA52WQ56bBcotdE4Gm/HsZzmo3nHjHFTmw9Tusm0PFrgVuY4VWqG2/GGOGbbDtZaLn6/FoaLCsRFn+Vgc0MMc0eF6QXtC2envLkWiQJl6EGuxW6hxMvD2fiyGO6zHTTaDgYLLX5FE7BeAZ/tB77pBhoPAbuOXm30e3u39/1d5fUvKAyi46CR6JbEcE20Zgrl3kyJ9VyJA4Xv4GQ/0+ITnuSPFJszpZ4uLmYv8q0W4KsuoKUX6D0HXB5ESaD+NI7G0zw0Xx4TuWC5sIs6MpEUJtcimu/c9gUvA0zJXZS60nFXjPEIMNl28LF/QWEX2NIJHOwHLpXIcDHQfAf6vfnDuYLYTOsx/DC1+WAhe86K03eGlOC8hd9hlICwizX+RWzaC/ScRVlAdD5szxHCmxkLJNvOb9eihyn5BSUuIz3CsrF8D2aQ+qWJk02P9o4XA9H7ujvDL5xf6mJ6VoIijzAlTnElv+VKLhRt4iFjFGA5qE8Tfi9Zun2PphA+8GtCE+qMcsB2sDpN9LvDqCjoBPFpweqyCMCvARuT5Vf/NIju+z4NsFzML4sAyNbI5tKEt48DH2C5OBeO4S6jXPCbATXyyifKdAoQnQzb9wSw0ign6NzdcSQ3ONmy3zuvxywO2J9Lk9ZhAOW/M6CFxXuAlc25i6LI7csuYE8vcPIaI0Ea19zrzZMvEiS6To/Xv+zME9KLPTMAbD2YG6Fl5wLvJIBPOzzbjWblAtHfgG1d3nfqN1wuQHSIHtFNw6gEkIW/B4CfTwBvt41+Jkgt0uoJ668LuRozLgSQxuBQuErm8XknsK5teO0otMs0jsbTPDTfcFZUVsbtGGZZDg6TqubbjXz497KX3XWeBvQpoKXP05Z0o9/0d/red97rPxIQfVoHrceOYVZZBEBHTnqnfjyGiuKn4xU4Cq1qJIhqJGhXI0FUI0FUI0EP1UhwCNVIcAjVSDAPqpHgGKEaCbZXa4Ko1gTdCtUEbRcfjYeaoOViU0VqggS6nfVfk5WzJpi6HY7jyn+XVAzL9+Bey0G02PuA0aoJEh2iR3SN8YSwg5mp9z4Ojo1FTdB20Ws52FC2ys//8Q/hOB4n87Ad7Ew9mRlGOwrusjeOxts0X84bgImESAxT6W1POI7nbRe19CosVVojjXGxMvVKzEUtfbeaMIf6Xwuh/wD3xNQxd3IyBwAAAABJRU5ErkJggg=="

    dataDashboard = {
        "assistants": numAssistants,
        "cars": numCars,
        "drivers": numDrivers,
        "income": {
            "totalToday": incomeToday,
            "src": src
        },
        "expenses": {
            "totalToday": expensesToday,
            "src": []
        },
        "reports": {
            "data": defaultdict(lambda: defaultdict(int)),
        }
    }
    
    for report in monthlyReports:
        report.fecha = report.fecha.strftime("%m/%d/%Y, %H:%M:%S")
        report.month = int(report.fecha.split(",")[0].split("/")[0])
        dataDashboard["reports"]["data"][report.month]["income"] += report.ingresos
        dataDashboard["reports"]["data"][report.month]["expenses"] += report.gastos
    
    dateToday = date.today()
    dateToday = dateToday.strftime("%d/%m/%Y")

    welcome = {
        "name": userData.nombre,
        "day": dateToday,
        }
    alert = request.session.pop("alert", None)
    return templates.TemplateResponse("./index.html", {"request": request, "alert": alert, "welcome": welcome, "empresa": empresa, "db": dataDashboard})



@app.get("/logout", tags=["auth"])
async def logout(request: Request):
    request.session.pop("triedUser", None)
    response = RedirectResponse(
        url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="c_user")
    return response

# ========================================== USERBLOCK ============================================ #

# -- PATH TO REDIRECT TO USER CREATION -- #


@app.get("/register/user", response_class=HTMLResponse, tags=["create"])
async def create(request: Request, c_user: str = Cookie(None), db: Session = Depends(get_database)):
    user_id = None

    if not c_user:
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    token_payload = tokenDecoder(c_user)

    if not token_payload:
        alert = {"type": "general",
                 "message": "Su sesion ha expirado, por favor inicie sesión nuevamente."}
        request.session["alert"] = alert
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    user_id = int(token_payload["sub"])
    usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()

    if not usuario:
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    empresa = db.query(Empresa).filter(
        Empresa.id_empresa == usuario.empresa_id).first()

    if not empresa:
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)
    alert = request.session.pop("alert", None)
    return templates.TemplateResponse("CreateUser.html", {"request": request, "empresa": empresa, "usuario": usuario, "alert": alert})
# -- END OF THE ROUTE -- #

# -- PATH TO PROCEED TO THE CREATION OF A NEW USER -- #


@app.post("/register/user", response_class=HTMLResponse)
async def CreateUser(
    request: Request,
    cedula: str = Form(...),
    nombre: str = Form(...),
    apellido: str = Form(...),
    correo: str = Form(...),
    contrasena: Optional[str] = Form(""),
    rol: str = Form(...),
    empresa_id: int = Form(...),
    imagen: Optional[UploadFile] = Form(None),
    db: Session = Depends(get_database),
    c_user: str = Cookie(None)
):

    if not serverStatus(db):
        alert = {"type": "general",
                 "message": "Error en conexión al servidor, contacte al proveedor del servicio."}
        request.session["alert"] = alert
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    if not c_user:
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    token_payload = tokenDecoder(c_user)

    if not token_payload:
        alert = {"type": "general",
                 "message": "Su sesion ha expirado, por favor inicie sesión nuevamente."}
        request.session["alert"] = alert
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    user_id = int(token_payload["sub"])
    usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()

    if not usuario:
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    cedula_existente = db.query(Usuario).filter(
        Usuario.cedula == cedula).first()
    if cedula_existente:
        alert = {"type": "error", "message": "La cédula ya está en uso."}
        request.session["alert"] = alert
        return RedirectResponse(url="/register/user", status_code=status.HTTP_303_SEE_OTHER)

    correo_existente = db.query(Usuario).filter(
        Usuario.correo == correo).first()
    if correo_existente:
        alert = {"type": "error", "message": "El correo ya está en uso."}
        request.session["alert"] = alert
        return RedirectResponse(url="/register/user", status_code=status.HTTP_303_SEE_OTHER)

    # Encriptar la contraseña solo si se proporciona una
    hashed_password = None
    if contrasena and rol != "Conductor":
        hashed_password = bcrypt.hashpw(
            contrasena.encode('utf-8'), bcrypt.gensalt())

    image_bytes = None
    if imagen:
        image_bytes = convert_to_bynary(imagen)

    # Crear el nuevo usuario
    nuevo_usuario = Usuario(
        cedula=cedula,
        nombre=nombre,
        apellido=apellido,
        correo=correo.lower(),
        contrasena=hashed_password,
        rol=rol,
        estado='Activo',
        empresa_id=empresa_id,
        foto=image_bytes if image_bytes else None
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    alert = {"type": "success", "message": "Usuario registrado exitosamente."}
    request.session["alert"] = alert
    return RedirectResponse(url="/register/user", status_code=status.HTTP_303_SEE_OTHER)
# -- END OF THE ROUTE -- #

# -- PATH TO REDIRECT TO USER UPDATE -- #


@app.post("/update/user/path", response_class=HTMLResponse, tags=["update"])
async def update_user(
    request: Request,
    c_user: str = Cookie(None),
    id_usuario: str = Form(...),
    db: Session = Depends(get_database)
):

    if not serverStatus(db):
        alert = {"type": "general",
                 "message": "Error en conexión al servidor, contacte al proveedor del servicio."}
        request.session["alert"] = alert
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    # Validar que el usuario esté logueado
    if not c_user:
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    # Validar que el token sea válido
    token_payload = tokenDecoder(c_user)
    if not token_payload:
        alert = {"type": "general",
                 "message": "Su sesion ha expirado, por favor inicie sesión nuevamente."}
        request.session["alert"] = alert
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    usuario = db.query(Usuario).filter(
        Usuario.id_usuario == id_usuario).first()

    empresa = db.query(Empresa).filter(
        Empresa.id_empresa == usuario.empresa_id).first()

    if not usuario:
        alert = {"type": "general", "message": "El usuario no existe."}
        request.session["alert"] = alert
        return RedirectResponse(url="/home", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse("updateUser.html", {"request": request, "usuario": usuario, "empresa": empresa})
# -- END OF THE ROUTE -- #

# -- PATH TO PROCEED TO THE UPDATE OF A USER -- #


@app.post("/update/user", response_class=HTMLResponse, tags=["update"])
async def update_user(
    request: Request,
    c_user: str = Cookie(None),
    cedula: str = Form(...),
    nombre: str = Form(...),
    apellido: str = Form(...),
    correo: str = Form(...),
    rol: str = Form(...),
    empresa_id: int = Form(...),
    db: Session = Depends(get_database)
):
    if not serverStatus(db):
        alert = {"type": "general",
                 "message": "Error en conexión al servidor, contacte al proveedor del servicio."}
        request.session["alert"] = alert
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    # Validar que el usuario esté logueado
    if not c_user:
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    # Validar que el token sea válido
    token_payload = tokenDecoder(c_user)

    if not token_payload:
        alert = {"type": "general",
                 "message": "Su sesion ha expirado, por favor inicie sesión nuevamente."}
        request.session["alert"] = alert
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    # Obtén el usuario existente
    user = db.query(Usuario).filter(Usuario.cedula == cedula).first()

    if user:
        user.cedula = cedula
        user.nombre = nombre
        user.apellido = apellido
        user.correo = correo.lower()
        user.rol = rol
        user.empresa_id = empresa_id

        db.commit()

        alert = {"type": "success", "message": "Usuario actualizado con éxito"}
        request.session["alert"] = alert
        return RedirectResponse(url="/drivers", status_code=status.HTTP_303_SEE_OTHER)
    else:
        # Manejar el caso donde el usuario no existe
        alert = {"type": "error", "message": "Usuario no encontrado"}
        request.session["alert"] = alert

# ========================================== END OF USERBLOCK ============================================ #

# ========================================== TAXIBLOCK ============================================ #

# -- PATH TO REDIRECT TO TAXI CREATION -- #


@app.get("/register/taxi", response_class=HTMLResponse, tags=["create"])
async def create(request: Request, c_user: str = Cookie(None), db: Session = Depends(get_database)):
    user_id = None
    alert = request.session.pop("alert", None)
    try:
        if not c_user:
            return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

        token_payload = tokenDecoder(c_user)

        user_id = int(token_payload["sub"])

        usuario = db.query(Usuario).filter(
            Usuario.id_usuario == user_id).first()

        if not usuario:
            return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

        empresas = db.query(Empresa).filter(
            Empresa.id_empresa == usuario.empresa_id).all()

        if not empresas:
            return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

        return templates.TemplateResponse("CreateTaxi.html", {"request": request, "empresas": empresas, "alert": alert})
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener información del usuario y empresa: {str(e)}")
# -- END OF THE ROUTE -- #

# -- PATH TO PROCEED TO THE CREATION OF A NEW TAXI -- #
@app.post("/register/taxi", response_class=HTMLResponse)
async def create_taxi(
    request: Request,
    empresa_id: int = Form(...),
    placa: str = Form(...),
    modelo: str = Form(...),
    marca: str = Form(...),
    matricula: str = Form(...),
    tipo_combustible: str = Form(...),
    cuota_diaria: int = Form(...),
    db: Session = Depends(get_database)
):

    if not serverStatus(db):
        alert = {"type": "error",
                 "message": "Error en conexión al servidor, contacte al proveedor del servicio."}
        request.session["alert"] = alert
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    # Validar que la placa no esté vacía
    if not placa:
        alert = {"type": "error", "message": "La placa no puede estar vacía."}
        request.session["alert"] = alert
        return RedirectResponse(url="/register/taxi", status_code=status.HTTP_303_SEE_OTHER)

    # verificar q la placa este bien escrita
    if len(placa) != 6:
        alert = {"type": "error",
                 "message": "La placa debe tener 6 caracteres."}
        request.session["alert"] = alert
        return RedirectResponse(url="/register/taxi", status_code=status.HTTP_303_SEE_OTHER)

    if (verificar_formato(placa) == False):
        alert = {"type": "error",
                 "message": "La placa debe tener el formato AAA000."}
        request.session["alert"] = alert
        return RedirectResponse(url="/register/taxi", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar si la placa ya existe en la base de datos
    if db.query(Taxi).filter(Taxi.placa == placa).first():
        alert = {"type": "error", "message": "La placa ya está registrada."}
        request.session["alert"] = alert
        return RedirectResponse(url="/register/taxi", status_code=status.HTTP_303_SEE_OTHER)

    # Si pasa las validaciones, proceder con la creación del nuevo taxi
    nuevo_taxi = Taxi(
        empresa_id=empresa_id,
        placa=placa.upper(),
        modelo=modelo,
        marca=marca,
        matricula=matricula.upper(),
        tipo_combustible=tipo_combustible,
        cuota_diaria=cuota_diaria
    )

    db.add(nuevo_taxi)
    db.commit()
    db.refresh(nuevo_taxi)
    alert = {"type": "success", "message": "Taxi registrado exitosamente."}
    request.session["alert"] = alert
    return RedirectResponse(url="/register/taxi", status_code=status.HTTP_303_SEE_OTHER)
# -- END OF THE ROUTE -- #

# -- PATH TO REDIRECT TO TAXI VIEW -- #
@app.get("/taxis", tags=["routes"])
async def taxis(request: Request, c_user: str = Cookie(None), db: Session = Depends(get_database)):
    return RedirectResponse(url="/view/taxi", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/view/taxi", response_class=HTMLResponse, tags=["routes"])
async def view_taxi(request: Request, 
                    c_user: str = Cookie(None), 
                    db: Session = Depends(get_database), 
                    page: int = 1,
                    taxi_page: int = 8 ):
    user_id = None

    if not c_user: 
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    token_payload = tokenDecoder(c_user)

    user_id = int(token_payload["sub"])
    if page < 1:
        page = 1

    if taxi_page < 1:
        taxi_page = 8

    usuario = db.query(Usuario).filter(
        Usuario.id_usuario == user_id).first()

    if not usuario:
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)
    
    taxis_paginados=obtener_taxis_paginados(db, page, taxi_page, usuario.empresa_id)
    taxis = taxis_paginados["taxis"]
    total_paginas = taxis_paginados["total_paginas"]
    visible_pages = 10

    start_page = max(1, page - (visible_pages // 2))
    end_page = min(total_paginas, start_page + visible_pages - 1)

    

    alert = request.session.pop("alert", None)

    if not taxis:
        print("no hay taxis")
        return templates.TemplateResponse("viewTaxi.html", {"request": request, "taxis": [], "alert": alert, "no_taxis_message": "No hay taxis disponibles."})

    return templates.TemplateResponse("viewTaxi.html", {"request": request, "taxis": taxis, "alert": alert,"page":page,"taxi_page":taxi_page,"start_page":start_page,"end_page":end_page,"total_paginas":total_paginas})
# -- END OF THE ROUTE -- #

# -- PATH TO REDIRECT TO TAXI UPDATE -- #
@app.post("/update/taxi/path", response_class=HTMLResponse, tags=["update"])
async def update_taxi(
    request: Request,
    c_user: str = Cookie(None),
    id_taxi: str = Form(...),
    db: Session = Depends(get_database)
):

    if not serverStatus(db):
        alert = {"type": "general",
                 "message": "Error en conexión al servidor, contacte al proveedor del servicio."}
        request.session["alert"] = alert
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    # Validar que el usuario esté logueado
    if not c_user:
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    # Validar que el token sea válido
    token_payload = tokenDecoder(c_user)
    if not token_payload:
        alert = {"type": "general",
                 "message": "Su sesion ha expirado, por favor inicie sesión nuevamente."}
        request.session["alert"] = alert
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    taxi = db.query(Taxi).filter(Taxi.id_taxi == id_taxi).first()

    empresa = db.query(Empresa).filter(
        Empresa.id_empresa == taxi.empresa_id).first()

    if not taxi:
        alert = {"type": "error", "message": "El taxi no existe."}
        request.session["alert"] = alert
        return RedirectResponse(url="/view/taxi", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse("updateTaxi.html", {"request": request, "taxi": taxi, "empresa": empresa})
# -- END OF THE ROUTE -- #

# -- PATH TO PROCEED TO THE UPDATE OF A TAXI -- #
@app.post("/update/taxi", response_class=HTMLResponse, tags=["update"])
async def update_taxi(
    request: Request,
    c_user: str = Cookie(None),
    placa: str = Form(...),
    modelo: str = Form(...),
    marca: str = Form(...),
    matricula: str = Form(...),
    tipo_combustible: str = Form(...),
    cuota_diaria: int = Form(...),
    db: Session = Depends(get_database)
):
    if not serverStatus(db):
        alert = {"type": "general",
                 "message": "Error en conexión al servidor, contacte al proveedor del servicio."}
        request.session["alert"] = alert
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    # Validar que el usuario esté logueado
    if not c_user:
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    # Validar que el token sea válido
    token_payload = tokenDecoder(c_user)

    if not token_payload:
        alert = {"type": "general",
                 "message": "Su sesion ha expirado, por favor inicie sesión nuevamente."}
        request.session["alert"] = alert
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    # Obtén el taxi existente
    taxi = db.query(Taxi).filter(Taxi.placa == placa).first()

    if taxi:
        taxi.placa = placa
        taxi.modelo = modelo
        taxi.marca = marca
        taxi.matricula = matricula
        taxi.tipo_combustible = tipo_combustible
        taxi.cuota_diaria = cuota_diaria

        db.commit()

        alert = {"type": "success", "message": "Taxi actualizado con éxito"}
        request.session["alert"] = alert
        return RedirectResponse(url="/view/taxi", status_code=status.HTTP_303_SEE_OTHER)
    else:
        # Manejar el caso donde el taxi no existe
        alert = {"type": "error", "message": "Taxi no encontrado"}
        request.session["alert"] = alert
        return RedirectResponse(url="/view/taxi", status_code=status.HTTP_303_SEE_OTHER)
# -- END OF THE ROUTE -- #
# ========================================== END OF TAXIBLOCK ============================================ #

# ========================================== assignmentBLOCK ============================================ #

# -- PATH TO REDIRECT TO assignment CREATION -- #
@app.get("/register/assignment", response_class=HTMLResponse, tags=["create"])
async def create(request: Request, c_user: str = Cookie(None), db: Session = Depends(get_database)):
    user_id = None

    if not c_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    token_payload = tokenDecoder(c_user)

    user_id = int(token_payload["sub"])

    usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()

    if not usuario:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    driversNotAssigned = db.query(Usuario).filter(Usuario.rol == "Conductor", Usuario.empresa_id == usuario.empresa_id).filter(
        ~Usuario.id_usuario.in_(db.query(ConductorActual.id_conductor))).all()
    taxisNotAssigned = db.query(Taxi).filter(Taxi.empresa_id == usuario.empresa_id).filter(
        ~Taxi.id_taxi.in_(db.query(ConductorActual.id_taxi))).all()

    alert = request.session.pop("alert", None)
    return templates.TemplateResponse("registerAssignment.html", {"request": request, "conductores": driversNotAssigned, "taxis": taxisNotAssigned, "alert": alert})
# -- END OF THE ROUTE -- #

# -- PATH TO PROCEED TO THE CREATION OF A NEW assignment -- #
@app.post("/register/assignment", response_class=HTMLResponse)
async def create_assignment(
    request: Request,
    id_conductor: int = Form(...),
    id_taxi: int = Form(...),
    db: Session = Depends(get_database)
):
    if not serverStatus(db):
        alert = {"type": "general",
                 "message": "Error en conexión al servidor, contacte al proveedor del servicio."}
        request.session["alert"] = alert
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar si el conductor ya está asignado a un taxi
    if db.query(ConductorActual).filter(ConductorActual.id_conductor == id_conductor).first():
        alert = {"type": "error",
                 "message": "El conductor ya está asignado a un taxi."}
        request.session["alert"] = alert
        return RedirectResponse(url="/register/assignment", status_code=status.HTTP_303_SEE_OTHER)

    # Si pasa las validaciones, proceder con la creación de la asignación
    nueva_asignacion = ConductorActual(
        id_conductor=id_conductor,
        id_taxi=id_taxi
    )

    db.add(nueva_asignacion)
    db.commit()
    db.refresh(nueva_asignacion)
    alert = {"type": "success", "message": "Asignación registrada exitosamente."}
    request.session["alert"] = alert

    return RedirectResponse(url="/register/assignment", status_code=status.HTTP_303_SEE_OTHER)
# -- END OF THE ROUTE -- #

# ========================================== END OF assignmentBLOCK ============================================ #


# -- MODULO 2-- #
@app.get("/register/daily", response_class=HTMLResponse, tags=["routes"])
async def registro_diario_view(request: Request, c_user: str = Cookie(None), db: Session = Depends(get_database)):
    user_id = None

    try:
        if not serverStatus(db):
            alert = {"type": "general",
                     "message": "Error en conexión al servidor, contacte al proveedor del servicio."}
            request.session["alert"] = alert
            return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

        if not c_user:
            alert = {"type": "general",
                     "message": "Su sesion ha expirado, por favor inicie sesión nuevamente."}
            request.session["alert"] = alert
            return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

        token_payload = tokenDecoder(c_user)

        if not token_payload:
            alert = {"type": "general",
                     "message": "Su sesion ha expirado, por favor inicie sesión nuevamente."}
            request.session["alert"] = alert
            return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

        user_id = int(token_payload["sub"])
        usuario = db.query(Usuario).filter(
            Usuario.id_usuario == user_id).first()
        if not usuario:
            raise HTTPException(
                status_code=401, detail="Usuario no encontrado.")

        empresas = db.query(Empresa).filter(
            Empresa.id_empresa == usuario.empresa_id).first()
        if not empresas:
            alert = {"type": "error",
                     "message": "Error al obtener información de la empresa."}
            request.session["alert"] = alert
            return RedirectResponse(url="/register/daily", status_code=status.HTTP_303_SEE_OTHER)

        conductores = db.query(Usuario).filter(Usuario.rol == "Conductor", Usuario.empresa_id == usuario.empresa_id).filter(
            Usuario.id_usuario.in_(db.query(ConductorActual.id_conductor))).all()
        taxisAssigned = db.query(Taxi).filter(Taxi.empresa_id == usuario.empresa_id).filter(
            Taxi.id_taxi.in_(db.query(ConductorActual.id_taxi))).all()

        # Recuperar la alerta de la sesión
        alert = request.session.pop("alert", None)
        return templates.TemplateResponse("register_daily.html", {"request": request, "alert": alert, "conductores": conductores, "taxis": taxisAssigned})
    except HTTPException as e:
        alert = {"type": "general", "message": str(e.detail)}
        request.session["alert"] = alert
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    except Exception as e:
        alert = {"type": "general",
                 "message": "Error de servidor. Inténtelo nuevamente más tarde."}
        request.session["alert"] = alert
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)
# -- MODULO 2 actualizar registro diario-- #

@app.post("/register/daily", tags=["payments"])
async def registro_diario(
    request: Request,
    id_conductor: int = Form(...),
    valor: int = Form(...),
    db: Session = Depends(get_database),
):
    if not serverStatus(db):
        alert = {"type": "general",
                 "message": "Error en conexión al servidor, contacte al proveedor del servicio."}
        request.session["alert"] = alert
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    if valor < 0:
        alert = {"type": "error", "message": "El valor no puede ser negativo."}
        request.session["alert"] = alert
        return RedirectResponse(url="/register/daily", status_code=status.HTTP_303_SEE_OTHER)
    
    datos_conductor = getDriverData(id_conductor, db)

    if not datos_conductor:
        alert = {"type": "error",
                 "message": "El conductor no tiene un taxi asignado."}
        # Almacena la alerta en la sesión
        request.session["alert"] = alert
        return RedirectResponse(url="/register/daily", status_code=status.HTTP_303_SEE_OTHER)

    cuota_diaria_taxi = datos_conductor["cuota_diaria_taxi"]

    fecha_actual = date.today()
    pago_existente = db.query(Pago).filter(
        Pago.id_conductor == id_conductor,
        Pago.fecha == fecha_actual,
        Pago.cuota_diaria_registrada == True
    ).first()
    if pago_existente:
        alert = {"type": "error",
                 "message": "Este conductor ya tiene un pago registrado para el día de hoy."}
        request.session["alert"] = alert
        return RedirectResponse(url="/register/daily", status_code=status.HTTP_303_SEE_OTHER)
    else:
        estado = valor >= cuota_diaria_taxi

        nuevo_pago = Pago(
            id_conductor=id_conductor,
            fecha=fecha_actual,
            valor=valor,
            estado=estado,
            cuota_diaria_registrada=True
        )

        db.add(nuevo_pago)
        db.commit()
        
        conductor = db.query(Usuario).filter(Usuario.id_usuario == id_conductor).first()
        mes_actual = date.today().month
        ano_actual = date.today().year

        
        reporte_existente = db.query(Reporte).filter(
            Reporte.empresa_id == conductor.empresa_id,
            extract('month', Reporte.fecha) == mes_actual,
            extract('year', Reporte.fecha) == ano_actual
            
        ).first()

        if reporte_existente:
            reporte_existente.ingresos += valor
            db.commit()

        db.refresh(nuevo_pago)
        alert = {"type": "success", "message": "Pago registrado exitosamente."}
        # Almacena la alerta en la sesión
        request.session["alert"] = alert

    # Redirige a la vista de registro diario
    return RedirectResponse(url="/register/daily", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/update/daily", response_class=HTMLResponse, tags=["routes"])
async def actualizar_cuota_diaria_view(request: Request, c_user: str = Cookie(None), db: Session = Depends(get_database)):
    user_id = None

    try:
        if not serverStatus(db):
            alert = {"type": "general",
                     "message": "Error en conexión al servidor, contacte al proveedor del servicio."}
            request.session["alert"] = alert
            return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

        if not c_user:
            alert = {"type": "general",
                     "message": "Su sesión ha expirado, por favor inicie sesión nuevamente."}
            request.session["alert"] = alert
            return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

        token_payload = tokenDecoder(c_user)

        if not token_payload:
            alert = {"type": "general",
                     "message": "Su sesión ha expirado, por favor inicie sesión nuevamente."}
            request.session["alert"] = alert
            return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

        user_id = int(token_payload["sub"])
        usuario = db.query(Usuario).filter(
            Usuario.id_usuario == user_id).first()
        if not usuario:
            alert = {"type": "error",
                     "message": "Usuario no encontrado."}
            request.session["alert"] = alert
            return RedirectResponse(url="/update/daily", status_code=status.HTTP_303_SEE_OTHER)

        empresas = db.query(Empresa, Empresa.nombre).filter(
            Empresa.id_empresa == usuario.empresa_id).first()
        if not empresas:
            alert = {"type": "error",
                     "message": "Error al obtener información de la empresa."}
            request.session["alert"] = alert
            return RedirectResponse(url="/update/daily", status_code=status.HTTP_303_SEE_OTHER)

        # Filtrar conductores por la empresa del usuario
        conductores = db.query(Usuario).filter(Usuario.rol == "Conductor", Usuario.empresa_id == usuario.empresa_id).filter(
            Usuario.id_usuario.in_(db.query(ConductorActual.id_conductor))).all()
        taxisAssigned = db.query(Taxi).filter(Taxi.empresa_id == usuario.empresa_id).filter(
            Taxi.id_taxi.in_(db.query(ConductorActual.id_taxi))).all()

        # Obtener fechas registradas para el conductor seleccionado
        id_conductor_default = conductores[0].id_usuario if conductores else None
        fechas_registradas = obtener_fechas_registradas(
            id_conductor_default, db)

        # Recuperar la alerta de la sesión
        alert = request.session.pop("alert", None)

        return templates.TemplateResponse("registerDailyUpdate.html", {"request": request, "alert": alert, "conductores": conductores, "fechas_registradas": fechas_registradas, "empresas": empresas, "taxis": taxisAssigned})

    except HTTPException as e:
        alert = {"type": "general", "message": str(e.detail)}
        request.session["alert"] = alert
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    except Exception as e:
        alert = {"type": "general",
                 "message": "Error de servidor. Inténtelo nuevamente más tarde."}
        request.session["alert"] = alert
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/update/daily", tags=["payments"])
async def actualizar_cuota_diaria(
    request: Request,
    id_conductor: int = Form(...),
    nueva_cuota: int = Form(...),
    fecha_seleccionada: str = Form(...),
    db: Session = Depends(get_database),
):
    try:
        if not serverStatus(db):
            alert = {"type": "general",
                     "message": "Error en conexión al servidor, contacte al proveedor del servicio."}
            request.session["alert"] = alert
            return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

        datos_conductor = getDriverData(id_conductor, db)

        if not datos_conductor:
            alert = {"type": "error",
                     "message": "El conductor no existe."}
            # Almacena la alerta en la sesión
            request.session["alert"] = alert
            return RedirectResponse(url="/update/daily", status_code=status.HTTP_303_SEE_OTHER)

        # fecha seleccionada esté registrada
        fecha_seleccionada_dt = datetime.strptime(
            fecha_seleccionada, "%Y-%m-%d").date()

        # filtrar si ya hay un pago registrado para la fecha seleccionada
        pago_existente = db.query(Pago).filter(
            Pago.id_conductor == id_conductor,
            Pago.fecha == fecha_seleccionada_dt,
            Pago.cuota_diaria_registrada == True
        ).first()

        if not pago_existente:
            alert = {"type": "error",
                     "message": "No se encontró un pago registrado para la fecha seleccionada."}
            # Almacena la alerta en la sesión
            request.session["alert"] = alert
            return RedirectResponse(url="/update/daily", status_code=status.HTTP_303_SEE_OTHER)
        
        if nueva_cuota < pago_existente.valor:
            alert = {"type": "error",
                     "message": "El valor no puede ser menor a la cuota registrada."}
            # Almacena la alerta en la sesión
            request.session["alert"] = alert
            return RedirectResponse(url="/update/daily", status_code=status.HTTP_303_SEE_OTHER)

        # Actualizar la cuota diaria para la fecha seleccionada
        pago_antiguo=pago_existente.valor
        pago_existente.valor = nueva_cuota
        pago_existente.estado = nueva_cuota >= datos_conductor["cuota_diaria_taxi"]
        db.commit()

        conductor = db.query(Usuario).filter(Usuario.id_usuario == id_conductor).first()
        mes_actual = date.today().month
        ano_actual = date.today().year

        
        reporte_existente = db.query(Reporte).filter(
            Reporte.empresa_id == conductor.empresa_id,
            extract('month', Reporte.fecha) == mes_actual,
            extract('year', Reporte.fecha) == ano_actual
            
        ).first()

        if reporte_existente:
            reporte_existente.ingresos +=pago_existente.valor-pago_antiguo
            db.commit()

        alert = {"type": "success",
                 "message": "Cuota diaria actualizada exitosamente."}
        # Almacena la alerta en la sesión
        request.session["alert"] = alert

        # Redirige a la vista de actualización diaria
        return RedirectResponse(url="/update/daily", status_code=status.HTTP_303_SEE_OTHER)

    except HTTPException as e:
        alert = {"type": "general", "message": str(e.detail)}
        request.session["alert"] = alert
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    except Exception as e:
        alert = {"type": "general",
                 "message": "Error de servidor. Inténtelo nuevamente más tarde."}
        request.session["alert"] = alert
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/summary", response_class=HTMLResponse, tags=["routes"])
async def resumen_cuotas_view(
    request: Request,
    c_user: str = Cookie(None),
    id_conductor: int = None,
    fecha_inicio: date = Query(None),
    fecha_fin: date = Query(None),
    db: Session = Depends(get_database)
):
    try:

        if not serverStatus(db):
            alert = {"type": "general",
                     "message": "Error en conexión al servidor, contacte al proveedor del servicio."}
            request.session["alert"] = alert
            return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

        if not c_user:
            alert = {"type": "general",
                     "message": "Su sesión ha expirado, por favor inicie sesión nuevamente."}
            request.session["alert"] = alert
            return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

        token_payload = tokenDecoder(c_user)
        if not token_payload:
            alert = {"type": "general",
                     "message": "Su sesión ha expirado, por favor inicie sesión nuevamente."}
            request.session["alert"] = alert
            return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)
        user_id = int(token_payload["sub"])

        # Obtiene el usuario desde la base de datos
        usuario = db.query(Usuario).filter(
            Usuario.id_usuario == user_id).first()
        if not usuario:
            alert = {"type": "error", "message": "Usuario no encontrado."}
            request.session["alert"] = alert
            return RedirectResponse(url="/summary", status_code=status.HTTP_303_SEE_OTHER)

        # Obtiene la información de la empresa
        empresas = db.query(Empresa, Empresa.nombre).filter(
            Empresa.id_empresa == usuario.empresa_id).first()
        if not empresas:
            alert = {"type": "error",
                     "message": "Error al obtener información de la empresa."}
            request.session["alert"] = alert
            return RedirectResponse(url="/summary", status_code=status.HTTP_303_SEE_OTHER)

        # Filtra conductores por la empresa del usuario
        conductores = db.query(Usuario).filter(
            Usuario.rol == "Conductor", Usuario.empresa_id == usuario.empresa_id).all()

        # Recupera la alerta de la sesión
        alert = request.session.pop("alert", None)

        cuotas_diarias = []
        conductor = None

        # Verifica si se proporcionó un ID de conductor y si existe
        if id_conductor is not None:
            datos_conductor = getDriverData(id_conductor, db)
            print("Datos del conductor:", datos_conductor)
            if datos_conductor:
                # Si se proporcionan fechas, filtra por rango de fechas
                if fecha_inicio and fecha_fin:
                    fecha_inicio = datetime.combine(
                        fecha_inicio, datetime.min.time())
                    fecha_fin = datetime.combine(
                        fecha_fin, datetime.max.time())
                    cuotas_diarias = db.query(Pago).filter(
                        Pago.id_conductor == id_conductor,
                        Pago.fecha.between(fecha_inicio, fecha_fin)
                    ).all()
                    print("Cuotas diarias dentro del rango:", cuotas_diarias)
                else:
                    # Sin fechas, obtén todos los pagos para el conductor
                    cuotas_diarias = db.query(Pago).filter(
                        Pago.id_conductor == id_conductor).all()
                    print("Todas las cuotas diarias:", cuotas_diarias)
                # Obtiene la información del conductor
                conductor = db.query(Usuario).filter(
                    Usuario.id_usuario == id_conductor).first()

        # Renderiza el template con los resultados
        return templates.TemplateResponse("summary.html", {
            "request": request,
            "alert": alert,
            "conductores": conductores,
            "empresas": empresas,
            "id_conductor_selected": id_conductor,
            "cuotas_diarias": cuotas_diarias,
            "conductor": conductor,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin
        })

    except HTTPException as e:
        alert = {"type": "general", "message": str(e.detail)}
        request.session["alert"] = alert
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    except Exception as e:
        alert = {"type": "general",
                 "message": "Error de servidor. Inténtelo nuevamente más tarde."}
        request.session["alert"] = alert
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/summary", response_class=HTMLResponse, tags=["routes"])
async def resumen_cuotas_post(request: Request, id_conductor: int = Form(...), fecha_inicio: date = Form(None), fecha_fin: date = Form(None), db: Session = Depends(get_database)):
    try:

        if not serverStatus(db):
            alert = {"type": "general",
                     "message": "Error en conexión al servidor, contacte al proveedor del servicio."}
            request.session["alert"] = alert
            return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

        c_user = request.cookies.get("c_user")
        if not c_user:
            alert = {"type": "general",
                     "message": "Su sesión ha expirado, por favor inicie sesión nuevamente."}
            request.session["alert"] = alert
            return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

        token_payload = tokenDecoder(c_user)
        if not token_payload:
            alert = {"type": "general",
                     "message": "Su sesión ha expirado, por favor inicie sesión nuevamente."}
            request.session["alert"] = alert
            return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)
        user_id = int(token_payload["sub"])

        usuario = db.query(Usuario).filter(
            Usuario.id_usuario == user_id).first()
        if not usuario:
            alert = {"type": "error", "message": "Usuario no encontrado."}
            request.session["alert"] = alert
            return RedirectResponse(url="/summary", status_code=status.HTTP_303_SEE_OTHER)

        empresas = db.query(Empresa, Empresa.nombre).filter(
            Empresa.id_empresa == usuario.empresa_id).first()
        if not empresas:
            alert = {"type": "error",
                     "message": "Error al obtener información de la empresa."}
            request.session["alert"] = alert
            return RedirectResponse(url="/summary", status_code=status.HTTP_303_SEE_OTHER)

        conductores = db.query(Usuario).filter(
            Usuario.rol == "Conductor", Usuario.empresa_id == usuario.empresa_id).all()

        alert = request.session.pop("alert", None)

        cuotas_diarias = []
        conductor = None

        if id_conductor is not None:
            datos_conductor = getDriverData(id_conductor, db)
            print("Datos del conductor:", datos_conductor)
            if datos_conductor:
                # Si se proporcionan fechas, filtra por rango de fechas
                if fecha_inicio and fecha_fin:
                    fecha_inicio = datetime.combine(
                        fecha_inicio, datetime.min.time())
                    fecha_fin = datetime.combine(
                        fecha_fin, datetime.max.time())
                    cuotas_diarias = db.query(Pago).filter(
                        Pago.id_conductor == id_conductor,
                        Pago.fecha.between(fecha_inicio, fecha_fin)
                    ).all()
                    print("Cuotas diarias dentro del rango:", cuotas_diarias)
                else:
                    # Sin fechas, obtén todos los pagos para el conductor
                    cuotas_diarias = db.query(Pago).filter(
                        Pago.id_conductor == id_conductor).all()
                    print("Todas las cuotas diarias:", cuotas_diarias)
                # Obtiene la información del conductor
                conductor = db.query(Usuario).filter(
                    Usuario.id_usuario == id_conductor).first()

        if not cuotas_diarias:
            alert = {
                "type": "error", 
                "message": "No se encontraron resultados para la búsqueda del conductor " + conductor.nombre + " " + conductor.apellido + "en la fecha inicio {0} y fecha fin {1}".format(fecha_inicio, fecha_fin)}
            request.session["alert"] = alert

        return templates.TemplateResponse("summary.html", {
            "request": request,
            "alert": alert,
            "conductores": conductores,
            "empresas": empresas,
            "id_conductor_selected": id_conductor,
            "cuotas_diarias": cuotas_diarias,
            "conductor": conductor,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin
        })

    except HTTPException as e:
        alert = {"type": "general", "message": str(e.detail)}
        request.session["alert"] = alert
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    except Exception as e:
        alert = {"type": "general",
                 "message": "Error de servidor. Inténtelo nuevamente más tarde."}
        request.session["alert"] = alert
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/drivers", response_class=HTMLResponse, tags=["routes"])
async def drivers(request: Request,
                    c_user: str = Cookie(None),
                    db: Session = Depends(get_database),
                    page: int = 1,
                    per_page: int = 8
                    ):
    alert = request.session.pop("alert", None)
    if not c_user:
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    checkTokenStatus = userStatus(c_user, request)
    if not checkTokenStatus["status"]:
        return checkTokenStatus["redirect"]

    if not serverStatus(db):
        alert = {"type": "general",
                "message": "Error en conexión al servidor, contacte al proveedor del servicio."}
        request.session["alert"] = alert
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    UUID = checkTokenStatus["userid"]
    userData = db.query(Usuario).filter(Usuario.id_usuario == UUID).first()
    if not userData:
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    usuario = db.query(Usuario).filter(
        Usuario.id_usuario == UUID).first()

    if per_page < 1:
        per_page = 4

    if page < 1:
        page = 1

    resultado_paginado = obtener_usuarios_paginados(
        db=db,
        page=page,
        per_page=per_page,
        empresa_id=usuario.empresa_id,
        rol="Conductor"
    )

    conductores = resultado_paginado["usuarios"]
    total_paginas = resultado_paginado["total_paginas"]

    for conductor in conductores:
        if conductor.foto:
            conductor.foto = convertIMG(conductor.foto)

    visible_pages = 10


    
    start_page = max(1, page - (visible_pages // 2))
    end_page = min(total_paginas, start_page + visible_pages - 1)

    return templates.TemplateResponse("./Reports/drivers.html", {"request": request, "usuarios": conductores, "alert": alert, "total_paginas": total_paginas, "page": page, "per_page": per_page , "start_page": start_page, "end_page": end_page})

@app.post("/reports/driver/{name}", response_class=HTMLResponse, tags=["routes"])
async def reports(request: Request, id_usuario: int = Form(...), db: Session = Depends(get_database)):
    #mes actual 
    now = datetime.now()
    current_month = now.strftime("%B")
    current_month = MONTHS_IN_SPANISH[current_month]
    # Obtener la fecha actual
    today = date.today()
    
    first_day_of_month = datetime(today.year, today.month, 1)
    last_day_of_month = datetime(today.year, today.month + 1, 1) - timedelta(days=1)
    
        
    #  total acumulado del mes
    total_acumulado = (
        db.query(func.sum(Pago.valor))
        .filter(Pago.id_conductor == id_usuario)
        .filter(Pago.fecha.between(first_day_of_month, last_day_of_month))
        .scalar() or 0  
    )
    print("Total acumulado: ", total_acumulado)        
    first_day_of_last_month = datetime(today.year, today.month - 1, 1) if today.month > 1 else datetime(today.year - 1, 12, 1)    
    last_day_of_last_month = first_day_of_month - timedelta(days=1)
    
    total_mes_anterior = (
        db.query(func.sum(Pago.valor))
        .filter(Pago.id_conductor == id_usuario)
        .filter(Pago.fecha.between(first_day_of_last_month, last_day_of_last_month))
        .scalar() or 0
    )
    print("Total mes anteior: ", total_mes_anterior)
    
    
    first_day_of_week = today - timedelta(days=today.weekday())
    last_day_of_week = first_day_of_week + timedelta(days=6)

    # Obtener los pagos de la semana actual
    weekly_reports = db.query(Pago).filter(
        Pago.id_conductor == id_usuario,
        Pago.fecha.between(first_day_of_week, last_day_of_week)
    ).all()

    reports_week_data = {str(report.fecha): report.valor for report in weekly_reports}
    # Crear una lista ordenada de los pagos diarios para los últimos 7 días
    last_seven_days = [(last_day_of_week - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]

    # Obtener los pagos diarios para los últimos 7 días
    daily_reports_data = {day: reports_week_data.get(day, 0) for day in last_seven_days}


    reports = db.query(Pago).filter(Pago.id_conductor == id_usuario).all()
    conductor = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    taxi_actual = (db.query(Taxi).join(ConductorActual, ConductorActual.id_taxi == Taxi.id_taxi).filter(ConductorActual.id_conductor == id_usuario).first())
    empresas = db.query(Empresa, Empresa.nombre).filter(Empresa.id_empresa == Usuario.empresa_id).first()
    usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    return templates.TemplateResponse("./Reports/dailyreports.html", {"request": request, "reports": reports, "conductor": conductor,"taxi_actual": taxi_actual, "total_acumulado": total_acumulado, "today": today, "current_month": current_month, "empresas": empresas,"weekly_reports": daily_reports_data, "total_mes_anterior": total_mes_anterior, "usuario": usuario})
    
@app.post("/drivers", response_class=HTMLResponse, tags=["routes"])
async def search(request: Request, search: Optional[str] = Form(None), db: Session = Depends(get_database)):
    conductores = None
    if not search:
        conductores = db.query(Usuario).filter(
            Usuario.rol == 'Conductor').all()
    else:
        conductores = db.query(Usuario).filter(
            Usuario.rol == 'Conductor',
            or_(
                Usuario.nombre == search,
                Usuario.correo == search,
                Usuario.cedula == search
            )
        ).all()
        for conductor in conductores:
            if conductor.foto:
                conductor.foto = convertIMG(conductor.foto)

        if not conductores:
            alert = {"type": "error",
                     "message": "No se encontraron resultados."}
            request.session["alert"] = alert
            return RedirectResponse(url="/drivers", status_code=status.HTTP_303_SEE_OTHER)
        
    
    return templates.TemplateResponse("./Reports/drivers.html", {"request": request, "usuarios": conductores})

@app.get("/renew/token", tags=["auth"])
async def renew_token(request: Request, c_user: str = Cookie(None)):
    if not c_user:
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    token_payload = tokenDecoder(c_user)

    if not token_payload:
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    response = RedirectResponse(
        url="/home",
        status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="c_user",
        value=tokenConstructor(token_payload["sub"]))

    return response

@app.get("/pruebas", response_class=HTMLResponse, tags=["routes"])
async def pruebas(request: Request, c_user: str = Cookie(None), db: Session = Depends(get_database)):
    if not c_user:
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    token_payload = tokenDecoder(c_user)

    if not token_payload:
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)
    alert = {"type": "error", "message": "si funca."}

    return templates.TemplateResponse("./pr.html", {"request": request, "alert": alert})

@app.get("/404-NotFound", response_class=HTMLResponse, tags=["routes"])
async def not_found(request: Request, c_user: str = Cookie(None)):
    if not c_user:
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("./error404.html", {"request": request})

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return RedirectResponse(url="/404-NotFound", status_code=status.HTTP_303_SEE_OTHER)


# ========================================== MAINTENANCEBLOCK ============================================ #

# -- PATH TO REDIRECT TO maintenance CREATION -- #
@app.get("/maintenance", response_class=HTMLResponse, tags=["routes"])
async def maintenance(request: Request, c_user: str = Cookie(None), db: Session = Depends(get_database)):
    if not c_user:
            alert = {"type": "general",
                        "message": "Su sesión ha expirado, por favor inicie sesión nuevamente."}
            request.session["alert"] = alert
            return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    token_payload = tokenDecoder(c_user)
    user_id = int(token_payload["sub"])

    usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()

    if not usuario:
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    empresa = db.query(Empresa).filter(Empresa.id_empresa == usuario.empresa_id).first()

    if not empresa:
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    # Consulta para obtener todos los taxis asociados a la empresa
    taxis = db.query(Taxi).filter(Taxi.empresa_id == empresa.id_empresa).all()

    alert = request.session.pop("alert", None)
    return templates.TemplateResponse(
        "maintenance.html", {"request": request, "alert": alert, "empresa": empresa, "taxis": taxis}
    )
# -- END OF THE ROUTE -- #

# -- PATH TO PROCEED TO THE CREATION OF A NEW maintenance -- #
@app.post("/maintenance", response_class=HTMLResponse, tags=["routes"])
async def maintenance(
    request: Request,
    c_user: str = Cookie(None),
    placa: str = Form(...),
    fecha: str = Form(...),
    descripcion: str = Form(...),
    costo: int = Form(...),
    db: Session = Depends(get_database)
):
    if not serverStatus(db):
            alert = {"type": "general",
                        "message": "Error en conexión al servidor, contacte al proveedor del servicio."}
            request.session["alert"] = alert
            return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    c_user = request.cookies.get("c_user")

    if not c_user:
        alert = {"type": "general",
                    "message": "Su sesión ha expirado, por favor inicie sesión nuevamente."}
        request.session["alert"] = alert
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    token_payload = tokenDecoder(c_user)
    if not token_payload:
        alert = {"type": "general",
                    "message": "Su sesión ha expirado, por favor inicie sesión nuevamente."}
        request.session["alert"] = alert
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)
    

    print(" ============================================ Placa:", placa)

    # Obtener el taxi por placa
    taxi = db.query(Taxi).filter(Taxi.placa == placa).first()

    # Verificar si se encontró el taxi
    if not taxi:
        alert = {"type": "error", "message": "No se encontró ningún taxi con la placa proporcionada."}
        request.session["alert"] = alert
        return RedirectResponse(url="/maintenance", status_code=status.HTTP_303_SEE_OTHER)

    if costo <= 0:
        alert = {"type": "error", "message": "El costo del mantenimiento debe ser mayor a 0."}
        request.session["alert"] = alert
        return RedirectResponse(url="/maintenance", status_code=status.HTTP_303_SEE_OTHER)

    # Continuar con el registro del mantenimiento
    nuevo_mantenimiento = Mantenimiento(
        id_taxi=taxi.id_taxi,
        fecha=fecha,
        descripcion=descripcion,
        costo=costo
    )

    db.add(nuevo_mantenimiento)
    db.commit()
    
    
    mes_actual = date.today().month
    ano_actual = date.today().year

    
    reporte_existente = db.query(Reporte).filter(
        Reporte.empresa_id == taxi.empresa_id,
        extract('month', Reporte.fecha) == mes_actual,
        extract('year', Reporte.fecha) == ano_actual
        
    ).first()

    if reporte_existente:
        reporte_existente.gastos += costo
        db.commit()
    db.refresh(nuevo_mantenimiento)
    alert = {"type": "success", "message": "Mantenimiento registrado exitosamente."}
    request.session["alert"] = alert

    return RedirectResponse(url="/maintenance", status_code=status.HTTP_303_SEE_OTHER)
# -- END OF THE ROUTE -- #

# ========================================== END OF MAINTENANCEBLOCK ============================================ #

# ========================================== REPORTSTAXIBLOCK ============================================ #

# -- PATH TO REDIRECT TO REPORTSTAXI -- #
@app.post("/view/detail/taxi", response_class=HTMLResponse, tags=["routes"])
async def detail_taxi(
    request: Request,
    c_user: str = Cookie(None),
    id_taxi: str = Form(...),
    db: Session = Depends(get_database)
):

    print(" ============================================ id_taxi:", id_taxi)
    print(" ============================================ c_user:", c_user)

    if not serverStatus(db):
        alert = {"type": "general",
                "message": "Error en conexión al servidor, contacte al proveedor del servicio."}
        request.session["alert"] = alert
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    # Validar que el usuario esté logueado
    if not c_user:
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    # Validar que el token sea válido
    token_payload = tokenDecoder(c_user)
    if not token_payload:
        alert = {"type": "general",
                "message": "Su sesion ha expirado, por favor inicie sesión nuevamente."}
        request.session["alert"] = alert
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)
    
    conductorActual = db.query(ConductorActual).filter(ConductorActual.id_taxi == id_taxi).first()

    if not conductorActual:
        alert = {"type": "error",
                "message": "No se encontró ningún conductor asignado a este taxi."}
        request.session["alert"] = alert
        return RedirectResponse(url="/view/taxi", status_code=status.HTTP_303_SEE_OTHER)

    # obtener los pagos que ha hecho el conductor
    pagos = db.query(Pago).filter(Pago.id_conductor == conductorActual.id_conductor).all()

    # obtener los mantenimientos que ha hecho el taxi
    mantenimientos = db.query(Mantenimiento).filter(Mantenimiento.id_taxi == id_taxi).all()

    #obtener informacion del conductor
    conductor = db.query(Usuario).filter(Usuario.id_usuario == conductorActual.id_conductor).first()

    #obtener informacion del taxi
    taxi = db.query(Taxi).filter(Taxi.id_taxi == id_taxi).first()

    print ("============================================ conductor:", conductorActual.id_conductor)

    # obtener la sumatoria de los pagos
    total_pagos = db.query(func.sum(Pago.valor)).filter(Pago.id_conductor == conductorActual.id_conductor).scalar()

    # Obtener la sumatoria de todos los mantenimientos
    total_mantenimientos = db.query(func.sum(Mantenimiento.costo)).filter(Mantenimiento.id_taxi == id_taxi).scalar()

    if not total_pagos:
        total_pagos = 0

    if not total_mantenimientos:
        total_mantenimientos = 0
    
    return templates.TemplateResponse(
        "detailTaxi.html",
        {"request": request, "pagos": pagos, "mantenimientos": mantenimientos, "conductor": conductor, "taxi": taxi, "total_pagos": total_pagos, "total_mantenimientos": total_mantenimientos}
    )
# -- END OF THE ROUTE -- # 





