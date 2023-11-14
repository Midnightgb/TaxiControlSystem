from jose import jwt
from fastapi import HTTPException, Depends
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import joinedload, Session
from sqlalchemy.sql import text
from fastapi.security import OAuth2PasswordBearer

import os

from database import SessionLocal, get_database
from models import ConductorActual, Usuario, Taxi, Pago

from fastapi import status
from fastapi.responses import RedirectResponse


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
        print("conductor actual:", conductor_actual.id_taxi)
        if conductor_actual:
            taxi = conductor_actual.id_taxi
            taxi = db.query(Taxi).filter(
                Taxi.id_taxi==taxi
            ).first()
            
            data = {
                "id_conductor": conductor_actual.id_conductor,
                "nombre": conductor_actual.conductor.nombre,
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

def obtener_fechas_conductor(id_conductor, db: Session):
    if id_conductor:
        # Obtener las fechas asociadas al conductor desde la base de datos
        fechas_conductor = db.query(Pago.fecha).filter(
            Pago.id_conductor == id_conductor
        ).order_by(Pago.fecha.desc()).limit(7).all()

        # Desempaquetar las fechas de la lista de tuplas
        fechas_conductor = [fecha[0] for fecha in fechas_conductor]

        return fechas_conductor
    else:
        return []