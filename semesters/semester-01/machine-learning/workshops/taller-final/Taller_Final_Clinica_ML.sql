-- =====================================================================
-- Taller Final — Segmentación de servicios clínicos (PCA + K-Means)
-- Doctorado en Ciencia de Datos e Inteligencia Artificial
-- Universidad El Bosque · Machine Learning
--
-- Script de SOLO LECTURA: únicamente contiene consultas SELECT.
-- No incluye credenciales; la conexión se configura en el cliente.
-- =====================================================================

USE uokplago_clinica_ml;

-- ---------------------------------------------------------------------
-- 1. Muestra de cada tabla de la base de datos
-- ---------------------------------------------------------------------

SELECT * FROM medicos LIMIT 5;

SELECT * FROM pacientes LIMIT 5;

SELECT * FROM citas LIMIT 5;

SELECT * FROM tratamientos LIMIT 5;

-- ---------------------------------------------------------------------
-- 2. Consulta analítica (JOIN) usada para construir el dataset
--    - id_cita: solo identificador (no se usa como variable de ML).
--    - especialidad: solo para interpretar los clústeres.
--    - seis variables numéricas: entrada de PCA y K-Means.
-- ---------------------------------------------------------------------

SELECT
    c.id_cita          AS id_cita,
    m.especialidad     AS especialidad,
    p.edad             AS edad,
    c.duracion_min     AS duracion_min,
    c.costo            AS costo_cita,
    t.dosis_mg         AS dosis_mg,
    t.dias_tratamiento AS dias_tratamiento,
    c.satisfaccion     AS satisfaccion
FROM citas c
JOIN pacientes p
    ON p.id_paciente = c.id_paciente
JOIN medicos m
    ON m.id_medico = c.id_medico
JOIN tratamientos t
    ON t.id_cita = c.id_cita
ORDER BY c.id_cita;
