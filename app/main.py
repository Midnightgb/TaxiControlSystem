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
from datetime import date 
from models import Usuario, Pago, Taxi
from database import get_database


app = FastAPI()

app.mount("/static", StaticFiles(directory="public/dist"), name="static")

templates = Jinja2Templates(directory="public/templates")

@app.get("/", response_class=HTMLResponse, tags=["root"])
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

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
    cedula_existente = db.query(Usuario).filter(Usuario.cedula == cedula).first()
    if cedula_existente:
        raise HTTPException(status_code=400, detail="La cédula ya está en uso.")

    correo_existente = db.query(Usuario).filter(Usuario.correo == correo).first()
    if correo_existente:
        raise HTTPException(status_code=400, detail="El correo ya está en uso.")

    nuevo_usuario = Usuario(cedula=cedula, nombre=nombre, apellido=apellido, correo=correo, contrasena=contrasena, rol=rol,estado='Activo')
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




