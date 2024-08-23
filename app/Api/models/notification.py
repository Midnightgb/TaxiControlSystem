#Api/models/notification.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from Api.models.base_class import Base
from Api.models import Usuario

class Notificaciones(Base):
    __tablename__ = "notificaciones"

    id_mensaje = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False) #MODIFICAR DB XAMMP
    mensaje = Column(String(255), nullable=False)
    fecha_envio = Column(String, server_default=func.now(), nullable=False)
    hora_envio = Column(String, server_default=func.now(), nullable=False) #MODIFICAR DB XAMMP

    usuario = relationship("Usuario", back_populates="notificaciones")