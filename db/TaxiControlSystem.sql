CREATE DATABASE IF NOT EXISTS `taxicontrolsystem`;
USE `taxicontrolsystem`;

CREATE TABLE `empresas` (
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
  `contrasena` VARCHAR(250),
  `rol` enum('Administrador','Conductor','Secretaria') NOT NULL,
  `estado` enum('Activo','Inactivo') DEFAULT 'Activo' NOT NULL,
  `foto` LONGBLOB DEFAULT NULL,
  `empresa_id` INT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_usuario`),
  FOREIGN KEY (`empresa_id`) REFERENCES `empresas`(`id_empresa`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `taxis` (
  `id_taxi` INT NOT NULL AUTO_INCREMENT,
  `empresa_id` INT NOT NULL,
  `placa` VARCHAR(6) NOT NULL UNIQUE,
  `modelo` VARCHAR(45) NOT NULL,
  `marca` VARCHAR(45) NOT NULL,
  `matricula` VARCHAR(6) NOT NULL,
  `tipo_combustible` enum('Gasolina','Ambos','Gas') NOT NULL,
  `cuota_diaria` INT NOT NULL,
  `fecha_adquisicion` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_taxi`),
  FOREIGN KEY (`empresa_id`) REFERENCES `empresas`(`id_empresa`)
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
  `estado` BOOLEAN DEFAULT true,
  `cuota_diaria_registrada` BOOLEAN DEFAULT false,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_pago`),
  FOREIGN KEY (`id_conductor`) REFERENCES `usuarios`(`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `reportes` (
  `id_reporte` INT NOT NULL AUTO_INCREMENT,
  `ingresos` INT NOT NULL,
  `gastos` INT NOT NULL,
  `empresa_id` INT NOT NULL,
  `fecha` DATE DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_reporte`),
  FOREIGN KEY (`empresa_id`) REFERENCES `empresas`(`id_empresa`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `reporte_taxis` (
  `id_reporte_taxi` INT NOT NULL AUTO_INCREMENT,
  `id_taxi` INT NOT NULL,
  `descripcion` TEXT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_reporte_taxi`),
  FOREIGN KEY (`id_taxi`) REFERENCES `taxis`(`id_taxi`)
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
  `empresa_id` INT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_configuracion_plan`),
  FOREIGN KEY (`empresa_id`) REFERENCES `empresas`(`id_empresa`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `configuracion_app` (
  `id_configuracion` INT NOT NULL AUTO_INCREMENT,
  `plan` enum('Basico','Premium', 'Personalizado') NOT NULL DEFAULT 'Basico',
  `configuracion_plan_id` INT NOT NULL,
  `empresa` INT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_configuracion`),
  FOREIGN KEY (`configuracion_plan_id`) REFERENCES `configuracion_plan`(`id_configuracion_plan`),
  FOREIGN KEY (`empresa`) REFERENCES `empresas`(`id_empresa`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;



/* password to test: $2y$10$.LoHrb62oXUyoTUp8HXj/eGZA7GG0kk5tFQi08kFA0/l5l20LMNai */
/* 777 */