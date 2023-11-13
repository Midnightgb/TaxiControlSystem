from jose import jwt
from fastapi import HTTPException, Depends
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import text
from fastapi.security import OAuth2PasswordBearer

import os
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