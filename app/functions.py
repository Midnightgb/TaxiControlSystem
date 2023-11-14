from jose import jwt
from fastapi import HTTPException, Depends
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import text
from fastapi.security import OAuth2PasswordBearer

import os

from database import SessionLocal
from models import ConductorActual

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
    

def get_datos_conductor(id_conductor, db: SessionLocal):
    if id_conductor:
        conductor_actual = db.query(ConductorActual).filter_by(
            id_conductor=id_conductor
        ).first()

        if conductor_actual:
            # relación 'taxi' para obtener el taxi
            taxi = conductor_actual.taxi

            if taxi:
                datos_conductor = {
                    "id_conductor": id_conductor,
                    "nombre": conductor_actual.conductor.nombre,
                    "apellido": conductor_actual.conductor.apellido,
                    "correo": conductor_actual.conductor.correo,
                    "cuota_diaria_taxi": taxi.cuota_diaria,
                }
                return datos_conductor
            else:
                return None
        else:
            return None
    else:
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
