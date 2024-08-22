# core/utils/serverStatus.py
from sqlalchemy.exc import OperationalError
from sqlalchemy import text
from fastapi import Request

# Función para verificar si el servidor de base de datos está disponible y acepta conexiones
def serverStatus(db, request: Request) -> bool:
    try:
        db.execute(text('SELECT 1'))
        return True
    except OperationalError:
        alert = {"type": "general", "message": "Error en conexión al servidor, contacte al proveedor del servicio."}
        request.session["alert"] = alert
        return False
