from jose import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import text

import os
from database import SessionLocal
from models import ConductorActual

load_dotenv()
SECRET_KEY = os.environ.get("SECRET_KEY")


def tokenConstructor(userId: str):
    print("##########$$$$$$$$$$$$########## tokenConstructor ##########$$$$$$$$$$$$##########")
    expiration = datetime.utcnow() + timedelta(hours=1)
    payload = {"sub": userId, "exp": expiration}
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
