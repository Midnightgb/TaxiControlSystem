from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Date
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum

Base = declarative_base()


class Rol(PyEnum):
    Administrador = "Administrador"
    Conductor = "Conductor"


class Estado(PyEnum):
    Activo = "Activo"
    Inactivo = "Inactivo"


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    cedula = Column(Integer, nullable=False, unique=True)
    nombre = Column(String(45), nullable=False)
    apellido = Column(String(45), nullable=False)
    correo = Column(String(45))
    contrasena = Column(String(45))
    rol = Column(Enum(Rol), nullable=False)
    estado = Column(Enum(Estado), nullable=False)
    created_at = Column(String, server_default=func.now(), nullable=False)
    updated_at = Column(String, server_default=func.now(),
                        onupdate=func.now(), nullable=False)


class Taxi(Base):
    __tablename__ = "taxis"

    id_taxi = Column(Integer, primary_key=True, autoincrement=True)
    id_conductor = Column(Integer, ForeignKey("usuarios.id_usuario"))
    placa = Column(String(6), nullable=False, unique=True)
    modelo = Column(String(45), nullable=False)
    marca = Column(String(45), nullable=False)
    fecha_adquisicion = Column(Date)
    created_at = Column(String, server_default=func.now(), nullable=False)
    updated_at = Column(String, server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    conductor = relationship("Usuario", back_populates="taxis")


class Mantenimiento(Base):
    __tablename__ = "mantenimientos"

    id_mantenimiento = Column(Integer, primary_key=True, autoincrement=True)
    id_taxi = Column(Integer, ForeignKey("taxis.id_taxi"))
    fecha = Column(Date, nullable=False)
    descripcion = Column(String(155), nullable=False)
    costo = Column(Integer, nullable=False)
    created_at = Column(String, server_default=func.now(), nullable=False)
    updated_at = Column(String, server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    taxi = relationship("Taxi", back_populates="mantenimientos")


class Pago(Base):
    __tablename__ = "pagos"

    id_pago = Column(Integer, primary_key=True, autoincrement=True)
    id_conductor = Column(Integer, ForeignKey("usuarios.id_usuario"))
    fecha = Column(Date, nullable=False)
    valor = Column(Integer, nullable=False)
    created_at = Column(String, server_default=func.now(), nullable=False)
    updated_at = Column(String, server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    conductor = relationship("Usuario", back_populates="pagos")


class Reporte(Base):
    __tablename__ = "reportes"

    id_reporte = Column(Integer, primary_key=True, autoincrement=True)
    id_conductor = Column(Integer, ForeignKey("usuarios.id_usuario"))
    fecha = Column(Date, nullable=False)
    ingresos = Column(Integer, nullable=False)
    gastos = Column(Integer, nullable=False)
    created_at = Column(String, server_default=func.now(), nullable=False)
    updated_at = Column(String, server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    conductor = relationship("Usuario", back_populates="reportes")
