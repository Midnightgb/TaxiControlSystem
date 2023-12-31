from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Date, Boolean,BLOB
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


class TipoCombustible(PyEnum):
    Gasolina = "Gasolina"
    Ambos = "Ambos"
    Gas = "Gas"


class Plan(PyEnum):
    Basico = "Basico"
    Premium = "Premium"
    Personalizado = "Personalizado"


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    cedula = Column(String(150), nullable=False)
    nombre = Column(String(45), nullable=False)
    apellido = Column(String(45), nullable=False)
    correo = Column(String(45))
    contrasena = Column(String(250))
    rol = Column(Enum(Rol), nullable=False)
    estado = Column(Enum(Estado), nullable=False)
    created_at = Column(String, server_default=func.now(), nullable=False)
    updated_at = Column(String, server_default=func.now(),
                        onupdate=func.now(), nullable=False)
    empresa_id  = Column(Integer, ForeignKey("empresas.id_empresa"))
    foto = Column(BLOB, default=None)

    empresa = relationship("Empresa", back_populates="usuarios")
    taxis = relationship("ConductorActual", back_populates="conductor")
    pagos = relationship("Pago", back_populates="conductor")
    notificaciones = relationship("Notificaciones", back_populates="usuario")

class Notificaciones(Base):
    __tablename__ = "notificaciones"

    id_mensaje = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False) #MODIFICAR DB XAMMP
    mensaje = Column(String(255), nullable=False)
    fecha_envio = Column(String, server_default=func.now(), nullable=False)
    hora_envio = Column(String, server_default=func.now(), nullable=False) #MODIFICAR DB XAMMP

    usuario = relationship("Usuario", back_populates="notificaciones")


class Taxi(Base):
    __tablename__ = "taxis"

    id_taxi = Column(Integer, primary_key=True, autoincrement=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id_empresa"))
    placa = Column(String(6), nullable=False, unique=True)
    modelo = Column(String(45), nullable=False)
    marca = Column(String(45), nullable=False)
    matricula = Column(String(6), nullable=False)
    tipo_combustible = Column(Enum(TipoCombustible), nullable=False)
    cuota_diaria = Column(Integer, nullable=False)
    fecha_adquisicion = Column(String, server_default=func.now(), nullable=False)
    created_at = Column(String, server_default=func.now(), nullable=False)
    updated_at = Column(String, server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    empresa = relationship("Empresa", back_populates="taxis")
    mantenimientos = relationship("Mantenimiento", back_populates="taxi")
    conductor_actual = relationship("ConductorActual", back_populates="taxi")
    reporte_taxi = relationship("reporteTaxi", back_populates="taxi")
    
class ConductorActual(Base):
    __tablename__ = "conductor_actual"

    id_conductor_actual = Column(Integer, primary_key=True, autoincrement=True)
    id_conductor = Column(Integer, ForeignKey("usuarios.id_usuario"))
    id_taxi = Column(Integer, ForeignKey("taxis.id_taxi"))
    fecha = Column(String, server_default=func.now(), nullable=False)
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
    estado = Column(Boolean, nullable=False)
    cuota_diaria_registrada = Column(Boolean, default=False)
    created_at = Column(String, server_default=func.now(), nullable=False)
    updated_at = Column(String, server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    conductor = relationship("Usuario", back_populates="pagos")


class Reporte(Base):
    __tablename__ = "reportes"

    id_reporte = Column(Integer, primary_key=True, autoincrement=True)
    ingresos = Column(Integer, nullable=False)
    gastos = Column(Integer, nullable=False)
    empresa_id = Column(Integer, ForeignKey("empresas.id_empresa"))
    fecha = Column(Date, nullable=False)
    created_at = Column(String, server_default=func.now(), nullable=False)
    updated_at = Column(String, server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    empresa = relationship("Empresa", back_populates="reportes")


class reporteTaxi(Base):
    __tablename__ = "reporte_taxis"

    id_reporte_taxi = Column(Integer, primary_key=True, autoincrement=True)
    id_taxi = Column(Integer, ForeignKey("taxis.id_taxi"))
    descripcion = Column(String(155), nullable=False)
    created_at = Column(String, server_default=func.now(), nullable=False)
    updated_at = Column(String, server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    taxi = relationship("Taxi", back_populates="reporte_taxi")

class ConfiguracionApp(Base):
    __tablename__ = "configuracion_app"

    id_configuracion = Column(Integer, primary_key=True, autoincrement=True)
    plan = Column(Enum(Plan),
                  nullable=False, default="Basico")
    configuracion_plan_id = Column(Integer, ForeignKey(
        "configuracion_plan.id_configuracion_plan"))
    empresa_id = Column(Integer, ForeignKey("empresas.id_empresa"))
    created_at = Column(String, server_default=func.now(), nullable=False)
    updated_at = Column(String, server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    configuracion_plan = relationship(
        "ConfiguracionPlan", back_populates="configuracion_app")
    empresa = relationship("Empresa", back_populates="configuracion_app")

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
    empresa_id = Column(Integer, ForeignKey("empresas.id_empresa"))
    created_at = Column(String, server_default=func.now(), nullable=False)
    updated_at = Column(String, server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    empresa = relationship("Empresa", back_populates="configuracion_plan")
    configuracion_app = relationship(
        "ConfiguracionApp", back_populates="configuracion_plan")

class Empresa(Base):
        __tablename__ = "empresas"

        id_empresa = Column(Integer, primary_key=True, autoincrement=True)
        nombre = Column(String(100), nullable=False)
        direccion = Column(String(100), nullable=False)
        telefono = Column(String(15), nullable=False)
        correo = Column(String(100), nullable=False)
        created_at = Column(String, server_default=func.now(), nullable=False)
        updated_at = Column(String, server_default=func.now(),
                            onupdate=func.now(), nullable=False)

        taxis = relationship("Taxi", back_populates="empresa")
        reportes = relationship("Reporte", back_populates="empresa")
        configuracion_plan = relationship(
            "ConfiguracionPlan", back_populates="empresa")
        configuracion_app = relationship(
            "ConfiguracionApp", back_populates="empresa")
        usuarios = relationship("Usuario", back_populates="empresa")