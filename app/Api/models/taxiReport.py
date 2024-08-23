#Api/models/taxireport.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from Api.models.base_class import Base
from Api.models import Taxi

class reporteTaxi(Base):
    __tablename__ = "reporte_taxis"

    id_reporte_taxi = Column(Integer, primary_key=True, autoincrement=True)
    id_taxi = Column(Integer, ForeignKey("taxis.id_taxi"))
    descripcion = Column(String(155), nullable=False)
    created_at = Column(String, server_default=func.now(), nullable=False)
    updated_at = Column(String, server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    taxi = relationship("Taxi", back_populates="reporte_taxi")