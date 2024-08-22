# core/utils/userValidations.py
from sqlalchemy.exc import OperationalError
from fastapi import Request
from Api.schemas.role import Rol
from Api.schemas.status import Estado

def userValidation(user: str, password: str, request: Request) -> bool:
    if not user or not password:
        alert = {"type": "user", "message": "Las crendenciales que ingresaste no coincide con ningún usuario."}
        request.session["alert"] = alert
        return False
    return True

def checkUserExist(user: str, request: Request) -> bool:
    try:
        if user:
            return True
    except OperationalError:
        alert = {"type": "user","message": "El correo o la cédula que ingresaste no coincide con ningún usuario."}
        request.session["alert"] = alert
        return False

def checkRoleUser(userRole: str, request: Request) -> bool:
    try:
        if userRole == Rol.Conductor:
            alert = {"type": "user", "message": "Las crendenciales que ingresaste no coincide con ningún usuario."}
            request.session["alert"] = alert
            return True
    except OperationalError:
        return False

def checkStatusUser(userStatus: str, request: Request) -> bool:
    try:
        if userStatus == Estado.Inactivo:
            alert = {"type": "general","message": "El usuario se encuentra inactivo, contacte al proveedor del servicio."}
            request.session["alert"] = alert
            return True
    except OperationalError:
        return False