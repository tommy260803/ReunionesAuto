-- Script para establecer el rol de administrador
-- Este script debe ejecutarse después de la migración query9_evaluacion_cientifica.sql

-- Actualizar el rol del usuario administrador principal
UPDATE usuarios 
SET rol = 'ADMIN' 
WHERE correo = 'anthonygv268@gmail.com';

-- Verificar el cambio
SELECT id, nombre, correo, rol 
FROM usuarios 
WHERE correo = 'anthonygv268@gmail.com';

-- Opcional: Establecer roles para otros usuarios de prueba
-- UPDATE usuarios SET rol = 'INVESTIGADOR' WHERE correo IN ('jmecolab@unitru.edu.pe', 'albedodark@gmail.com');
-- UPDATE usuarios SET rol = 'EVALUADOR' WHERE correo IN ('mecber_11@hotmail.com', 'raimg134@gmail.com');
