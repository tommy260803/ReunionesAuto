-- Script para actualizar la contraseña del usuario administrador
-- La nueva contraseña será: password123
-- El hash se genera con bcrypt (cost factor 12)

-- Primero verificar si el usuario existe
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM usuarios WHERE correo = 'juanaureliodelacruzgamarra@gmail.com') THEN
        -- Si no existe, crearlo
        INSERT INTO usuarios (nombre, correo, password_hash, nivel_suscripcion, estado_suscripcion, rol)
        VALUES (
            'Juana Aurelio de la Cruz Gamarra',
            'juanaureliodelacruzgamarra@gmail.com',
            '$2b$12$1.GMkb3vVEIKcHqhhMZDmO87fHD08txYdx5KeS.nqR8DEa3YzfiJi',
            'enterprise',
            'activo',
            'ADMIN'
        );
        RAISE NOTICE 'Usuario administrador creado';
    ELSE
        -- Si existe, actualizar contraseña y rol
        UPDATE usuarios 
        SET password_hash = '$2b$12$1.GMkb3vVEIKcHqhhMZDmO87fHD08txYdx5KeS.nqR8DEa3YzfiJi',
            rol = 'ADMIN'
        WHERE correo = 'juanaureliodelacruzgamarra@gmail.com';
        RAISE NOTICE 'Contraseña y rol de administrador actualizados';
    END IF;
END $$;

-- Verificar el cambio
SELECT id, nombre, correo, rol, estado_suscripcion 
FROM usuarios 
WHERE correo = 'juanaureliodelacruzgamarra@gmail.com';

-- Nota: La contraseña es 'password123'
