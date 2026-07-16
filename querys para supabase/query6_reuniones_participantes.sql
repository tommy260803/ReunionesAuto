-- Ejecutar después de query5_metricas.txt.
-- Inserta la reunión y sus participantes en una única transacción.

CREATE OR REPLACE FUNCTION public.crear_reunion_con_participantes(
  p_reunion JSONB,
  p_participantes JSONB
)
RETURNS public.reuniones
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  nueva_reunion public.reuniones;
BEGIN
  IF jsonb_typeof(p_participantes) <> 'array' OR jsonb_array_length(p_participantes) = 0 THEN
    RAISE EXCEPTION 'La reunión requiere al menos un participante organizador';
  END IF;

  INSERT INTO public.reuniones (
    creador_id, tema, fecha_inicio, duracion_minutos, proveedor,
    id_externo, join_url, start_url, estado, tipo, direccion
  )
  VALUES (
    (p_reunion->>'creador_id')::uuid,
    p_reunion->>'tema',
    (p_reunion->>'fecha_inicio')::timestamptz,
    COALESCE((p_reunion->>'duracion_minutos')::integer, 60),
    COALESCE(NULLIF(p_reunion->>'proveedor', ''), 'zoom'),
    NULLIF(p_reunion->>'id_externo', ''),
    NULLIF(p_reunion->>'join_url', ''),
    NULLIF(p_reunion->>'start_url', ''),
    COALESCE(NULLIF(p_reunion->>'estado', ''), 'programada'),
    COALESCE(NULLIF(p_reunion->>'tipo', ''), 'virtual'),
    NULLIF(p_reunion->>'direccion', '')
  )
  RETURNING * INTO nueva_reunion;

  INSERT INTO public.participantes (
    reunion_id, usuario_id, correo, rol, estado_invitacion
  )
  SELECT
    nueva_reunion.id,
    NULLIF(participante->>'usuario_id', '')::uuid,
    lower(trim(participante->>'correo')),
    COALESCE(NULLIF(participante->>'rol', ''), 'participante'),
    'enviado'
  FROM jsonb_array_elements(p_participantes) AS participante
  WHERE NULLIF(trim(participante->>'correo'), '') IS NOT NULL
  ON CONFLICT (reunion_id, correo) DO UPDATE
  SET
    usuario_id = COALESCE(EXCLUDED.usuario_id, participantes.usuario_id),
    rol = CASE
      WHEN EXCLUDED.rol = 'organizador' THEN 'organizador'
      ELSE participantes.rol
    END;

  IF NOT EXISTS (
    SELECT 1 FROM public.participantes WHERE reunion_id = nueva_reunion.id
  ) THEN
    RAISE EXCEPTION 'No se pudo registrar ningún participante válido';
  END IF;

  RETURN nueva_reunion;
END;
$$;

REVOKE ALL ON FUNCTION public.crear_reunion_con_participantes(JSONB, JSONB) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.crear_reunion_con_participantes(JSONB, JSONB) TO anon, authenticated;
NOTIFY pgrst, 'reload schema';
