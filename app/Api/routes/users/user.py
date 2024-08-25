from fastapi import APIRouter, Request, Depends, Cookie, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from Api.schemas.user import UserCreate
from Api.crud import create_user_in_db, check_existing_cedula_and_correo, get_user_by_id
from db.connection import get_session
from core.utils.serverStatus import serverStatus
from core.utils.tokenDecoder import tokenDecoder
import bcrypt

router = APIRouter()

@router.post("/register/user", response_class=HTMLResponse)
async def create_user(
    request: Request,
    user: UserCreate,
    db: Session = Depends(get_session),
    c_user: str = Cookie(None)
):
    # Verificar estado del servidor
    if not serverStatus(db):
        request.session["alert"] = {
            "type": "general",
            "message": "Error en conexión al servidor, contacte al proveedor del servicio."
        }
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar que el usuario esté autenticado
    if not c_user:
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    token_payload = tokenDecoder(c_user)
    if not token_payload:
        request.session["alert"] = {
            "type": "general",
            "message": "Su sesión ha expirado, por favor inicie sesión nuevamente."
        }
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    # Obtener el usuario autenticado
    user_id = int(token_payload["sub"])
    usuario = get_user_by_id(db, user_id)
    if not usuario:
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar si la cédula o el correo ya existen
    cedula_existente, correo_existente = check_existing_cedula_and_correo(db, user.cedula, user.correo)
    if cedula_existente:
        request.session["alert"] = {"type": "error", "message": "La cédula ya está en uso."}
        return RedirectResponse(url="/register/user", status_code=status.HTTP_303_SEE_OTHER)
    if correo_existente:
        request.session["alert"] = {"type": "error", "message": "El correo ya está en uso."}
        return RedirectResponse(url="/register/user", status_code=status.HTTP_303_SEE_OTHER)

    # Encriptar la contraseña solo si se proporciona una
    hashed_password = None
    if user.contrasena and user.rol != "Conductor":
        hashed_password = bcrypt.hashpw(user.contrasena.encode('utf-8'), bcrypt.gensalt())

    # Convertir la imagen a bytes si se proporciona
    image_bytes = None
    if user.imagen:
        image_bytes = convert_to_bynary(user.imagen)

    # Crear el nuevo usuario en la base de datos
    nuevo_usuario = create_user_in_db(db, user, hashed_password, image_bytes)

    # Configurar la alerta de éxito
    request.session["alert"] = {"type": "success", "message": "Usuario registrado exitosamente."}
    return RedirectResponse(url="/register/user", status_code=status.HTTP_303_SEE_OTHER)
