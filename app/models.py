from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Float, Date, Boolean, Time
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum

Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    cedula = Column(Integer, unique=True, nullable=False)
    nombre = Column(String(45), nullable=False)
    apellido = Column(String(45), nullable=False)
    correo = Column(String(45))
    contrasena = Column(String(45))
    rol = Column(Enum('Administrador', 'Conductor'), nullable=False)
    estado = Column(Enum('Activo', 'Inactivo'), default='Activo', nullable=False)