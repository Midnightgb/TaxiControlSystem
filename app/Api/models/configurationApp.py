#Api/models/ConfigurationApp.py
from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from Api.models.base_class import Base
from Api.models import Empresa,ConfiguracionPlan


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