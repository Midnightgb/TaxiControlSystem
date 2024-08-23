#Api/models/pyment.py
from sqlalchemy import Column, Integer, Date, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from Api.models.base_class import Base, Usuario

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