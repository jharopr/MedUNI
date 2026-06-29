ALTER TABLE estudiantes
ADD COLUMN IF NOT EXISTS estado BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE medicos
ADD COLUMN IF NOT EXISTS estado BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

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
