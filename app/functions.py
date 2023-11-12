from jose import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import text

import os

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
        alert = {"type": "general",
            "message": "Error en conexión al servidor, contacte al proveedor del servicio."}
        return alert
    except OperationalError:
        return False