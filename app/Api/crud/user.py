from sqlalchemy.orm import Session
from .models import Usuario
from .schemas import UserCreate
import bcrypt

def create_user_in_db(db: Session, user: UserCreate, hashed_password: Optional[str], image_bytes: Optional[bytes]):
    nuevo_usuario = Usuario(
        cedula=user.cedula,
        nombre=user.nombre,
        apellido=user.apellido,
        correo=user.correo.lower(),
        contrasena=hashed_password,
        rol=user.rol,
        estado='Activo',
        empresa_id=user.empresa_id,
        foto=image_bytes if image_bytes else None
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario

def check_existing_cedula_and_correo(db: Session, cedula: str, correo: str):
    cedula_existente = db.query(Usuario).filter(Usuario.cedula == cedula).first()
    correo_existente = db.query(Usuario).filter(Usuario.correo == correo).first()
    return cedula_existente, correo_existente

def get_user_by_id(db: Session, user_id: int):
    return db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
