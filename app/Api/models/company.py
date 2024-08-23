# Api/models/company.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from Api.models.base_class import Base
from Api.models import Taxi
from Api.models import Usuario
from Api.models import Reporte
from Api.models import ConfiguracionPlan,ConfiguracionApp


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

        