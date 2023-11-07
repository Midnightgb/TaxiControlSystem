CREATE DATABASE IF NOT EXISTS `taxicontrolsystem`;
USE `taxicontrolsystem`;

CREATE TABLE `empresa` (
  `id_empresa` INT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(45) NOT NULL,
  `direccion` VARCHAR(45) NOT NULL,
  `telefono` VARCHAR(45) NOT NULL,
  `correo` VARCHAR(45) NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_empresa`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `usuarios` (
  `id_usuario` INT NOT NULL AUTO_INCREMENT,
  `cedula` INT NOT NULL UNIQUE,
  `nombre` VARCHAR(45) NOT NULL,
  `apellido` VARCHAR(45) NOT NULL,
  `correo` VARCHAR(45),
  `contrasena` VARCHAR(45),
  `rol` enum('Administrador','Conductor','Secretaria') NOT NULL,
  `estado` enum('Activo','Inactivo') DEFAULT 'Activo' NOT NULL,
  `empresa` INT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_usuario`),
  FOREIGN KEY (`empresa`) REFERENCES `empresa`(`id_empresa`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `taxis` (
  `id_taxi` INT NOT NULL AUTO_INCREMENT,
  `empresa` INT NOT NULL,
  `placa` VARCHAR(6) NOT NULL UNIQUE,
  `modelo` VARCHAR(45) NOT NULL,
  `marca` VARCHAR(45) NOT NULL,
  `tipo_commbustible` enum('Gasolina','Ambos','Gas') NOT NULL,
  `cuota_diaria` INT NOT NULL,
  `fecha_adquisicion` DATE,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_taxi`),
  FOREIGN KEY (`empresa`) REFERENCES `empresa`(`id_empresa`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `conductor_actual` (
  `id_conductor_actual` INT NOT NULL AUTO_INCREMENT,
  `id_conductor` INT NOT NULL,
  `id_taxi` INT NOT NULL,
  `fecha` DATE NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_conductor_actual`),
  FOREIGN KEY (`id_taxi`) REFERENCES `taxis`(`id_taxi`),
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
  `estado` BOOLEAN DEFAULT true
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_pago`),
  FOREIGN KEY (`id_conductor`) REFERENCES `usuarios`(`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `reportes` (
  `id_reporte` INT NOT NULL AUTO_INCREMENT,
  `ingresos` INT NOT NULL,
  `gastos` INT NOT NULL,
  `empresa` INT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_reporte`),
  FOREIGN KEY (`empresa`) REFERENCES `empresa`(`id_empresa`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `reporte_taxi` (
  `id_reporte_taxi` INT NOT NULL AUTO_INCREMENT,
  `id_taxi` INT NOT NULL,
  `descripcion` TEXT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_reporte_taxi`),
  FOREIGN KEY (`id_taxi`) REFERENCES `taxis`(`id_taxi`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `configuracion_app` (
  `id_configuracion` INT NOT NULL AUTO_INCREMENT,
  `plan` enum('Basico','Premium', 'Personalizado') NOT NULL DEFAULT 'Basico',
  `configuracion_plan` INT NOT NULL,
  `empresa` INT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_configuracion`),
  FOREIGN KEY (`configuracion_plan`) REFERENCES `configuracion_plan`(`id_configuracion_plan`),
  FOREIGN KEY (`empresa`) REFERENCES `empresa`(`id_empresa`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `configuracion_plan` (
  `id_configuracion_plan` INT NOT NULL AUTO_INCREMENT,
  `cantidad_taxi` INT NOT NULL DEFAULT 100,
  `cantidad_conductor` INT NOT NULL DEFAULT 100,
  `cantidad_secretaria` INT NOT NULL DEFAULT 1,
  `precio` INT NOT NULL,
  `fecha_inicio` DATE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_fin` DATE NOT NULL,
  `estado` BOOLEAN DEFAULT true,
  `empresa` INT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_configuracion_plan`),
  FOREIGN KEY (`empresa`) REFERENCES `empresa`(`id_empresa`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;