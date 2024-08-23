#Api/models/currentdriver.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from Api.models.base_class import Base
from Api.models import Usuario,Taxi


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