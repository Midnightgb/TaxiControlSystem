-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Dec 02, 2023 at 03:35 AM
-- Server version: 10.4.28-MariaDB
-- PHP Version: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `taxicontrolsystem`
--
CREATE DATABASE IF NOT EXISTS `taxicontrolsystem` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `taxicontrolsystem`;

-- --------------------------------------------------------

--
-- Table structure for table `conductor_actual`
--

CREATE TABLE `conductor_actual` (
  `id_conductor_actual` int(11) NOT NULL,
  `id_conductor` int(11) NOT NULL,
  `id_taxi` int(11) NOT NULL,
  `fecha` date NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `configuracion_app`
--

CREATE TABLE `configuracion_app` (
  `id_configuracion` int(11) NOT NULL,
  `plan` enum('Basico','Premium','Personalizado') NOT NULL DEFAULT 'Basico',
  `configuracion_plan_id` int(11) NOT NULL,
  `empresa` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `configuracion_plan`
--

CREATE TABLE `configuracion_plan` (
  `id_configuracion_plan` int(11) NOT NULL,
  `cantidad_taxi` int(11) NOT NULL DEFAULT 100,
  `cantidad_conductor` int(11) NOT NULL DEFAULT 100,
  `cantidad_secretaria` int(11) NOT NULL DEFAULT 1,
  `precio` int(11) NOT NULL,
  `fecha_inicio` date NOT NULL DEFAULT current_timestamp(),
  `fecha_fin` date NOT NULL,
  `estado` tinyint(1) DEFAULT 1,
  `empresa_id` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `empresas`
--

CREATE TABLE `empresas` (
  `id_empresa` int(11) NOT NULL,
  `nombre` varchar(45) NOT NULL,
  `direccion` varchar(45) NOT NULL,
  `telefono` varchar(45) NOT NULL,
  `correo` varchar(45) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `mantenimientos`
--

CREATE TABLE `mantenimientos` (
  `id_mantenimiento` int(11) NOT NULL,
  `id_taxi` int(11) NOT NULL,
  `fecha` date NOT NULL,
  `descripcion` varchar(155) NOT NULL,
  `costo` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `notificaciones`
--

CREATE TABLE `notificaciones` (
  `id_mensaje` int(11) NOT NULL,
  `id_secretaria` int(11) DEFAULT NULL,
  `mensaje` varchar(255) NOT NULL,
  `fecha_envio` date DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `pagos`
--

CREATE TABLE `pagos` (
  `id_pago` int(11) NOT NULL,
  `id_conductor` int(11) NOT NULL,
  `fecha` date NOT NULL,
  `valor` int(11) NOT NULL,
  `estado` tinyint(1) DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `cuota_diaria_registrada` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `reportes`
--

CREATE TABLE `reportes` (
  `id_reporte` int(11) NOT NULL,
  `ingresos` int(11) NOT NULL,
  `gastos` int(11) NOT NULL,
  `empresa_id` int(11) NOT NULL,
  `fecha` date DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `reporte_taxis`
--

CREATE TABLE `reporte_taxis` (
  `id_reporte_taxi` int(11) NOT NULL,
  `id_taxi` int(11) NOT NULL,
  `descripcion` text NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `taxis`
--

CREATE TABLE `taxis` (
  `id_taxi` int(11) NOT NULL,
  `empresa_id` int(11) NOT NULL,
  `placa` varchar(6) NOT NULL,
  `matricula` varchar(6) NOT NULL,
  `modelo` varchar(45) NOT NULL,
  `marca` varchar(45) NOT NULL,
  `tipo_combustible` enum('Gasolina','Ambos','Gas') NOT NULL,
  `cuota_diaria` int(11) NOT NULL,
  `fecha_adquisicion` date DEFAULT current_timestamp(),
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `usuarios`
--

CREATE TABLE `usuarios` (
  `id_usuario` int(11) NOT NULL,
  `cedula` int(11) NOT NULL,
  `nombre` varchar(45) NOT NULL,
  `apellido` varchar(45) NOT NULL,
  `correo` varchar(45) DEFAULT NULL,
  `contrasena` varchar(250) DEFAULT NULL,
  `rol` enum('Administrador','Conductor','Secretaria') NOT NULL,
  `estado` enum('Activo','Inactivo') NOT NULL DEFAULT 'Activo',
  `foto` longblob DEFAULT NULL,
  `empresa_id` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `conductor_actual`
--
ALTER TABLE `conductor_actual`
  ADD PRIMARY KEY (`id_conductor_actual`),
  ADD KEY `id_taxi` (`id_taxi`),
  ADD KEY `id_conductor` (`id_conductor`);

--
-- Indexes for table `configuracion_app`
--
ALTER TABLE `configuracion_app`
  ADD PRIMARY KEY (`id_configuracion`),
  ADD KEY `configuracion_plan_id` (`configuracion_plan_id`),
  ADD KEY `empresa` (`empresa`);

--
-- Indexes for table `configuracion_plan`
--
ALTER TABLE `configuracion_plan`
  ADD PRIMARY KEY (`id_configuracion_plan`),
  ADD KEY `empresa_id` (`empresa_id`);

--
-- Indexes for table `empresas`
--
ALTER TABLE `empresas`
  ADD PRIMARY KEY (`id_empresa`);

--
-- Indexes for table `mantenimientos`
--
ALTER TABLE `mantenimientos`
  ADD PRIMARY KEY (`id_mantenimiento`),
  ADD KEY `id_taxi` (`id_taxi`);

--
-- Indexes for table `notificaciones`
--
ALTER TABLE `notificaciones`
  ADD PRIMARY KEY (`id_mensaje`),
  ADD KEY `id_secretaria` (`id_secretaria`);

--
-- Indexes for table `pagos`
--
ALTER TABLE `pagos`
  ADD PRIMARY KEY (`id_pago`),
  ADD KEY `id_conductor` (`id_conductor`);

--
-- Indexes for table `reportes`
--
ALTER TABLE `reportes`
  ADD PRIMARY KEY (`id_reporte`),
  ADD KEY `empresa_id` (`empresa_id`);

--
-- Indexes for table `reporte_taxis`
--
ALTER TABLE `reporte_taxis`
  ADD PRIMARY KEY (`id_reporte_taxi`),
  ADD KEY `id_taxi` (`id_taxi`);

--
-- Indexes for table `taxis`
--
ALTER TABLE `taxis`
  ADD PRIMARY KEY (`id_taxi`),
  ADD UNIQUE KEY `placa` (`placa`),
  ADD KEY `empresa_id` (`empresa_id`);

--
-- Indexes for table `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id_usuario`),
  ADD UNIQUE KEY `cedula` (`cedula`),
  ADD KEY `empresa_id` (`empresa_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `conductor_actual`
--
ALTER TABLE `conductor_actual`
  MODIFY `id_conductor_actual` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `configuracion_app`
--
ALTER TABLE `configuracion_app`
  MODIFY `id_configuracion` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `configuracion_plan`
--
ALTER TABLE `configuracion_plan`
  MODIFY `id_configuracion_plan` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `empresas`
--
ALTER TABLE `empresas`
  MODIFY `id_empresa` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `mantenimientos`
--
ALTER TABLE `mantenimientos`
  MODIFY `id_mantenimiento` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `notificaciones`
--
ALTER TABLE `notificaciones`
  MODIFY `id_mensaje` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `pagos`
--
ALTER TABLE `pagos`
  MODIFY `id_pago` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `reportes`
--
ALTER TABLE `reportes`
  MODIFY `id_reporte` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `reporte_taxis`
--
ALTER TABLE `reporte_taxis`
  MODIFY `id_reporte_taxi` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `taxis`
--
ALTER TABLE `taxis`
  MODIFY `id_taxi` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id_usuario` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `conductor_actual`
--
ALTER TABLE `conductor_actual`
  ADD CONSTRAINT `conductor_actual_ibfk_1` FOREIGN KEY (`id_taxi`) REFERENCES `taxis` (`id_taxi`),
  ADD CONSTRAINT `conductor_actual_ibfk_2` FOREIGN KEY (`id_conductor`) REFERENCES `usuarios` (`id_usuario`);

--
-- Constraints for table `configuracion_app`
--
ALTER TABLE `configuracion_app`
  ADD CONSTRAINT `configuracion_app_ibfk_1` FOREIGN KEY (`configuracion_plan_id`) REFERENCES `configuracion_plan` (`id_configuracion_plan`),
  ADD CONSTRAINT `configuracion_app_ibfk_2` FOREIGN KEY (`empresa`) REFERENCES `empresas` (`id_empresa`);

--
-- Constraints for table `configuracion_plan`
--
ALTER TABLE `configuracion_plan`
  ADD CONSTRAINT `configuracion_plan_ibfk_1` FOREIGN KEY (`empresa_id`) REFERENCES `empresas` (`id_empresa`);

--
-- Constraints for table `mantenimientos`
--
ALTER TABLE `mantenimientos`
  ADD CONSTRAINT `mantenimientos_ibfk_1` FOREIGN KEY (`id_taxi`) REFERENCES `taxis` (`id_taxi`);

--
-- Constraints for table `notificaciones`
--
ALTER TABLE `notificaciones`
  ADD CONSTRAINT `notificaciones_ibfk_1` FOREIGN KEY (`id_secretaria`) REFERENCES `usuarios` (`id_usuario`);

--
-- Constraints for table `pagos`
--
ALTER TABLE `pagos`
  ADD CONSTRAINT `pagos_ibfk_1` FOREIGN KEY (`id_conductor`) REFERENCES `usuarios` (`id_usuario`);

--
-- Constraints for table `reportes`
--
ALTER TABLE `reportes`
  ADD CONSTRAINT `reportes_ibfk_1` FOREIGN KEY (`empresa_id`) REFERENCES `empresas` (`id_empresa`);

--
-- Constraints for table `reporte_taxis`
--
ALTER TABLE `reporte_taxis`
  ADD CONSTRAINT `reporte_taxis_ibfk_1` FOREIGN KEY (`id_taxi`) REFERENCES `taxis` (`id_taxi`);

--
-- Constraints for table `taxis`
--
ALTER TABLE `taxis`
  ADD CONSTRAINT `taxis_ibfk_1` FOREIGN KEY (`empresa_id`) REFERENCES `empresas` (`id_empresa`);

--
-- Constraints for table `usuarios`
--
ALTER TABLE `usuarios`
  ADD CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`empresa_id`) REFERENCES `empresas` (`id_empresa`);

DELIMITER $$
--
-- Events
--
CREATE DEFINER=`root`@`localhost` EVENT `generar_reportes_mensuales` ON SCHEDULE EVERY 1 MONTH STARTS '2023-11-01 07:19:00' ON COMPLETION NOT PRESERVE ENABLE DO BEGIN
    DECLARE empresa_id_cursor INT;
    DECLARE done BOOLEAN DEFAULT FALSE;
    DECLARE empresas_cursor CURSOR FOR SELECT id_empresa FROM empresas;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    OPEN empresas_cursor;

    read_loop: LOOP
        FETCH empresas_cursor INTO empresa_id_cursor;

        IF done THEN
            LEAVE read_loop;
        END IF;

        INSERT INTO reportes (ingresos, gastos, empresa_id, fecha)
VALUES (0, 0, empresa_id_cursor, DATE_FORMAT(CURRENT_DATE, '%Y-%m-01'));

    END LOOP;

    CLOSE empresas_cursor;
END$$

DELIMITER ;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
