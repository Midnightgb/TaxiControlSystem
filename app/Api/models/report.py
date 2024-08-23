#Api/models/report.py
from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from Api.models.base_class import Base
from Api.models import Empresa

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