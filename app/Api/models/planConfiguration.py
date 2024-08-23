#Api/models/planConfiguration.py
from sqlalchemy import Column, Integer, Date, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from Api.models.base_class import Base
from Api.models import Empresa, ConfiguracionApp


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