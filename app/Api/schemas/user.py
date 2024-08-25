from pydantic import BaseModel
from typing import Optional
from Api.schemas.role import Rol 

class UserBase(BaseModel):
    cedula: str
    nombre: str
    apellido: str
    correo: str
    telefono: str
    rol: Rol
    empresa_id: int

class UserCreate(UserBase):
    contrasena: Optional[str] = None
    imagen: Optional[UploadFile] = None
    
