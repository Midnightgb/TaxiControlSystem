from sqlalchemy import Column, Integer, String, Enum, TIMESTAMP, LargeBinary
from sqlalchemy.sql import func
from Api.models.base_class import Base
from Api.models import Empresa, Notificaciones, Taxi, Pago 

class Usuario(Base):
    __tablename__ = 'usuarios'

    id_usuario = Column(Integer, primary_key=True)
    cedula = Column(Integer, nullable=False)
    nombre = Column(String(45), nullable=False)
    apellido = Column(String(45), nullable=False)
    correo = Column(String(45), default=None)
    contrasena = Column(String(250), default=None)
    rol = Column(Enum('Administrador', 'Conductor', 'Secretaria'), nullable=False)
    estado = Column(Enum('Activo', 'Inactivo'), nullable=False, default='Activo')
    foto = Column(LargeBinary, default=None)
    empresa_id = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    empresa = relationship("Empresa", back_populates="usuarios")
    taxis = relationship("ConductorActual", back_populates="conductor")
    pagos = relationship("Pago", back_populates="conductor")
    notificaciones = relationship("Notificaciones", back_populates="usuario")