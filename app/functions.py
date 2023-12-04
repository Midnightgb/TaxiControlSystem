from jose import jwt
from fastapi import HTTPException, Depends
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import func
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import joinedload, Session
from sqlalchemy.sql import text
from fastapi.security import OAuth2PasswordBearer

import os

from database import SessionLocal, get_database
from models import *

from fastapi import status
from fastapi.responses import RedirectResponse
import re
from PIL import Image
from io import BytesIO
import base64

from typing import List



load_dotenv()
SECRET_KEY = os.environ.get("SECRET_KEY")
def tokenConstructor(userId: str):
    print("##########$$$$$$$$$$$$########## tokenConstructor ##########$$$$$$$$$$$$##########")
    expiration = datetime.utcnow() + timedelta(hours=1)
    payload = {"sub": str(userId), "exp": expiration}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def serverStatus(db):
    try:
        db.execute(text('SELECT 1'))
        return True
    except OperationalError:
        return False
    

def getDriverData(id_conductor, db: SessionLocal):
    if id_conductor:
        conductor_actual = db.query(ConductorActual).filter(
            ConductorActual.id_conductor==id_conductor
        ).first()

        if conductor_actual and conductor_actual.taxi:
            taxi = conductor_actual.taxi
            data = {
                "id_conductor": conductor_actual.id_conductor,
                "nombre": conductor_actual.conductor.nombre,
                "apellido": conductor_actual.conductor.apellido,
                "cuota_diaria_taxi": taxi.cuota_diaria,
            }
            return data
    return None
     
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
def tokenDecoder(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        print("##########$$$$$$$$$$$$########## tokenDecoder ##########$$$$$$$$$$$$##########")
        print("Payload del token decodificado:", payload)
        return payload
    except jwt.ExpiredSignatureError:
        return False
    except jwt.JWTError:
        raise False
        
def verificar_formato(cadena):
    # El patrón es: tres letras seguidas de tres números
    patron = re.compile(r'^[a-zA-Z]{3}\d{3}$')

    # Verificar si la cadena coincide con el patrón
    if patron.match(cadena):
        return True
    else:
        return False

def userStatus(c_user, request):
    token_payload = tokenDecoder(c_user)
    if not token_payload:
        alert = {"type": "general","message": "Su sesion ha expirado, por favor inicie sesión nuevamente."}
        request.session["alert"] = alert
        redirect_response = RedirectResponse(url='/logout', status_code=status.HTTP_303_SEE_OTHER)
        redirect_response.delete_cookie("c_user")
        validation = {
            "status": False,
            "redirect": redirect_response
        }
        return validation
    else:
        validation = {"status": True, "userid": token_payload["sub"]}
        return validation

def obtener_fechas_registradas(id_conductor, db):
    fechas_registradas = db.query(func.distinct(Pago.fecha)).filter(
        Pago.id_conductor == id_conductor,
        Pago.cuota_diaria_registrada == True
    ).all()
    return [fecha[0] for fecha in fechas_registradas]

def obtener_cuota_actual(id_conductor, fecha_seleccionada, db):
    cuota_actual = db.query(Pago.valor).filter(
        Pago.id_conductor == id_conductor,
        Pago.fecha == fecha_seleccionada,
        Pago.cuota_diaria_registrada == True
    ).first()
    return cuota_actual[0] if cuota_actual else None

    
def convert_to_bynary(upload_file):
    try:
        if upload_file and hasattr(upload_file, 'file'):
            
            with upload_file.file as imagen_archivo:
                imagen = imagen_archivo.read()
                return imagen
        else:
            return None
    except Exception as e:
        print(f"Error al convertir a binario: {e}")
        return None

def convertIMG(foto: bytes):
    try:
        image = Image.open(BytesIO(foto))
        img_io = BytesIO()
        image.save(img_io, format='JPEG')
        img_io.seek(0)
        base64_image = base64.b64encode(img_io.getvalue()).decode('utf-8')
        return f"data:image/jpeg;base64,{base64_image}"
    except Exception as e:
        print(f"Error al procesar la imagen: {str(e)}")
        return None



def obtener_usuarios_paginados(
    db: Session,
    page: int = 1,
    per_page: int = 8,
    empresa_id: int = None,
    rol: str = None
) -> List[Usuario]:
    offset = (page - 1) * per_page

    
    total_usuarios = db.query(func.count(Usuario.id_usuario)).filter(
        Usuario.empresa_id == empresa_id,
        Usuario.rol == rol
    ).scalar()

    
    total_paginas = (total_usuarios + per_page - 1) // per_page

    
    usuarios_paginados = db.query(Usuario).filter(
        Usuario.empresa_id == empresa_id,
        Usuario.rol == rol
    ).offset(offset).limit(per_page).all()

    return {"usuarios": usuarios_paginados, "total_paginas": total_paginas}

def obtener_taxis_paginados(db: Session, page: int = 1, tax_page: int = 8, empresa_id: int = None,assigned: bool = None) -> List[Taxi]:
    offset = (page - 1) * tax_page

    
    if assigned is not None:
        query = db.query(Taxi).filter(
            Taxi.empresa_id == empresa_id,
            Taxi.id_taxi.in_(db.query(ConductorActual.id_taxi)) if assigned else ~Taxi.id_taxi.in_(db.query(ConductorActual.id_taxi))
        )
    else:
        query = db.query(Taxi).filter(
            Taxi.empresa_id == empresa_id
        )
    
    total_taxis = query.count()

    total_paginas = (total_taxis + tax_page - 1) // tax_page

    taxis_paginados = query.offset(offset).limit(tax_page).all()

    
    
    return {"taxis": taxis_paginados, "total_paginas": total_paginas}

