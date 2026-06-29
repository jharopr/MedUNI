-- =======================
-- TABLAS
-- =======================

CREATE TABLE estudiantes (
    id SERIAL PRIMARY KEY,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    codigo_estudiante VARCHAR(100) UNIQUE NOT NULL,
    codigo_dirce VARCHAR(100) NOT NULL,
    estado BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE especialidades (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    estado BOOLEAN DEFAULT true
);

CREATE TABLE medicos (
    id SERIAL PRIMARY KEY,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    especialidad_id INT NOT NULL REFERENCES especialidades(id),
    estado BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE citas (
    id SERIAL PRIMARY KEY,
    estudiante_id INT NOT NULL REFERENCES estudiantes(id),
    medico_id INT NOT NULL REFERENCES medicos(id),
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    estado VARCHAR(20) DEFAULT 'reservada' CHECK (estado IN ('reservada', 'cancelada', 'atendida', 'no_asistio')),
    especialidad_id INT NOT NULL REFERENCES especialidades(id),
    hora_cita TIMESTAMP, -- Timestamp de cuando se programó la cita
    hora_atencion TIMESTAMP, -- Timestamp de cuando se atendió realmente
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Para calcular tiempo de ciclo de admisión
    reserva_confirmada_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX uq_cita_medico_horario_reservada
ON citas (medico_id, fecha, hora)
WHERE estado = 'reservada';

CREATE TABLE disponibilidad_especialidad (
    id SERIAL PRIMARY KEY,
    especialidad_id INT NOT NULL REFERENCES especialidades(id),
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    dia_semana INT NOT NULL, -- ejemplo: [1,2,3,4,5] = lunes a viernes
    disponibilidad BOOLEAN NOT NULL DEFAULT TRUE,
    duracion_turno INT NOT NULL DEFAULT 30 --minutos por turno
);

CREATE TABLE horario_medico (
    id SERIAL PRIMARY KEY,
    medico_id INT NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    dia_semana INT NOT NULL, -- 1=Lunes ... 7=Domingo
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    FOREIGN KEY (medico_id) REFERENCES medicos(id)
);

CREATE TABLE administradores (
    id SERIAL PRIMARY KEY,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    estado BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE personal_topico (
    id SERIAL PRIMARY KEY,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    estado BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE calificaciones (
    id SERIAL PRIMARY KEY,
    cita_id INT NOT NULL UNIQUE REFERENCES citas(id),
    calificacion INT NOT NULL CHECK (calificacion >= 1 AND calificacion <= 5),
    comentario TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE registro_atencion (
    id SERIAL PRIMARY KEY,
    cita_id INT NOT NULL UNIQUE REFERENCES citas(id),
    hora_llegada TIMESTAMP,
    hora_triaje TIMESTAMP,
    hora_inicio TIMESTAMP,
    hora_fin TIMESTAMP,
    estado_atencion VARCHAR(30) DEFAULT 'en_espera' CHECK (estado_atencion IN ('en_espera', 'en_triaje', 'en_atencion', 'finalizada', 'no_asistio')),
    observacion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE auditoria (
    id SERIAL PRIMARY KEY,
    usuario_id INT,
    rol VARCHAR(30),
    accion VARCHAR(100) NOT NULL,
    entidad VARCHAR(100) NOT NULL,
    entidad_id INT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    detalle TEXT
);

-- =======================
-- DATOS
-- =======================

INSERT INTO especialidades (nombre) VALUES
('Cirugía General'),
('Cardiología'),
('Ginecología'),
('Urología'),
('Oftalmología'),
('Endocrinología'),
('Psicología'),
('Otorrinolaringología'),
('Odontología'),
('Psiquiatría'),
('Laboratorio Clínico'),
('Neumología'),
('Medicina Interna/Familia/General'),
('Nutrición'),
('Ecografía');

-- Disponibilidad por especialidad (días disponibles)
-- FECHAS ACTUALIZADAS A DICIEMBRE 2025
INSERT INTO disponibilidad_especialidad (especialidad_id, fecha_inicio, fecha_fin, hora_inicio, hora_fin, dia_semana)
VALUES
(1, '2025-12-01', '2025-12-31', '14:00', '20:00', 2),
(1, '2025-12-01', '2025-12-31', '08:00', '14:00', 4);

-- Días no disponibles (COMENTADOS)
INSERT INTO disponibilidad_especialidad (especialidad_id, fecha_inicio, fecha_fin, hora_inicio, hora_fin, dia_semana)
VALUES
(2, '2025-12-01', '2025-12-31', '10:00', '18:00', 4), -- Cardiología: Jueves de 10 a.m. a 6 p.m.
(3, '2025-12-01', '2025-12-31', '08:00', '14:00', 2), -- Ginecología: Martes, Jueves, Viernes
(3, '2025-12-01', '2025-12-31', '08:00', '20:00', 4),
(3, '2025-12-01', '2025-12-31', '08:00', '14:00', 5),
(5, '2025-12-01', '2025-12-31', '08:00', '20:00', 1), -- Oftalmología: Lunes
(6, '2025-12-01', '2025-12-31', '08:00', '20:00', 2), -- Endocrinología: Martes
(7, '2025-12-01', '2025-12-31', '08:00', '20:00', 1), -- Psicología: Lunes a Sábado
(7, '2025-12-01', '2025-12-31', '08:00', '20:00', 2),
(7, '2025-12-01', '2025-12-31', '08:00', '20:00', 3),
(7, '2025-12-01', '2025-12-31', '08:00', '20:00', 4),
(7, '2025-12-01', '2025-12-31', '08:00', '20:00', 5),
(7, '2025-12-01', '2025-12-31', '08:00', '20:00', 6),
(8, '2025-12-01', '2025-12-31', '15:00', '20:00', 4), -- Otorrinolaringología: Jueves (Hora corregida: '15:00')
(9, '2025-12-01', '2025-12-31', '08:00', '20:00', 1), -- Odontología: Lunes a Sábado
(9, '2025-12-01', '2025-12-31', '08:00', '20:00', 2),
(9, '2025-12-01', '2025-12-31', '08:00', '20:00', 3),
(9, '2025-12-01', '2025-12-31', '08:00', '20:00', 4),
(9, '2025-12-01', '2025-12-31', '08:00', '20:00', 5),
(9, '2025-12-01', '2025-12-31', '08:00', '20:00', 6),
(10, '2025-12-01', '2025-12-31', '08:00', '20:00', 1), -- Psiquiatría: Lunes a Sábado
(10, '2025-12-01', '2025-12-31', '10:00', '16:00', 2),
(10, '2025-12-01', '2025-12-31', '10:00', '16:00', 3),
(10, '2025-12-01', '2025-12-31', '10:00', '16:00', 4),
(10, '2025-12-01', '2025-12-31', '10:00', '16:00', 5),
(10, '2025-12-01', '2025-12-31', '10:00', '16:00', 6),
(12, '2025-12-01', '2025-12-31', '14:00', '20:00', 1), -- Neumología: Lunes
(13, '2025-12-01', '2025-12-31', '08:00', '20:00', 1), -- Medicina General: Lunes a Sábado
(13, '2025-12-01', '2025-12-31', '08:00', '20:00', 2),
(13, '2025-12-01', '2025-12-31', '08:00', '20:00', 3),
(13, '2025-12-01', '2025-12-31', '08:00', '20:00', 4),
(13, '2025-12-01', '2025-12-31', '08:00', '20:00', 5),
(13, '2025-12-01', '2025-12-31', '08:00', '20:00', 6),
(14, '2025-12-01', '2025-12-31', '08:00', '14:00', 1), -- Nutrición: Lunes a Jueves, Sábado
(14, '2025-12-01', '2025-12-31', '08:00', '14:00', 2),
(14, '2025-12-01', '2025-12-31', '08:00', '14:00', 3),
(14, '2025-12-01', '2025-12-31', '08:00', '14:00', 4),
(14, '2025-12-01', '2025-12-31', '08:00', '14:00', 6),
(15, '2025-12-01', '2025-12-31', '08:00', '14:00', 1), -- Ecografía: Lunes a Viernes
(15, '2025-12-01', '2025-12-31', '08:00', '14:00', 2),
(15, '2025-12-01', '2025-12-31', '08:00', '14:00', 3),
(15, '2025-12-01', '2025-12-31', '08:00', '14:00', 4),
(15, '2025-12-01', '2025-12-31', '08:00', '14:00', 5);


-- Médicos (SIN CAMBIOS)
INSERT INTO medicos (nombres, apellidos, correo, especialidad_id)
VALUES
-- Cirugía General
('Saldivar', 'Medina', 'saldivar.medina@gmail.com', 1),
('Samuel', 'Gutierrez', 'Samuel.gutierrez@gmail.com', 1),
-- Cardiología
('Ana', 'López', 'ana.lopez@correo.com', 2),
('Ricardo', 'Ramírez', 'ricardo.ramirez@correo.com', 2),

-- Ginecología
('María', 'Hernández', 'maria.hernandez@correo.com', 3),
('Sofía', 'Torres', 'sofia.torres@correo.com', 3),

-- Urología
('Luis', 'Martínez', 'luis.martinez@correo.com', 4),
('Pedro', 'García', 'pedro.garcia@correo.com', 4),

-- Oftalmología
('Laura', 'Sánchez', 'laura.sanchez@correo.com', 5),
('Javier', 'Rodríguez', 'javier.rodriguez@correo.com', 5),

-- Endocrinología
('Ricardo', 'Jiménez', 'ricardo.jimenez@correo.com', 6),
('Elena', 'Pérez', 'elena.perez@correo.com', 6),

-- Psicología
('Beatriz', 'Flores', 'beatriz.flores@correo.com', 7),
('Claudia', 'Gutiérrez', 'claudia.gutierrez@correo.com', 7),

-- Otorrinolaringología
('José', 'Díaz', 'jose.diaz@correo.com', 8),
('Victor', 'Morales', 'victor.morales@correo.com', 8),

-- Odontología
('Andrea', 'Martínez', 'andrea.martinez@correo.com', 9),
('Manuel', 'Luna', 'manuel.luna@correo.com', 9),

-- Psiquiatría
('Lucía', 'Vargas', 'lucia.vargas@correo.com', 10),
('Francisco', 'Serrano', 'francisco.serrano@correo.com', 10),

-- Laboratorio Clínico
('Alejandro', 'Castro', 'alejandro.castro@correo.com', 11),
('Marta', 'Salazar', 'marta.salazar@correo.com', 11),

-- Neumología
('Carlos', 'Jiménez', 'carlos.jimenez@correo.com', 12),
('Paula', 'Ríos', 'paula.rios@correo.com', 12),

-- Medicina Interna/Familia/General
('José', 'González', 'jose.gonzalez@correo.com', 13),
('Isabel', 'López', 'isabel.lopez@correo.com', 13),

-- Nutrición
('Valeria', 'García', 'valeria.garcia@correo.com', 14),
('Raúl', 'Mendoza', 'raul.mendoza@correo.com', 14),

-- Ecografía
('Gabriela', 'Figueroa', 'gabriela.figueroa@correo.com', 15),
('Juan', 'Sánchez', 'juan.sanchez@correo.com', 15);


-- Insertar estudiantes
INSERT INTO estudiantes (nombres, apellidos, correo, codigo_estudiante, codigo_dirce)
VALUES 
('Jharo', 'Paucarcaja Ramos', 'jharolym.paucarcaja.r@uni.pe', '20234044I', '111111'),
('Alexis', 'Garay', 'alexis.g@uni.pe', '20244017D', '111111'),
('Rolly', 'Mamani', 'rolly.m@uni.pe', '20240010E', '111111'),
('María', 'González Pérez', 'maria.gonzalez@uni.pe', '20231001A', '111111'),
('Carlos', 'Rodríguez Silva', 'carlos.rodriguez@uni.pe', '20231002B', '111111'),
('Ana', 'Martínez López', 'ana.martinez@uni.pe', '20231003C', '111111'),
('Luis', 'Fernández Torres', 'luis.fernandez@uni.pe', '20231004D', '111111'),
('Laura', 'Sánchez Díaz', 'laura.sanchez@uni.pe', '20231005E', '111111'),
('Pedro', 'Ramírez Vega', 'pedro.ramirez@uni.pe', '20231006F', '111111'),
('Carmen', 'Morales Ruiz', 'carmen.morales@uni.pe', '20231007G', '111111'),
('Diego', 'Castro Herrera', 'diego.castro@uni.pe', '20231008H', '111111'),
('Sofía', 'Jiménez Vargas', 'sofia.jimenez@uni.pe', '20231009I', '111111'),
('Miguel', 'Torres Mendoza', 'miguel.torres@uni.pe', '20231010J', '111111'),
('Elena', 'García Flores', 'elena.garcia@uni.pe', '20231011K', '111111'),
('Roberto', 'Hernández Ríos', 'roberto.hernandez@uni.pe', '20231012L', '111111'),
('Patricia', 'Luna Campos', 'patricia.luna@uni.pe', '20231013M', '111111'),
('Fernando', 'Ortega Salas', 'fernando.ortega@uni.pe', '20231014N', '111111'),
('Gabriela', 'Mendoza Paredes', 'gabriela.mendoza@uni.pe', '20231015O', '111111'),
('Ricardo', 'Vargas Quiroz', 'ricardo.vargas@uni.pe', '20231016P', '111111'),
('Isabel', 'Cruz Moreno', 'isabel.cruz@uni.pe', '20231017Q', '111111'),
('Jorge', 'Paredes Soto', 'jorge.paredes@uni.pe', '20231018R', '111111'),
('Andrea', 'Soto Delgado', 'andrea.soto@uni.pe', '20231019S', '111111'),
('Daniel', 'Delgado Campos', 'daniel.delgado@uni.pe', '20231020T', '111111'),
('Valeria', 'Moreno Rojas', 'valeria.moreno@uni.pe', '20231021U', '111111'),
('Andrés', 'Rojas Peña', 'andres.rojas@uni.pe', '20231022V', '111111');

-- Insertar administradores
INSERT INTO administradores (nombres, apellidos, correo, username, password)
VALUES 
('Admin', 'Principal', 'admin@uni.pe', 'admin', 'admin123'),
('Administrador', 'Sistema', 'admin.sistema@uni.pe', 'admin_sistema', 'admin123');

INSERT INTO personal_topico (nombres, apellidos, correo, username, password)
VALUES
('Personal', 'Topico', 'topico@uni.pe', 'topico', 'topico123');

-- =======================
-- DATOS FICTICIOS PARA HISTORIAL Y KPIs
-- =======================

-- Horarios de médicos (para calcular ocupación médica)
INSERT INTO horario_medico (medico_id, fecha_inicio, fecha_fin, dia_semana, hora_inicio, hora_fin)
VALUES
-- Médicos con horarios variados en los últimos 6 meses
(1, '2024-06-01', '2025-12-31', 2, '14:00', '20:00'), -- Saldivar - Martes
(1, '2024-06-01', '2025-12-31', 4, '08:00', '14:00'), -- Saldivar - Jueves
(2, '2024-06-01', '2025-12-31', 2, '14:00', '20:00'), -- Samuel - Martes
(2, '2024-06-01', '2025-12-31', 4, '08:00', '14:00'), -- Samuel - Jueves
(3, '2024-06-01', '2025-12-31', 4, '10:00', '18:00'), -- Ana López - Jueves
(4, '2024-06-01', '2025-12-31', 4, '10:00', '18:00'), -- Ricardo - Jueves
(5, '2024-06-01', '2025-12-31', 2, '08:00', '14:00'), -- María - Martes
(5, '2024-06-01', '2025-12-31', 4, '08:00', '20:00'), -- María - Jueves
(5, '2024-06-01', '2025-12-31', 5, '08:00', '14:00'), -- María - Viernes
(7, '2024-06-01', '2025-12-31', 1, '08:00', '20:00'), -- Laura - Lunes
(8, '2024-06-01', '2025-12-31', 1, '08:00', '20:00'), -- Javier - Lunes
(9, '2024-06-01', '2025-12-31', 2, '08:00', '20:00'), -- Ricardo Jiménez - Martes
(10, '2024-06-01', '2025-12-31', 2, '08:00', '20:00'), -- Elena - Martes
(11, '2024-06-01', '2025-12-31', 1, '08:00', '20:00'), -- Beatriz - Lunes a Sábado
(11, '2024-06-01', '2025-12-31', 2, '08:00', '20:00'),
(11, '2024-06-01', '2025-12-31', 3, '08:00', '20:00'),
(11, '2024-06-01', '2025-12-31', 4, '08:00', '20:00'),
(11, '2024-06-01', '2025-12-31', 5, '08:00', '20:00'),
(11, '2024-06-01', '2025-12-31', 6, '08:00', '20:00'),
(13, '2024-06-01', '2025-12-31', 1, '08:00', '20:00'), -- José González - Medicina General
(13, '2024-06-01', '2025-12-31', 2, '08:00', '20:00'),
(13, '2024-06-01', '2025-12-31', 3, '08:00', '20:00'),
(13, '2024-06-01', '2025-12-31', 4, '08:00', '20:00'),
(13, '2024-06-01', '2025-12-31', 5, '08:00', '20:00'),
(13, '2024-06-01', '2025-12-31', 6, '08:00', '20:00'),
(19, '2024-06-01', '2025-12-31', 1, '08:00', '14:00'), -- Valeria - Nutrición
(19, '2024-06-01', '2025-12-31', 2, '08:00', '14:00'),
(19, '2024-06-01', '2025-12-31', 3, '08:00', '14:00'),
(19, '2024-06-01', '2025-12-31', 4, '08:00', '14:00'),
(19, '2024-06-01', '2025-12-31', 6, '08:00', '14:00');

-- Citas pasadas (para historial - canceladas)
-- Citas canceladas en los últimos 6 meses
INSERT INTO citas (estudiante_id, medico_id, fecha, hora, estado, especialidad_id, hora_cita, created_at, reserva_confirmada_at)
VALUES
-- Estudiantes 1-3 (los originales) con citas canceladas
(1, 1, '2024-09-15', '14:30', 'cancelada', 1, '2024-09-15 14:30:00', '2024-09-10 10:15:00', '2024-09-10 10:17:00'),
(1, 3, '2024-10-20', '11:00', 'cancelada', 2, '2024-10-20 11:00:00', '2024-10-15 14:20:00', '2024-10-15 14:22:00'),
(1, 7, '2024-08-22', '15:00', 'cancelada', 4, '2024-08-22 15:00:00', '2024-08-18 11:30:00', '2024-08-18 11:32:00'),
(1, 9, '2024-07-30', '10:30', 'cancelada', 5, '2024-07-30 10:30:00', '2024-07-25 09:15:00', '2024-07-25 09:17:00'),
(2, 2, '2024-09-18', '15:00', 'cancelada', 1, '2024-09-18 15:00:00', '2024-09-12 13:20:00', '2024-09-12 13:22:00'),
(2, 11, '2024-10-25', '14:00', 'cancelada', 7, '2024-10-25 14:00:00', '2024-10-20 10:10:00', '2024-10-20 10:12:00'),
(2, 13, '2024-11-10', '11:30', 'cancelada', 13, '2024-11-10 11:30:00', '2024-11-05 15:30:00', '2024-11-05 15:32:00'),
(2, 19, '2024-08-28', '09:30', 'cancelada', 14, '2024-08-28 09:30:00', '2024-08-22 12:00:00', '2024-08-22 12:02:00'),
(3, 4, '2024-10-12', '12:00', 'cancelada', 2, '2024-10-12 12:00:00', '2024-10-08 14:45:00', '2024-10-08 14:47:00'),
(3, 6, '2024-09-28', '10:00', 'cancelada', 3, '2024-09-28 10:00:00', '2024-09-22 11:20:00', '2024-09-22 11:22:00'),
(3, 8, '2024-11-15', '16:00', 'cancelada', 5, '2024-11-15 16:00:00', '2024-11-10 09:30:00', '2024-11-10 09:32:00'),
-- Más estudiantes con citas canceladas
(4, 13, '2024-08-05', '10:00', 'cancelada', 13, '2024-08-05 10:00:00', '2024-07-30 13:15:00', '2024-07-30 13:17:00'),
(4, 19, '2024-09-12', '09:00', 'cancelada', 14, '2024-09-12 09:00:00', '2024-09-08 15:20:00', '2024-09-08 15:22:00'),
(5, 1, '2024-10-08', '15:30', 'cancelada', 1, '2024-10-08 15:30:00', '2024-10-03 10:45:00', '2024-10-03 10:47:00'),
(5, 11, '2024-11-20', '13:00', 'cancelada', 7, '2024-11-20 13:00:00', '2024-11-15 14:30:00', '2024-11-15 14:32:00'),
(6, 3, '2024-09-25', '11:30', 'cancelada', 2, '2024-09-25 11:30:00', '2024-09-20 16:10:00', '2024-09-20 16:12:00'),
(6, 5, '2024-10-30', '08:30', 'cancelada', 3, '2024-10-30 08:30:00', '2024-10-25 11:50:00', '2024-10-25 11:52:00'),
(7, 7, '2024-08-15', '14:00', 'cancelada', 4, '2024-08-15 14:00:00', '2024-08-10 12:25:00', '2024-08-10 12:27:00'),
(7, 9, '2024-09-22', '10:00', 'cancelada', 5, '2024-09-22 10:00:00', '2024-09-17 15:40:00', '2024-09-17 15:42:00'),
(8, 2, '2024-10-18', '16:00', 'cancelada', 1, '2024-10-18 16:00:00', '2024-10-13 09:15:00', '2024-10-13 09:17:00'),
(8, 13, '2024-11-25', '12:00', 'cancelada', 13, '2024-11-25 12:00:00', '2024-11-20 13:30:00', '2024-11-20 13:32:00'),
(9, 4, '2024-08-20', '12:30', 'cancelada', 2, '2024-08-20 12:30:00', '2024-08-15 14:20:00', '2024-08-15 14:22:00'),
(9, 19, '2024-09-30', '09:00', 'cancelada', 14, '2024-09-30 09:00:00', '2024-09-25 10:50:00', '2024-09-25 10:52:00'),
(10, 1, '2024-10-15', '14:00', 'cancelada', 1, '2024-10-15 14:00:00', '2024-10-10 11:25:00', '2024-10-10 11:27:00'),
(10, 11, '2024-11-28', '15:00', 'cancelada', 7, '2024-11-28 15:00:00', '2024-11-23 16:40:00', '2024-11-23 16:42:00'),
(11, 5, '2024-08-25', '09:30', 'cancelada', 3, '2024-08-25 09:30:00', '2024-08-20 12:15:00', '2024-08-20 12:17:00'),
(11, 13, '2024-09-28', '11:00', 'cancelada', 13, '2024-09-28 11:00:00', '2024-09-23 13:50:00', '2024-09-23 13:52:00'),
(12, 7, '2024-10-22', '15:30', 'cancelada', 4, '2024-10-22 15:30:00', '2024-10-17 10:30:00', '2024-10-17 10:32:00'),
(12, 9, '2024-11-18', '10:30', 'cancelada', 5, '2024-11-18 10:30:00', '2024-11-13 14:20:00', '2024-11-13 14:22:00'),
(13, 3, '2024-08-30', '11:00', 'cancelada', 2, '2024-08-30 11:00:00', '2024-08-25 15:10:00', '2024-08-25 15:12:00'),
(13, 19, '2024-10-05', '08:30', 'cancelada', 14, '2024-10-05 08:30:00', '2024-09-30 11:45:00', '2024-09-30 11:47:00'),
(14, 2, '2024-09-10', '16:00', 'cancelada', 1, '2024-09-10 16:00:00', '2024-09-05 12:30:00', '2024-09-05 12:32:00'),
(14, 13, '2024-10-28', '12:30', 'cancelada', 13, '2024-10-28 12:30:00', '2024-10-23 16:00:00', '2024-10-23 16:02:00'),
(15, 4, '2024-11-12', '13:00', 'cancelada', 2, '2024-11-12 13:00:00', '2024-11-07 09:20:00', '2024-11-07 09:22:00'),
(15, 11, '2024-08-18', '14:30', 'cancelada', 7, '2024-08-18 14:30:00', '2024-08-13 13:40:00', '2024-08-13 13:42:00'),
(16, 5, '2024-09-20', '10:00', 'cancelada', 3, '2024-09-20 10:00:00', '2024-09-15 14:50:00', '2024-09-15 14:52:00'),
(16, 7, '2024-10-25', '15:00', 'cancelada', 4, '2024-10-25 15:00:00', '2024-10-20 10:10:00', '2024-10-20 10:12:00'),
(17, 1, '2024-11-08', '14:00', 'cancelada', 1, '2024-11-08 14:00:00', '2024-11-03 15:30:00', '2024-11-03 15:32:00'),
(17, 9, '2024-08-12', '11:00', 'cancelada', 5, '2024-08-12 11:00:00', '2024-08-07 12:20:00', '2024-08-07 12:22:00'),
(18, 3, '2024-09-15', '12:00', 'cancelada', 2, '2024-09-15 12:00:00', '2024-09-10 11:15:00', '2024-09-10 11:17:00'),
(18, 13, '2024-10-30', '10:30', 'cancelada', 13, '2024-10-30 10:30:00', '2024-10-25 13:45:00', '2024-10-25 13:47:00'),
(19, 2, '2024-11-15', '15:30', 'cancelada', 1, '2024-11-15 15:30:00', '2024-11-10 14:00:00', '2024-11-10 14:02:00'),
(19, 19, '2024-08-22', '09:00', 'cancelada', 14, '2024-08-22 09:00:00', '2024-08-17 15:25:00', '2024-08-17 15:27:00'),
(20, 4, '2024-09-28', '13:30', 'cancelada', 2, '2024-09-28 13:30:00', '2024-09-23 10:40:00', '2024-09-23 10:42:00'),
(20, 11, '2024-10-18', '14:00', 'cancelada', 7, '2024-10-18 14:00:00', '2024-10-13 12:50:00', '2024-10-13 12:52:00'),
(21, 5, '2024-11-22', '09:30', 'cancelada', 3, '2024-11-22 09:30:00', '2024-11-17 16:15:00', '2024-11-17 16:17:00'),
(21, 7, '2024-08-28', '16:00', 'cancelada', 4, '2024-08-28 16:00:00', '2024-08-23 11:30:00', '2024-08-23 11:32:00'),
(22, 1, '2024-09-18', '14:30', 'cancelada', 1, '2024-09-18 14:30:00', '2024-09-13 13:20:00', '2024-09-13 13:22:00'),
(22, 13, '2024-10-25', '11:00', 'cancelada', 13, '2024-10-25 11:00:00', '2024-10-20 14:10:00', '2024-10-20 14:12:00'),
(23, 3, '2024-11-10', '12:30', 'cancelada', 2, '2024-11-10 12:30:00', '2024-11-05 09:50:00', '2024-11-05 09:52:00'),
(23, 9, '2024-08-15', '10:00', 'cancelada', 5, '2024-08-15 10:00:00', '2024-08-10 15:40:00', '2024-08-10 15:42:00'),
(24, 2, '2024-09-22', '15:00', 'cancelada', 1, '2024-09-22 15:00:00', '2024-09-17 12:25:00', '2024-09-17 12:27:00'),
(24, 19, '2024-10-28', '08:30', 'cancelada', 14, '2024-10-28 08:30:00', '2024-10-23 11:15:00', '2024-10-23 11:17:00'),
(25, 4, '2024-11-20', '13:00', 'cancelada', 2, '2024-11-20 13:00:00', '2024-11-15 14:30:00', '2024-11-15 14:32:00'),
(25, 11, '2024-08-25', '14:30', 'cancelada', 7, '2024-08-25 14:30:00', '2024-08-20 10:20:00', '2024-08-20 10:22:00');

-- Citas reservadas (activas y pasadas con atención) para KPIs
-- Citas reservadas con hora_atencion para calcular tiempo de espera
INSERT INTO citas (estudiante_id, medico_id, fecha, hora, estado, especialidad_id, hora_cita, hora_atencion, created_at, reserva_confirmada_at)
VALUES
-- Citas con tiempos de espera variados (algunas cumplen meta <15min, otras no)
(1, 13, '2024-11-01', '10:00', 'reservada', 13, '2024-11-01 10:00:00', '2024-11-01 10:08:00', '2024-10-28 14:20:00', '2024-10-28 14:22:00'), -- 8 min
(2, 13, '2024-11-01', '11:00', 'reservada', 13, '2024-11-01 11:00:00', '2024-11-01 11:12:00', '2024-10-28 15:30:00', '2024-10-28 15:32:00'), -- 12 min
(3, 13, '2024-11-01', '12:00', 'reservada', 13, '2024-11-01 12:00:00', '2024-11-01 12:18:00', '2024-10-29 09:15:00', '2024-10-29 09:17:00'), -- 18 min
(4, 13, '2024-11-02', '10:00', 'reservada', 13, '2024-11-02 10:00:00', '2024-11-02 10:05:00', '2024-10-29 11:20:00', '2024-10-29 11:22:00'), -- 5 min
(5, 13, '2024-11-02', '11:00', 'reservada', 13, '2024-11-02 11:00:00', '2024-11-02 11:14:00', '2024-10-29 13:45:00', '2024-10-29 13:47:00'), -- 14 min
(6, 13, '2024-11-02', '12:00', 'reservada', 13, '2024-11-02 12:00:00', '2024-11-02 12:20:00', '2024-10-30 10:10:00', '2024-10-30 10:12:00'), -- 20 min
(7, 13, '2024-11-03', '10:00', 'reservada', 13, '2024-11-03 10:00:00', '2024-11-03 10:07:00', '2024-10-30 14:30:00', '2024-10-30 14:32:00'), -- 7 min
(8, 13, '2024-11-03', '11:00', 'reservada', 13, '2024-11-03 11:00:00', '2024-11-03 11:13:00', '2024-10-31 09:25:00', '2024-10-31 09:27:00'), -- 13 min
(9, 13, '2024-11-03', '12:00', 'reservada', 13, '2024-11-03 12:00:00', '2024-11-03 12:16:00', '2024-10-31 11:40:00', '2024-10-31 11:42:00'), -- 16 min
(10, 13, '2024-11-04', '10:00', 'reservada', 13, '2024-11-04 10:00:00', '2024-11-04 10:06:00', '2024-11-01 13:15:00', '2024-11-01 13:17:00'), -- 6 min
(11, 13, '2024-11-04', '11:00', 'reservada', 13, '2024-11-04 11:00:00', '2024-11-04 11:11:00', '2024-11-01 15:20:00', '2024-11-01 15:22:00'), -- 11 min
(12, 13, '2024-11-04', '12:00', 'reservada', 13, '2024-11-04 12:00:00', '2024-11-04 12:19:00', '2024-11-02 10:30:00', '2024-11-02 10:32:00'), -- 19 min
(13, 13, '2024-11-05', '10:00', 'reservada', 13, '2024-11-05 10:00:00', '2024-11-05 10:04:00', '2024-11-02 12:45:00', '2024-11-02 12:47:00'), -- 4 min
(14, 13, '2024-11-05', '11:00', 'reservada', 13, '2024-11-05 11:00:00', '2024-11-05 11:15:00', '2024-11-02 14:50:00', '2024-11-02 14:52:00'), -- 15 min
(15, 13, '2024-11-05', '12:00', 'reservada', 13, '2024-11-05 12:00:00', '2024-11-05 12:22:00', '2024-11-03 09:10:00', '2024-11-03 09:12:00'), -- 22 min
(16, 13, '2024-11-06', '10:00', 'reservada', 13, '2024-11-06 10:00:00', '2024-11-06 10:09:00', '2024-11-03 11:25:00', '2024-11-03 11:27:00'), -- 9 min
(17, 13, '2024-11-06', '11:00', 'reservada', 13, '2024-11-06 11:00:00', '2024-11-06 11:10:00', '2024-11-03 13:40:00', '2024-11-03 13:42:00'), -- 10 min
(18, 13, '2024-11-06', '12:00', 'reservada', 13, '2024-11-06 12:00:00', '2024-11-06 12:17:00', '2024-11-04 10:15:00', '2024-11-04 10:17:00'), -- 17 min
(19, 13, '2024-11-07', '10:00', 'reservada', 13, '2024-11-07 10:00:00', '2024-11-07 10:03:00', '2024-11-04 12:30:00', '2024-11-04 12:32:00'), -- 3 min
(20, 13, '2024-11-07', '11:00', 'reservada', 13, '2024-11-07 11:00:00', '2024-11-07 11:14:00', '2024-11-04 14:45:00', '2024-11-04 14:47:00'), -- 14 min
-- Más citas con diferentes especialidades
(1, 1, '2024-10-15', '14:30', 'reservada', 1, '2024-10-15 14:30:00', '2024-10-15 14:42:00', '2024-10-10 10:20:00', '2024-10-10 10:22:00'), -- 12 min
(2, 1, '2024-10-15', '15:00', 'reservada', 1, '2024-10-15 15:00:00', '2024-10-15 15:08:00', '2024-10-10 11:30:00', '2024-10-10 11:32:00'), -- 8 min
(3, 1, '2024-10-15', '15:30', 'reservada', 1, '2024-10-15 15:30:00', '2024-10-15 15:48:00', '2024-10-10 12:40:00', '2024-10-10 12:42:00'), -- 18 min
(4, 3, '2024-10-18', '11:00', 'reservada', 2, '2024-10-18 11:00:00', '2024-10-18 11:13:00', '2024-10-13 14:15:00', '2024-10-13 14:17:00'), -- 13 min
(5, 3, '2024-10-18', '11:30', 'reservada', 2, '2024-10-18 11:30:00', '2024-10-18 11:35:00', '2024-10-13 15:25:00', '2024-10-13 15:27:00'), -- 5 min
(6, 3, '2024-10-18', '12:00', 'reservada', 2, '2024-10-18 12:00:00', '2024-10-18 12:21:00', '2024-10-14 09:50:00', '2024-10-14 09:52:00'), -- 21 min
(7, 5, '2024-10-22', '09:00', 'reservada', 3, '2024-10-22 09:00:00', '2024-10-22 09:11:00', '2024-10-17 11:20:00', '2024-10-17 11:22:00'), -- 11 min
(8, 5, '2024-10-22', '09:30', 'reservada', 3, '2024-10-22 09:30:00', '2024-10-22 09:37:00', '2024-10-17 12:30:00', '2024-10-17 12:32:00'), -- 7 min
(9, 5, '2024-10-22', '10:00', 'reservada', 3, '2024-10-22 10:00:00', '2024-10-22 10:19:00', '2024-10-17 13:40:00', '2024-10-17 13:42:00'), -- 19 min
(10, 11, '2024-10-25', '14:00', 'reservada', 7, '2024-10-25 14:00:00', '2024-10-25 14:06:00', '2024-10-20 10:10:00', '2024-10-20 10:12:00'), -- 6 min
(11, 11, '2024-10-25', '14:30', 'reservada', 7, '2024-10-25 14:30:00', '2024-10-25 14:43:00', '2024-10-20 11:20:00', '2024-10-20 11:22:00'), -- 13 min
(12, 11, '2024-10-25', '15:00', 'reservada', 7, '2024-10-25 15:00:00', '2024-10-25 15:16:00', '2024-10-20 12:30:00', '2024-10-20 12:32:00'), -- 16 min
(13, 19, '2024-10-28', '09:00', 'reservada', 14, '2024-10-28 09:00:00', '2024-10-28 09:05:00', '2024-10-23 14:15:00', '2024-10-23 14:17:00'), -- 5 min
(14, 19, '2024-10-28', '09:30', 'reservada', 14, '2024-10-28 09:30:00', '2024-10-28 09:44:00', '2024-10-23 15:25:00', '2024-10-23 15:27:00'), -- 14 min
(15, 19, '2024-10-28', '10:00', 'reservada', 14, '2024-10-28 10:00:00', '2024-10-28 10:18:00', '2024-10-24 09:40:00', '2024-10-24 09:42:00'), -- 18 min
-- Citas reservadas futuras (sin hora_atencion aún)
(1, 13, '2025-12-05', '10:00', 'reservada', 13, '2025-12-05 10:00:00', NULL, '2024-11-28 14:20:00', '2024-11-28 14:22:00'),
(2, 13, '2025-12-05', '11:00', 'reservada', 13, '2025-12-05 11:00:00', NULL, '2024-11-28 15:30:00', '2024-11-28 15:32:00'),
(3, 13, '2025-12-05', '12:00', 'reservada', 13, '2025-12-05 12:00:00', NULL, '2024-11-29 09:15:00', '2024-11-29 09:17:00'),
(4, 1, '2025-12-10', '14:30', 'reservada', 1, '2025-12-10 14:30:00', NULL, '2024-11-30 10:20:00', '2024-11-30 10:22:00'),
(5, 1, '2025-12-10', '15:00', 'reservada', 1, '2025-12-10 15:00:00', NULL, '2024-11-30 11:30:00', '2024-11-30 11:32:00'),
(6, 3, '2025-12-12', '11:00', 'reservada', 2, '2025-12-12 11:00:00', NULL, '2024-12-01 14:15:00', '2024-12-01 14:17:00'),
(7, 5, '2025-12-15', '09:00', 'reservada', 3, '2025-12-15 09:00:00', NULL, '2024-12-02 11:20:00', '2024-12-02 11:22:00'),
(8, 11, '2025-12-18', '14:00', 'reservada', 7, '2025-12-18 14:00:00', NULL, '2024-12-03 10:10:00', '2024-12-03 10:12:00'),
(9, 19, '2025-12-20', '09:00', 'reservada', 14, '2025-12-20 09:00:00', NULL, '2024-12-04 14:15:00', '2024-12-04 14:17:00'),
(10, 13, '2025-12-22', '10:00', 'reservada', 13, '2025-12-22 10:00:00', NULL, '2024-12-05 13:15:00', '2024-12-05 13:17:00');

-- Calificaciones para el KPI de satisfacción
-- Calificaciones variadas (algunas altas, algunas bajas) para tener un promedio realista
INSERT INTO calificaciones (cita_id, calificacion, comentario, created_at)
VALUES
(51, 5, 'Excelente atención, muy profesional', '2024-11-01 10:15:00'),
(52, 4, 'Buen servicio, esperé un poco', '2024-11-01 11:20:00'),
(53, 3, 'Atención regular', '2024-11-01 12:30:00'),
(54, 5, 'Muy satisfecho con la atención', '2024-11-02 10:10:00'),
(55, 4, 'Buen médico, recomendado', '2024-11-02 11:25:00'),
(56, 2, 'Tuve que esperar mucho tiempo', '2024-11-02 12:40:00'),
(57, 5, 'Excelente experiencia', '2024-11-03 10:15:00'),
(58, 4, 'Muy buena atención', '2024-11-03 11:25:00'),
(59, 4, 'Satisfecho con el servicio', '2024-11-03 12:30:00'),
(60, 5, 'Excelente profesional', '2024-11-04 10:10:00'),
(61, 5, 'Muy recomendado', '2024-11-04 11:20:00'),
(62, 3, 'Atención aceptable', '2024-11-04 12:35:00'),
(63, 5, 'Excelente servicio', '2024-11-05 10:10:00'),
(64, 4, 'Buen trato', '2024-11-05 11:25:00'),
(65, 2, 'Demasiada espera', '2024-11-05 12:40:00'),
(66, 5, 'Muy profesional', '2024-11-06 10:15:00'),
(67, 4, 'Buen servicio', '2024-11-06 11:20:00'),
(68, 4, 'Satisfecho', '2024-11-06 12:30:00'),
(69, 5, 'Excelente atención', '2024-11-07 10:10:00'),
(70, 4, 'Muy bueno', '2024-11-07 11:25:00'),
(71, 5, 'Excelente médico', '2024-10-15 14:50:00'),
(72, 4, 'Buen servicio', '2024-10-15 15:15:00'),
(73, 3, 'Regular', '2024-10-15 16:00:00'),
(74, 5, 'Muy satisfecho', '2024-10-18 11:20:00'),
(75, 4, 'Buen trato', '2024-10-18 11:45:00'),
(76, 2, 'Mucha espera', '2024-10-18 12:30:00'),
(77, 5, 'Excelente', '2024-10-22 09:20:00'),
(78, 4, 'Muy bueno', '2024-10-22 09:45:00'),
(79, 4, 'Satisfactorio', '2024-10-22 10:30:00'),
(80, 5, 'Excelente atención', '2024-10-25 14:15:00'),
(81, 4, 'Buen servicio', '2024-10-25 14:50:00'),
(82, 4, 'Recomendado', '2024-10-25 15:25:00'),
(83, 5, 'Muy profesional', '2024-10-28 09:15:00'),
(84, 4, 'Buen trato', '2024-10-28 10:00:00'),
(85, 4, 'Satisfecho', '2024-10-28 10:30:00');

-- =======================
-- CITAS CON ESTADO "ATENDIDA" (para historial y calificación)
-- =======================

-- Actualizar citas existentes con hora_atencion para que sean "atendida" en lugar de "reservada"
-- Esto se hará mediante UPDATE para las citas que ya tienen hora_atencion y fecha pasada
-- (Nota: Este UPDATE se ejecutará cuando se restaure el dump)

-- Citas atendidas SIN calificación (para poder probar la funcionalidad de calificación)
-- Estas citas tienen hora_atencion pero NO tienen calificación aún
INSERT INTO citas (estudiante_id, medico_id, fecha, hora, estado, especialidad_id, hora_cita, hora_atencion, created_at, reserva_confirmada_at)
VALUES
-- Estudiantes 1-3 con citas atendidas sin calificar
(1, 13, '2024-11-20', '10:00', 'atendida', 13, '2024-11-20 10:00:00', '2024-11-20 10:08:00', '2024-11-15 14:20:00', '2024-11-15 14:22:00'),
(1, 1, '2024-11-18', '14:30', 'atendida', 1, '2024-11-18 14:30:00', '2024-11-18 14:35:00', '2024-11-13 10:20:00', '2024-11-13 10:22:00'),
(1, 11, '2024-11-25', '14:00', 'atendida', 7, '2024-11-25 14:00:00', '2024-11-25 14:06:00', '2024-11-20 10:10:00', '2024-11-20 10:12:00'),
(2, 13, '2024-11-21', '11:00', 'atendida', 13, '2024-11-21 11:00:00', '2024-11-21 11:12:00', '2024-11-16 15:30:00', '2024-11-16 15:32:00'),
(2, 3, '2024-11-19', '11:00', 'atendida', 2, '2024-11-19 11:00:00', '2024-11-19 11:15:00', '2024-11-14 14:15:00', '2024-11-14 14:17:00'),
(2, 5, '2024-11-26', '09:00', 'atendida', 3, '2024-11-26 09:00:00', '2024-11-26 09:07:00', '2024-11-21 11:20:00', '2024-11-21 11:22:00'),
(3, 13, '2024-11-22', '12:00', 'atendida', 13, '2024-11-22 12:00:00', '2024-11-22 12:10:00', '2024-11-17 09:15:00', '2024-11-17 09:17:00'),
(3, 11, '2024-11-20', '14:00', 'atendida', 7, '2024-11-20 14:00:00', '2024-11-20 14:05:00', '2024-11-15 10:10:00', '2024-11-15 10:12:00'),
(3, 19, '2024-11-27', '09:00', 'atendida', 14, '2024-11-27 09:00:00', '2024-11-27 09:05:00', '2024-11-22 14:15:00', '2024-11-22 14:17:00'),
-- Más estudiantes con citas atendidas sin calificar
(4, 13, '2024-11-23', '10:00', 'atendida', 13, '2024-11-23 10:00:00', '2024-11-23 10:06:00', '2024-11-18 11:20:00', '2024-11-18 11:22:00'),
(4, 1, '2024-11-28', '14:30', 'atendida', 1, '2024-11-28 14:30:00', '2024-11-28 14:38:00', '2024-11-23 10:20:00', '2024-11-23 10:22:00'),
(5, 1, '2024-11-17', '15:00', 'atendida', 1, '2024-11-17 15:00:00', '2024-11-17 15:08:00', '2024-11-12 11:30:00', '2024-11-12 11:32:00'),
(5, 3, '2024-11-24', '11:30', 'atendida', 2, '2024-11-24 11:30:00', '2024-11-24 11:35:00', '2024-11-19 15:25:00', '2024-11-19 15:27:00'),
(6, 3, '2024-11-21', '12:00', 'atendida', 2, '2024-11-21 12:00:00', '2024-11-21 12:18:00', '2024-11-16 09:50:00', '2024-11-16 09:52:00'),
(6, 5, '2024-11-25', '09:30', 'atendida', 3, '2024-11-25 09:30:00', '2024-11-25 09:37:00', '2024-11-20 12:30:00', '2024-11-20 12:32:00'),
(7, 5, '2024-11-24', '09:00', 'atendida', 3, '2024-11-24 09:00:00', '2024-11-24 09:11:00', '2024-11-19 11:20:00', '2024-11-19 11:22:00'),
(7, 11, '2024-11-26', '14:30', 'atendida', 7, '2024-11-26 14:30:00', '2024-11-26 14:43:00', '2024-11-21 11:20:00', '2024-11-21 11:22:00'),
(8, 11, '2024-11-25', '14:00', 'atendida', 7, '2024-11-25 14:00:00', '2024-11-25 14:12:00', '2024-11-20 10:10:00', '2024-11-20 10:12:00'),
(8, 13, '2024-11-27', '11:00', 'atendida', 13, '2024-11-27 11:00:00', '2024-11-27 11:13:00', '2024-11-22 09:25:00', '2024-11-22 09:27:00'),
(9, 19, '2024-11-26', '09:00', 'atendida', 14, '2024-11-26 09:00:00', '2024-11-26 09:05:00', '2024-11-21 14:15:00', '2024-11-21 14:17:00'),
(9, 13, '2024-11-28', '12:00', 'atendida', 13, '2024-11-28 12:00:00', '2024-11-28 12:16:00', '2024-11-23 11:40:00', '2024-11-23 11:42:00'),
(10, 13, '2024-11-27', '10:00', 'atendida', 13, '2024-11-27 10:00:00', '2024-11-27 10:14:00', '2024-11-22 13:15:00', '2024-11-22 13:17:00'),
(10, 1, '2024-11-29', '14:00', 'atendida', 1, '2024-11-29 14:00:00', '2024-11-29 14:08:00', '2024-11-24 11:25:00', '2024-11-24 11:27:00');

-- Actualizar las citas que ya tienen hora_atencion para cambiar su estado a "atendida"
-- Solo si tienen fecha pasada (ya fueron atendidas)
UPDATE citas 
SET estado = 'atendida' 
WHERE hora_atencion IS NOT NULL 
AND estado = 'reservada'
AND fecha < CURRENT_DATE;

INSERT INTO registro_atencion (
    cita_id,
    hora_llegada,
    hora_inicio,
    hora_fin,
    estado_atencion,
    observacion
)
SELECT
    id,
    hora_cita,
    hora_atencion,
    hora_atencion + interval '15 minutes',
    'finalizada',
    'Registro generado desde datos historicos de citas'
FROM citas
WHERE hora_atencion IS NOT NULL;
