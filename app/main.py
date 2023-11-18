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
import bcrypt
import os
from dotenv import load_dotenv
from datetime import date

from functions import *
from models import *

from database import get_database
from starlette.middleware.sessions import SessionMiddleware

from starlette.exceptions import HTTPException as StarletteHTTPException

load_dotenv()
MIDDLEWARE_KEY = os.environ.get("MIDDLEWARE_KEY")

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=MIDDLEWARE_KEY)
app.mount("/static", StaticFiles(directory="public/dist"), name="static")
templates = Jinja2Templates(directory="public/templates")
templatesReports = Jinja2Templates(directory="public/templates/Reports")


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

    welcome = {"name": userData.nombre, "message": ""}
    alert = request.session.pop("alert", None)
    return templates.TemplateResponse("./index.html", {"request": request, "alert": alert, "welcome": welcome})


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

    empresa = db.query(Empresa).filter(
        Empresa.id_empresa == usuario.empresa_id).first()
    error_message = None
    cedula_existente = db.query(Usuario).filter(
        Usuario.cedula == cedula).first()
    if cedula_existente:
        error_message = "La cédula ya está en uso."

    correo_existente = db.query(Usuario).filter(
        Usuario.correo == correo).first()
    if correo_existente:
        error_message = "El correo ya está en uso."

    if error_message:
        return templates.TemplateResponse("CreateUser.html", {"request": request, "error_message": error_message, "empresa": empresa, "usuario": usuario})

    # Encriptar la contraseña solo si se proporciona una
    hashed_password = None
    if contrasena and rol != "Conductor":
        hashed_password = bcrypt.hashpw(
            contrasena.encode('utf-8'), bcrypt.gensalt())

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
    alert = {"type": "success", "message": "Usuario registrado exitosamente."}
    request.session["alert"] = alert
    return RedirectResponse(url="/register/user", status_code=status.HTTP_303_SEE_OTHER)

# -- END OF THE ROUTE -- #


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
    tipo_combustible: str = Form(...),
    cuota_diaria: int = Form(...),
    db: Session = Depends(get_database)
):

    if not serverStatus(db):
        alert = {"type": "danger",
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
        placa=placa,
        modelo=modelo,
        marca=marca,
        tipo_combustible=tipo_combustible,
        cuota_diaria=cuota_diaria
    )

    db.add(nuevo_taxi)
    db.commit()
    db.refresh(nuevo_taxi)
    alert = {"type": "success", "message": "Taxi registrado exitosamente."}
    request.session["alert"] = alert
    return RedirectResponse(url="/register/taxi", status_code=status.HTTP_303_SEE_OTHER)


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

    return templates.TemplateResponse("index.html", {"request": request, "message": "Asignación creada con éxito"})
# -- END OF THE ROUTE -- #

# ========================================== END OF assignmentBLOCK ============================================ #


# -- MODULO 2-- #

@app.get("/register/daily", response_class=HTMLResponse, tags=["routes"])
async def registro_diario_view(request: Request, c_user: str = Cookie(None), db: Session = Depends(get_database)):
    user_id = None

    try:
        if not serverStatus(db):
            raise HTTPException(
                status_code=500, detail="Error en conexión al servidor, contacte al proveedor del servicio.")

        if not c_user:
            raise HTTPException(
                logout=401, detail="No se proporcionó un token de usuario.")

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
            raise HTTPException(
                status_code=500, detail="Error al obtener información de la empresa.")

        # Filtrar conductores por la empresa del usuario
        conductores = db.query(Usuario).filter(
            Usuario.rol == "Conductor", Usuario.empresa_id == usuario.empresa_id).all()
        
        
        # Recuperar la alerta de la sesión
        alert = request.session.pop("alert", None)
        return templates.TemplateResponse("register_daily.html", {"request": request, "alert": alert, "conductores": conductores})
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

    datos_conductor = getDriverData(id_conductor, db)

    if not datos_conductor:
        alert = {"type": "conductor_not_found",
                 "message": "El conductor no existe."}
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
        alert = {"type": "payment_already_registered",
                 "message": "Ya se registró el pago de la cuota diaria para este conductor."}
        # Almacena la alerta en la sesión
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
            raise HTTPException(
                status_code=500, detail="Error en conexión al servidor, contacte al proveedor del servicio.")

        if not c_user:
            raise HTTPException(
                logout=401, detail="No se proporcionó un token de usuario.")

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
            raise HTTPException(
                status_code=401, detail="Usuario no encontrado.")

        empresas = db.query(Empresa, Empresa.nombre).filter(
            Empresa.id_empresa == usuario.empresa_id).first()
        if not empresas:
            raise HTTPException(
                status_code=500, detail="Error al obtener información de la empresa.")

        # Filtrar conductores por la empresa del usuario
        conductores = db.query(Usuario).filter(
            Usuario.rol == "Conductor", Usuario.empresa_id == usuario.empresa_id).all()

        # Obtener fechas registradas para el conductor seleccionado
        id_conductor_default = conductores[0].id_usuario if conductores else None
        fechas_registradas = obtener_fechas_registradas(
            id_conductor_default, db)

        # Recuperar la alerta de la sesión
        alert = request.session.pop("alert", None)
        
        return templates.TemplateResponse("registerDailyUpdate.html", {"request": request, "alert": alert, "conductores": conductores, "fechas_registradas": fechas_registradas, "empresas": empresas})
    
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
            raise HTTPException(
                status_code=500, detail="Error en conexión al servidor, contacte al proveedor del servicio.")

        datos_conductor = getDriverData(id_conductor, db)

        if not datos_conductor:
            alert = {"type": "conductor_not_found",
                     "message": "El conductor no existe."}
            # Almacena la alerta en la sesión
            request.session["alert"] = alert
            return RedirectResponse(url="/update/daily", status_code=status.HTTP_303_SEE_OTHER)

        # Puedes utilizar la función datetime.strptime para convertir la cadena de fecha a un objeto datetime
        fecha_seleccionada_dt = datetime.strptime(
            fecha_seleccionada, "%Y-%m-%d").date()

        # Verificar si ya existe un pago registrado para la fecha seleccionada
        pago_existente = db.query(Pago).filter(
            Pago.id_conductor == id_conductor,
            Pago.fecha == fecha_seleccionada_dt,
            Pago.cuota_diaria_registrada == True
        ).first()

        if not pago_existente:
            alert = {"type": "payment_not_registered",
                     "message": "No se encontró un pago registrado para la fecha seleccionada."}
            # Almacena la alerta en la sesión
            request.session["alert"] = alert
            return RedirectResponse(url="/update/daily", status_code=status.HTTP_303_SEE_OTHER)
        
        # Actualizar la cuota diaria para la fecha seleccionada
        pago_existente.valor = nueva_cuota
        pago_existente.estado = nueva_cuota >= datos_conductor["cuota_diaria_taxi"]
        db.commit()

        alert = {"type": "success", "message": "Cuota diaria actualizada exitosamente."}
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

# -- PATH TO  REPORTS -- #


@app.get("/drivers", response_class=HTMLResponse, tags=["routes"])
async def drivers(request: Request,
                  db: Session = Depends(get_database)
                  ):
    conductores = db.query(Usuario).filter(Usuario.rol == 'Conductor').all()

    return templatesReports.TemplateResponse("./drivers.html", {"request": request, "usuarios": conductores})


@app.post("/reports/driver/{name}", response_class=HTMLResponse, tags=["routes"])
async def reports(request: Request,
                  id_usuario: int = Form(...),
                  db: Session = Depends(get_database)
                  ):
    reports = db.query(Pago).filter(Pago.id_conductor == id_usuario).all()

    return templatesReports.TemplateResponse("./dailyreports.html", {"request": request, "reports": reports})


@app.get("/404-NotFound", response_class=HTMLResponse, tags=["routes"])
async def not_found(request: Request, c_user: str = Cookie(None)):
    if not c_user:
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("./error404.html", {"request": request})


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return RedirectResponse(url="/404-NotFound", status_code=status.HTTP_303_SEE_OTHER)
