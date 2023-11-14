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
from models import Usuario, Empresa, Taxi, Pago, ConductorActual   

from database import get_database
from starlette.middleware.sessions import SessionMiddleware

load_dotenv()
MIDDLEWARE_KEY = os.environ.get("MIDDLEWARE_KEY")

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=MIDDLEWARE_KEY)
app.mount("/static", StaticFiles(directory="public/dist"), name="static")
templates = Jinja2Templates(directory="public/templates")
templatesReports = Jinja2Templates(directory="public/templates/Reports")


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
        alert = {"type": "pass","message": "La contraseña que ingresaste es incorrecta.", "link": "/login/recover"}
        request.session["alert"] = alert
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    if usuario.estado == 'Inactivo':
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
async def home(request: Request, c_user: str = Cookie(None)):
    if not c_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    checkTokenStatus = userStatus(c_user, request)
    if not checkTokenStatus["status"]:
        return checkTokenStatus["redirect"]

    alert = request.session.pop("alert", None)
    return templates.TemplateResponse("./index.html", {"request": request, "alert": alert})

@app.get("/logout", tags=["auth"])
async def logout(): 
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="c_user")
    return response

# ========================================== USERBLOCK ============================================ #

# -- PATH TO REDIRECT TO USER CREATION -- #
@app.get("/register/user", response_class=HTMLResponse, tags=["create"])
async def create(request: Request, c_user: str = Cookie(None), db: Session = Depends(get_database)):
    user_id = None

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

    empresa = db.query(Empresa).filter(Empresa.id_empresa == usuario.empresa_id).first()

    if not empresa:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse("CreateUser.html", {"request": request, "empresa": empresa, "usuario": usuario})
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

    empresa = db.query(Empresa).filter(Empresa.id_empresa == usuario.empresa_id).first()

    cedula_existente = db.query(Usuario).filter(Usuario.cedula == cedula).first()
    if cedula_existente:
        error_message = "La cédula ya está en uso."

    correo_existente = db.query(Usuario).filter(Usuario.correo == correo).first()
    if correo_existente:
        print("paso 3")
        error_message = "El correo ya está en uso."

    if error_message:
        return templates.TemplateResponse("CreateUser.html", {"request": request, "error_message": error_message,"empresa":empresa, "usuario": usuario})

    # Encriptar la contraseña solo si se proporciona una
    hashed_password = None
    if contrasena and rol != "Conductor":
        print("paso 4")
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
    print("paso 5")
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    print("paso 6")
    return templates.TemplateResponse("index.html", {"request": request})

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
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

        token_payload = tokenDecoder(c_user)

        user_id = int(token_payload["sub"])

        usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()

        if not usuario:
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

        empresas = db.query(Empresa).filter(Empresa.id_empresa == usuario.empresa_id).all()

        if not empresas:
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

        return templates.TemplateResponse("CreateTaxi.html", {"request": request, "empresas": empresas, "alert": alert})
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
    
        if not serverStatus(db):
            alert = {"type": "danger","message": "Error en conexión al servidor, contacte al proveedor del servicio."}
            request.session["alert"] = alert
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

        # Validar que la placa no esté vacía
        if not placa:
            alert = {"type":"danger" ,"message": "La placa no puede estar vacía."}
            request.session["alert"] = alert
            return RedirectResponse(url="/register/taxi", status_code=status.HTTP_303_SEE_OTHER)
        
        #verificar q la placa este bien escrita
        if len(placa) != 6:
            alert = {"type":"danger" ,"message": "La placa debe tener 6 caracteres."}
            request.session["alert"] = alert
            return RedirectResponse(url="/register/taxi", status_code=status.HTTP_303_SEE_OTHER)
        
        if(verificar_formato(placa) == False):
            alert = {"type":"danger" ,"message": "La placa debe tener el formato AAA000."}
            request.session["alert"] = alert
            return RedirectResponse(url="/register/taxi", status_code=status.HTTP_303_SEE_OTHER)
        
        # Verificar si la placa ya existe en la base de datos
        if db.query(Taxi).filter(Taxi.placa == placa).first():
            alert = {"type": "danger","message": "La placa ya está registrada."}
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
        alert = {"type": "succes","message": "Taxi creado con éxito"}
        request.session["alert"] = alert
        return RedirectResponse(url="/home", status_code=status.HTTP_303_SEE_OTHER)


# ========================================== END OF TAXIBLOCK ============================================ #

# ========================================== ALLOCATIONBLOCK ============================================ #

# -- PATH TO REDIRECT TO ALLOCATION CREATION -- #
@app.get("/register/allocation", response_class=HTMLResponse, tags=["create"])
async def create(request: Request, c_user: str = Cookie(None), db: Session = Depends(get_database)):
    user_id = None
    print("ENTRO A PASO 1", c_user)
    if not c_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    token_payload = tokenDecoder(c_user)

    user_id = int(token_payload["sub"])

    usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()

    if not usuario:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    # Recuperar alerta de la sesión
    alert = request.session.pop("alert", None)

    # Subconsulta para obtener los IDs de conductores asignados
    conductores_asignados_subquery = db.query(ConductorActual.id_conductor).distinct()

    # Subconsulta para obtener los IDs de taxis asignados
    taxis_asignados_subquery = db.query(ConductorActual.id_taxi).distinct()

    # Consulta para traer los conductores no asignados en la misma empresa
    conductores_no_asignados = db.query(Usuario).filter(
        Usuario.rol == "conductor",
        Usuario.empresa_id == usuario.empresa_id,
        Usuario.id_usuario.in_(conductores_asignados_subquery),
    ).all()

    # Consulta para traer los taxis no asignados en la misma empresa
    taxis_no_asignados = db.query(Taxi).filter(
        Taxi.empresa_id == usuario.empresa_id,
        Taxi.id_taxi.in_(taxis_asignados_subquery),
    ).all()

    print("Usuario:", usuario)
    print("Roles del usuario:", usuario.rol)
    print("Token Payload:", token_payload)
    print("Conductores no asignados:", conductores_no_asignados)
    print("Taxis no asignados:", taxis_no_asignados)

    return templates.TemplateResponse("CreateAllocation.html", {"request": request, "conductores": conductores_no_asignados, "taxis": taxis_no_asignados, "alert": alert})
# -- END OF THE ROUTE -- #


# -- PATH TO PROCEED TO THE CREATION OF A NEW ALLOCATION -- #
@app.post("/register/allocation", response_class=HTMLResponse)
async def create_allocation(
    request: Request,
    id_conductor: int = Form(...),
    id_taxi: int = Form(...),
    db: Session = Depends(get_database)
):

    try:
        if not serverStatus(db):
            alert = {"type": "general","message": "Error en conexión al servidor, contacte al proveedor del servicio."}
            request.session["alert"] = alert
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

        # Verificar si el conductor ya está asignado a un taxi
        if db.query(ConductorActual).filter(ConductorActual.id_conductor == id_conductor).first():
            raise HTTPException(status_code=400, detail="El conductor ya está asignado a un taxi.")

        # Si pasa las validaciones, proceder con la creación de la asignación
        nueva_asignacion = ConductorActual(
            id_conductor=id_conductor,
            id_taxi=id_taxi
        )
        
        if nueva_asignacion:
            alert = {"type": "general","message": "Asignación creada con éxito."}
            request.session["alert"] = alert
            return RedirectResponse(url="/register/allocation", status_code=status.HTTP_303_SEE_OTHER)
        
        
        if not nueva_asignacion:
            alert = {"type": "general","message": "Error al crear la asignación."}
            request.session["alert"] = alert
            return RedirectResponse(url="/register/allocation", status_code=status.HTTP_303_SEE_OTHER)
        
        
        db.add(nueva_asignacion)
        db.commit()
        db.refresh(nueva_asignacion)

        return templates.TemplateResponse("index.html", {"request": request, "message": "Asignación creada con éxito"})
    except HTTPException as e:
        # Capturamos las excepciones específicas de FastAPI
        return templates.TemplateResponse("index.html", {"request": request, "error_message": e.detail})
    except Exception as e:
        # Capturamos otras excepciones y mostramos un mensaje genérico de error
        return templates.TemplateResponse("index.html", {"request": request, "error_message": "Error al procesar la solicitud."})
# -- END OF THE ROUTE -- #

# ========================================== END OF ALLOCATIONBLOCK ============================================ #





# -- MODULO 2-- #

@app.get("/register/daily", response_class=HTMLResponse, tags=["routes"])
async def registro_diario_view(request: Request, c_user: str = Cookie(None), db: Session = Depends(get_database)):
    user_id = None
    
    try:
        if not serverStatus(db):
            raise HTTPException(status_code=500, detail="Error en conexión al servidor, contacte al proveedor del servicio.")
        
        if not c_user:
            raise HTTPException(status_code=401, detail="No se proporcionó un token de usuario.")
        
        token_payload = tokenDecoder(c_user)
        
        if not token_payload:
            alert = {"type": "general","message": "Su sesion ha expirado, por favor inicie sesión nuevamente."}
            request.session["alert"] = alert
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        
        user_id = int(token_payload["sub"])
        usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
        if not usuario:
            raise HTTPException(status_code=401, detail="Usuario no encontrado.")
        
        empresas = db.query(Empresa).filter(Empresa.id_empresa == usuario.empresa_id).first()
        if not empresas:
            raise HTTPException(status_code=500, detail="Error al obtener información de la empresa.")
        
        # Filtrar conductores por la empresa del usuario
        conductores = db.query(Usuario).filter(Usuario.rol == "Conductor", Usuario.empresa_id == usuario.empresa_id).all()
        # Recuperar la alerta de la sesión
        alert = request.session.pop("alert", None)
        return templates.TemplateResponse("register_daily.html", {"request": request, "alert": alert, "conductores": conductores})
    except HTTPException as e:
        alert = {"type": "general", "message": str(e.detail)}
        request.session["alert"] = alert
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    except Exception as e:
        alert = {"type": "general", "message": "Error de servidor. Inténtelo nuevamente más tarde."}
        request.session["alert"] = alert
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
   
# -- MODULO 2 actualizar registro diario-- #    
@app.post("/register/daily", tags=["payments"])
async def registro_diario(
    request: Request,
    id_conductor: int = Form(...),
    valor: int = Form(...),
    db: Session = Depends(get_database),
):  
    if not serverStatus(db):
        alert = {"type": "general","message": "Error en conexión al servidor, contacte al proveedor del servicio."}
        request.session["alert"] = alert
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    datos_conductor = getDriverData(id_conductor, db)

    if not datos_conductor:
        alert = {"type": "conductor_not_found", "message": "El conductor no existe."}
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
        alert = {"type": "payment_already_registered", "message": "Ya se registró el pago de la cuota diaria para este conductor."}
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

@app.get("/update/driver", response_class=HTMLResponse, tags=["routes"])
async def update_driver_value_view(request: Request, c_user: str = Cookie(None), db: Session = Depends(get_database)):
    user_id = None
    
    try:
        print("paso 1 get")
        if not serverStatus(db):
            print("paso 2 get")
            raise HTTPException(status_code=500, detail="Error en conexión al servidor, contacte al proveedor del servicio.")
        print("paso 3 get")
        if not c_user:
            print("paso 4 get")
            raise HTTPException(status_code=401, detail="No se proporcionó un token de usuario.")
        
        print("paso 5 get")
        token_payload = tokenDecoder(c_user)
        
        print("paso 6 get")
        if not token_payload:
            print("paso 7 get")
            alert = {"type": "general","message": "Su sesión ha expirado, por favor inicie sesión nuevamente."}
            request.session["alert"] = alert
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        
        print("paso 8 get")
        user_id = int(token_payload["sub"])
        usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
        print("paso 9 get")
        if not usuario:
            print("paso 10 get")
            raise HTTPException(status_code=401, detail="Usuario no encontrado.")
        
        empresas = db.query(Empresa).filter(Empresa.id_empresa == usuario.empresa_id).first()
        print("paso 11 get")
        if not empresas:
            print("paso 12 get")
            raise HTTPException(status_code=500, detail="Error al obtener información de la empresa.")
        
        # Filtrar conductores por la empresa del usuario
        conductores = db.query(Usuario).filter(Usuario.rol == "Conductor", Usuario.empresa_id == usuario.empresa_id).all()

        # Consultar fechas del conductor
        fechas_conductor = db.query(Pago.fecha).filter(Pago.id_conductor == user_id).all()

        # Recuperar la alerta de la sesión
        alert = request.session.pop("alert", None)
        print("paso 13 get")
        return templates.TemplateResponse("registerDailyUpdate.html", {
            "request": request,
            "alert": alert,
            "conductores": conductores,
            "fechas_conductor": fechas_conductor  # Agregar las fechas del conductor
        })
        print("paso 14 get")

    except HTTPException as e:
        alert = {"type": "general", "message": str(e.detail)}
        request.session["alert"] = alert
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    except Exception as e:
        alert = {"type": "general", "message": "Error de servidor. Inténtelo nuevamente más tarde."}
        request.session["alert"] = alert
        print("Error paso 15:", str(e))
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/update/driver", tags=["payments"])
async def update_driver_value(
    request: Request,
    id_conductor: int = Form(...),
    valor: int = Form(...),
    fecha_seleccionada: date = Form(...),
    db: Session = Depends(get_database),
    
):  
    print("paso 1 post")
    if not serverStatus(db):
        print("paso 2 post")
        alert = {"type": "general","message": "Error en conexión al servidor, contacte al proveedor del servicio."}
        request.session["alert"] = alert
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    datos_conductor = getDriverData(id_conductor, db)

    print("paso 3 post")
    if not datos_conductor:
        print("paso 4 post")
        alert = {"type": "conductor_not_found", "message": "El conductor no existe."}
        # Almacena la alerta en la sesión
        request.session["alert"] = alert
        return RedirectResponse(url="/update/driver", status_code=status.HTTP_303_SEE_OTHER)

    print("paso 5 post")
    # Verificar si ya existe un registro para la fecha seleccionada
    pago_existente = db.query(Pago).filter(
        Pago.id_conductor == id_conductor,
        Pago.fecha == fecha_seleccionada
    ).first()

    print("paso 6 post")
    if pago_existente:
        print("paso 7 post")
        # Si existe, actualizar el valor
        pago_existente.valor = valor
        pago_existente.estado = valor >= datos_conductor["cuota_diaria_taxi"]
    else:
        print("paso 8 post")
        # Si no existe, crear un nuevo registro
        estado = valor >= datos_conductor["cuota_diaria_taxi"]
        nuevo_pago = Pago(
            id_conductor=id_conductor,
            fecha=fecha_seleccionada,
            valor=valor,
            estado=estado,
            cuota_diaria_registrada=True
        )
        db.add(nuevo_pago)

    db.commit()
    print("paso 9 post")
    alert = {"type": "success", "message": "Valor del conductor actualizado exitosamente."}
    # Almacena la alerta en la sesión
    request.session["alert"] = alert

    # Redirige a la vista de actualización de valor del conductor
    return RedirectResponse(url="/update/driver", status_code=status.HTTP_303_SEE_OTHER)
# -- FIN MODULO 2-- #

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


# -- PATH TO  REPORTS -- #
@app.get("/drivers", response_class=HTMLResponse, tags=["routes"])
async def drivers(request: Request,
                    db: Session = Depends(get_database)
                ):
    conductores=db.query(Usuario).filter(Usuario.rol == 'Conductor').all()

    return templatesReports.TemplateResponse("./drivers.html", {"request": request, "usuarios": conductores})

@app.post("/reports", response_class=HTMLResponse, tags=["routes"])
async def reports(request: Request,
                    id_usuario: int = Form(...),
                    db: Session = Depends(get_database)
                ):
    reports= db.query(Pago).filter(Pago.id_conductor == id_usuario).all()

    return templatesReports.TemplateResponse("./dailyreports.html", {"request": request, "reports": reports})

