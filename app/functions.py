from jose import jwt
from datetime import datetime, timedelta
import os

SECRET_KEY = os.environ.get("SECRET_KEY")

def tokenConstructor(usuario_id: str):
    expiration = datetime.utcnow() + timedelta(hours=1)  
    payload = {"sub": usuario_id, "exp": expiration}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token