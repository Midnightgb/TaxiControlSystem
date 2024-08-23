#Api/models/maintenance.py
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from Api.models.base_class import Base,Taxi

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