ALTER TABLE estudiantes
ADD COLUMN IF NOT EXISTS estado BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE medicos
ADD COLUMN IF NOT EXISTS estado BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS username VARCHAR(100) UNIQUE,
ADD COLUMN IF NOT EXISTS password VARCHAR(100);

UPDATE medicos
SET username = 'beatriz', password = 'medico123'
WHERE correo = 'beatriz.flores@correo.com'
  AND username IS NULL;

ALTER TABLE administradores
ADD COLUMN IF NOT EXISTS estado BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE citas
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE citas
DROP CONSTRAINT IF EXISTS citas_estado_check;

ALTER TABLE citas
ADD CONSTRAINT citas_estado_check
CHECK (estado IN ('reservada', 'cancelada', 'atendida', 'no_asistio'));

CREATE UNIQUE INDEX IF NOT EXISTS uq_cita_medico_horario_reservada
ON citas (medico_id, fecha, hora)
WHERE estado = 'reservada';

CREATE TABLE IF NOT EXISTS registro_atencion (
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

CREATE TABLE IF NOT EXISTS auditoria (
    id SERIAL PRIMARY KEY,
    usuario_id INT,
    rol VARCHAR(30),
    accion VARCHAR(100) NOT NULL,
    entidad VARCHAR(100) NOT NULL,
    entidad_id INT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    detalle TEXT
);

CREATE TABLE IF NOT EXISTS personal_topico (
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

INSERT INTO personal_topico (nombres, apellidos, correo, username, password)
VALUES ('Personal', 'Topico', 'topico@uni.pe', 'topico', 'topico123')
ON CONFLICT (username) DO NOTHING;

CREATE UNIQUE INDEX IF NOT EXISTS uq_calificaciones_cita
ON calificaciones (cita_id);

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
WHERE hora_atencion IS NOT NULL
ON CONFLICT (cita_id) DO NOTHING;

INSERT INTO citas (
    estudiante_id,
    medico_id,
    fecha,
    hora,
    estado,
    especialidad_id,
    hora_cita,
    created_at,
    reserva_confirmada_at,
    updated_at
)
SELECT
    1,
    m.id,
    CURRENT_DATE,
    '10:00',
    'reservada',
    m.especialidad_id,
    CURRENT_DATE + time '10:00',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
FROM medicos m
WHERE m.username = 'beatriz'
  AND NOT EXISTS (
      SELECT 1
      FROM citas c
      WHERE c.medico_id = m.id
        AND c.fecha = CURRENT_DATE
        AND c.hora = '10:00'
        AND c.estado = 'reservada'
  );

INSERT INTO estudiantes (nombres, apellidos, correo, codigo_estudiante, codigo_dirce)
VALUES
('Sofia', 'Prueba Dental', 'sofia.dental@uni.pe', 'TESTODON01', '111111'),
('Mateo', 'Prueba Nutricion', 'mateo.nutricion@uni.pe', 'TESTNUTRI01', '111111'),
('Valeria', 'Prueba Oftalmologia', 'valeria.oftalmo@uni.pe', 'TESTOFTA01', '111111')
ON CONFLICT (codigo_estudiante) DO NOTHING;

WITH agenda(codigo_estudiante, medico_correo, fecha, hora, especialidad_id) AS (
    VALUES
    ('20234044I', 'beatriz.flores@correo.com', DATE '2026-06-29', TIME '10:00', 7),
    ('20244017D', 'beatriz.flores@correo.com', DATE '2026-06-29', TIME '10:30', 7),
    ('20234044I', 'beatriz.flores@correo.com', DATE '2026-06-30', TIME '10:00', 7),
    ('20234044I', 'beatriz.flores@correo.com', DATE '2026-06-30', TIME '10:30', 7),
    ('20240010E', 'beatriz.flores@correo.com', DATE '2026-06-30', TIME '11:00', 7),
    ('20234044I', 'beatriz.flores@correo.com', DATE '2026-07-01', TIME '10:00', 7),
    ('TESTODON01', 'andrea.martinez@correo.com', DATE '2026-06-29', TIME '09:00', 9),
    ('TESTODON01', 'andrea.martinez@correo.com', DATE '2026-06-30', TIME '09:00', 9),
    ('TESTNUTRI01', 'valeria.garcia@correo.com', DATE '2026-06-30', TIME '08:30', 14),
    ('TESTNUTRI01', 'valeria.garcia@correo.com', DATE '2026-07-01', TIME '09:00', 14),
    ('TESTOFTA01', 'laura.sanchez@correo.com', DATE '2026-06-29', TIME '10:30', 5),
    ('TESTOFTA01', 'laura.sanchez@correo.com', DATE '2026-07-01', TIME '10:00', 5)
)
INSERT INTO citas (
    estudiante_id,
    medico_id,
    fecha,
    hora,
    estado,
    especialidad_id,
    hora_cita,
    created_at,
    reserva_confirmada_at,
    updated_at
)
SELECT
    e.id,
    m.id,
    a.fecha,
    a.hora,
    'reservada',
    a.especialidad_id,
    a.fecha + a.hora,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
FROM agenda a
JOIN estudiantes e ON e.codigo_estudiante = a.codigo_estudiante
JOIN medicos m ON m.correo = a.medico_correo
WHERE NOT EXISTS (
    SELECT 1
    FROM citas c
    WHERE c.medico_id = m.id
      AND c.fecha = a.fecha
      AND c.hora = a.hora
      AND c.estado = 'reservada'
);
