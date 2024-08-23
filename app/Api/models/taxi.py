#Api/models/taxi.py
from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from Api.models.base_class import Base
from Api.models import Empresa, reporteTaxi, Mantenimiento, ConductorActual

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