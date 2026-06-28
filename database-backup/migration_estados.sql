-- =======================
-- MIGRACIÓN DE ESTADOS DE CITAS
-- =======================
-- Este script actualiza los estados antiguos de citas a los nuevos estados
-- Ejecutar después de actualizar el esquema de la base de datos

-- Actualizar citas con estado 'pendiente' a 'reservada'
UPDATE citas 
SET estado = 'reservada' 
WHERE estado = 'pendiente';

-- Actualizar citas con estado 'confirmada' a 'reservada'
UPDATE citas 
SET estado = 'reservada' 
WHERE estado = 'confirmada';

-- Actualizar citas con estado 'no_asistio' a 'cancelada'
UPDATE citas 
SET estado = 'cancelada' 
WHERE estado = 'no_asistio';

-- Verificar que solo queden estados 'reservada' y 'cancelada'
-- SELECT DISTINCT estado FROM citas;

