from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Date, Boolean
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum

Base = declarative_base()


class Rol(PyEnum):
    Administrador = "Administrador"
    Conductor = "Conductor"
    Secretaria = "Secretaria"


class Estado(PyEnum):
    Activo = "Activo"
    Inactivo = "Inactivo"


class Empresa(Base):
    __tablename__ = "empresas"

    id_empresa = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(45), nullable=False)
    direccion = Column(String(45), nullable=False)
    telefono = Column(String(45), nullable=False)
    correo = Column(String(45), nullable=False)
    created_at = Column(String, server_default=func.now(), nullable=False)
    updated_at = Column(String, server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    usuarios = relationship("Usuario", back_populates="empresa")
    taxis = relationship("Taxi", back_populates="empresa")
    reportes = relationship("Reporte", back_populates="empresa")
    configuracion_plan = relationship(
        "ConfiguracionPlan", back_populates="empresa")
    configuracion_app = relationship(
        "ConfiguracionApp", back_populates="empresa")


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
    empresa = Column(Integer, ForeignKey("empresas.id_empresa"))
    created_at = Column(String, server_default=func.now(), nullable=False)
    updated_at = Column(String, server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    empresa = relationship("Empresa", back_populates="usuarios")
    taxis = relationship("Taxi", back_populates="conductor")
    pagos = relationship("Pago", back_populates="conductor")


class Taxi(Base):
    __tablename__ = "taxis"

    id_taxi = Column(Integer, primary_key=True, autoincrement=True)
    empresa = Column(Integer, ForeignKey("empresas.id_empresa"))
    id_conductor = Column(Integer, ForeignKey("usuarios.id_usuario"))
    placa = Column(String(6), nullable=False, unique=True)
    modelo = Column(String(45), nullable=False)
    marca = Column(String(45), nullable=False)
    tipo_combustible = Column(Enum("Gasolina", "Ambos", "Gas"), nullable=False)
    cuota_diaria = Column(Integer, nullable=False)
    fecha_adquisicion = Column(Date)
    created_at = Column(String, server_default=func.now(), nullable=False)
    updated_at = Column(String, server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    empresa = relationship("Empresa", back_populates="taxis")
    conductor = relationship("Usuario", back_populates="taxis")
    mantenimientos = relationship("Mantenimiento", back_populates="taxi")


class ConductorActual(Base):
    __tablename__ = "conductor_actual"

    id_conductor_actual = Column(Integer, primary_key=True, autoincrement=True)
    id_conductor = Column(Integer, ForeignKey("usuarios.id_usuario"))
    id_taxi = Column(Integer, ForeignKey("taxis.id_taxi"))
    fecha = Column(Date, nullable=False)
    created_at = Column(String, server_default=func.now(), nullable=False)
    updated_at = Column(String, server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    conductor = relationship("Usuario", back_populates="taxis")
    taxi = relationship("Taxi", back_populates="conductor_actual")


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
    estado = Column(Boolean, default=True)
    created_at = Column(String, server_default=func.now(), nullable=False)
    updated_at = Column(String, server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    conductor = relationship("Usuario", back_populates="pagos")


class Reporte(Base):
    __tablename__ = "reportes"

    id_reporte = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(Date, nullable=False)
    ingresos = Column(Integer, nullable=False)
    gastos = Column(Integer, nullable=False)
    empresa = Column(Integer, ForeignKey("empresas.id_empresa"))
    created_at = Column(String, server_default=func.now(), nullable=False)
    updated_at = Column(String, server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    empresa = relationship("Empresa", back_populates="reportes")


class reporteTaxi(Base):
    __tablename__ = "reporte_taxi"

    id_reporte_taxi = Column(Integer, primary_key=True, autoincrement=True)
    id_taxi = Column(Integer, ForeignKey("taxis.id_taxi"))
    descripcion = Column(String(155), nullable=False)
    created_at = Column(String, server_default=func.now(), nullable=False)
    updated_at = Column(String, server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    taxi = relationship("Taxi", back_populates="reporte_taxi")


class ConfiguracionPlan(Base):
    __tablename__ = "configuracion_plan"

    id_configuracion_plan = Column(
        Integer, primary_key=True, autoincrement=True)
    cantidad_taxi = Column(Integer, nullable=False, default=100)
    cantidad_conductor = Column(Integer, nullable=False, default=100)
    cantidad_secretaria = Column(Integer, nullable=False, default=1)
    precio = Column(Integer, nullable=False)
    fecha_inicio = Column(Date, nullable=False, server_default=func.now())
    fecha_fin = Column(Date, nullable=False)
    estado = Column(Boolean, default=True)
    empresa = Column(Integer, ForeignKey("empresas.id_empresa"))
    created_at = Column(String, server_default=func.now(), nullable=False)
    updated_at = Column(String, server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    empresa = relationship("Empresa", back_populates="configuracion_plan")
    configuracion_app = relationship(
        "ConfiguracionApp", back_populates="configuracion_plan")


class configuracionApp(Base):
    __tablename__ = "configuracion_app"

    id_configuracion = Column(Integer, primary_key=True, autoincrement=True)
    plan = Column(Enum("Basico", "Premium", "Personalizado"),
                  nullable=False, default="Basico")
    configuracion_plan = Column(Integer, ForeignKey(
        "configuracion_plan.id_configuracion_plan"))
    empresa = Column(Integer, ForeignKey("empresas.id_empresa"))
    created_at = Column(String, server_default=func.now(), nullable=False)
    updated_at = Column(String, server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    configuracion_plan = relationship(
        "ConfiguracionPlan", back_populates="configuracion_app")
    empresa = relationship("Empresa", back_populates="configuracion_app")
