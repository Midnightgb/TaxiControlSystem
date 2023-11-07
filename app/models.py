from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Float, Date, Boolean, Time
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum

Base = declarative_base()

class Rol(PyEnum):
    Administrador = "Administrador"
    Conductor = "Conductor"

class Estado(PyEnum):
    Activo = "Activo"
    Inactivo = "Inactivo"

class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    cedula = Column(Integer, nullable=False, unique=True)
    nombre = Column(String(45), nullable=False)
    apellido = Column(String(45), nullable=False)
    correo = Column(String(45))
    contrasena = Column(String(45))
    rol = Column(Enum(Rol), nullable=False)
    estado = Column(Enum(Estado), nullable=False)
    created_at = Column(String, server_default=func.now(), nullable=False)
    updated_at = Column(String, server_default=func.now(), onupdate=func.now(), nullable=False)

class Taxi(Base):
    __tablename__ = "taxis"

    id_taxi = Column(Integer, primary_key=True, autoincrement=True)
    id_conductor = Column(Integer, ForeignKey("usuarios.id_usuario"))
    placa = Column(String(6), nullable=False, unique=True)
    modelo = Column(String(45), nullable=False)
    marca = Column(String(45), nullable=False)
    fecha_adquisicion = Column(Date)
    created_at = Column(String, server_default=func.now(), nullable=False)
    updated_at = Column(String, server_default=func.now(), onupdate=func.now(), nullable=False)

    conductor = relationship("Usuario", back_populates="taxis")

class Mantenimiento(Base):
    __tablename__ = "mantenimientos"

    id_mantenimiento = Column(Integer, primary_key=True, autoincrement=True)
    id_taxi = Column(Integer, ForeignKey("taxis.id_taxi"))
    fecha = Column(Date, nullable=False)
    descripcion = Column(String(155), nullable=False)
    costo = Column(Integer, nullable=False)
    created_at = Column(String, server_default=func.now(), nullable=False)
    updated_at = Column(String, server_default=func.now(), onupdate=func.now(), nullable=False)

    taxi = relationship("Taxi", back_populates="mantenimientos")





""" 
CREATE DATABASE IF NOT EXISTS `taxicontrolsystem`;
USE `taxicontrolsystem`;

CREATE TABLE `usuarios` (
  `id_usuario` INT NOT NULL AUTO_INCREMENT,
  `cedula` INT NOT NULL UNIQUE,
  `nombre` VARCHAR(45) NOT NULL,
  `apellido` VARCHAR(45) NOT NULL,
  `correo` VARCHAR(45),
  `contrasena` VARCHAR(45),
  `rol` enum('Administrador','Conductor') NOT NULL,
  `estado` enum('Activo','Inactivo') DEFAULT 'Activo' NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `taxis` (
  `id_taxi` INT NOT NULL AUTO_INCREMENT,
  `id_conductor` INT,
  `placa` VARCHAR(6) NOT NULL UNIQUE,
  `modelo` VARCHAR(45) NOT NULL,
  `marca` VARCHAR(45) NOT NULL,
  `fecha_adquisicion` DATE,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_taxi`),
  FOREIGN KEY (`id_conductor`) REFERENCES `usuarios`(`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `mantenimientos` (
  `id_mantenimiento` INT NOT NULL AUTO_INCREMENT,
  `id_taxi` INT NOT NULL,
  `fecha` DATE NOT NULL,
  `descripcion` VARCHAR(155) NOT NULL,
  `costo` INT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_mantenimiento`),
  FOREIGN KEY (`id_taxi`) REFERENCES `taxis`(`id_taxi`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;  

CREATE TABLE `pagos` (
  `id_pago` INT NOT NULL AUTO_INCREMENT,
  `id_conductor` INT NOT NULL,
  `fecha` DATE NOT NULL,
  `valor` INT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_pago`),
  FOREIGN KEY (`id_conductor`) REFERENCES `usuarios`(`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `reportes` (
  `id_reporte` INT NOT NULL AUTO_INCREMENT,
  `id_conductor` INT NOT NULL,
  `fecha` DATE NOT NULL,
  `ingresos` INT NOT NULL,
  `gastos` INT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_reporte`),
  FOREIGN KEY (`id_conductor`) REFERENCES `usuarios`(`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
 """