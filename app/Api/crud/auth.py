# Api/crud/auth.py
from Api.models.user import Usuario
from sqlalchemy.orm import Session
from typing import Optional
from fastapi import Request
import bcrypt
from datetime import datetime, timedelta
from jose import jwt
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")

def verificateCharacter(user: str, db: Session) -> Optional[Usuario]:
    if '@' in user:
        return db.query(Usuario).filter(Usuario.correo == user).first()
    else:
        return db.query(Usuario).filter(Usuario.cedula == user).first()

def verifyPassword(password: str, hashed_password: str, request: Request) -> bool:
    if not bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
        alert = {"type": "pass", "message": "La contraseña que ingresaste es incorrecta.", "link": "/login/recover"}
        request.session["alert"] = alert
        return False
    return True

def tokenConstructor(userId: str):
    print("##########$$$$$$$$$$$$########## tokenConstructor ##########$$$$$$$$$$$$##########")
    expiration = datetime.utcnow() + timedelta(hours=1)
    payload = {"sub": str(userId), "exp": expiration}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token
