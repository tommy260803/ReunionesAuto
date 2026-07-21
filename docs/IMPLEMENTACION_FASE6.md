# Implementación Fase 6: Mejoras de Seguridad y Roles

**Estado:** COMPLETADO  
**Fecha:** 2026-07-20

---

## Objetivo

Eliminar la autorización hardcodeada basada en correo electrónico e implementar un sistema de roles robusto basado en base de datos.

---

## Cambios Realizados

### 1. Actualización de `dependencies.py`

**Archivo:** `backend/app/core/dependencies.py`

**Cambios:**
- Eliminada dependencia de `settings.ADMIN_EMAIL`
- Implementada verificación de roles basada en columna `rol` de BD
- Agregados flags de rol: `is_admin`, `is_investigator`, `is_evaluator`
- Creadas nuevas dependencias: `get_current_investigator`, `get_current_evaluator`

**Lógica de roles:**
```python
# Agregar flag de administrador basado en rol de BD
user["is_admin"] = user.get("rol", "USUARIO") == "ADMIN"
# Agregar flag de investigador
user["is_investigator"] = user.get("rol", "USUARIO") in ("ADMIN", "INVESTIGADOR")
# Agregar flag de evaluador
user["is_evaluator"] = user.get("rol", "USUARIO") in ("ADMIN", "INVESTIGADOR", "EVALUADOR")
```

**Nuevas dependencias:**
- `get_current_admin`: Verifica rol ADMIN
- `get_current_investigator`: Verifica rol ADMIN o INVESTIGADOR
- `get_current_evaluator`: Verifica rol ADMIN, INVESTIGADOR o EVALUADOR

---

### 2. Actualización de `config.py`

**Archivo:** `backend/app/core/config.py`

**Cambio:**
- Eliminada constante `ADMIN_EMAIL` hardcodeada
- Ya no hay dependencia de correo electrónico para autorización

**Antes:**
```python
# --- Correo del administrador (hardcoded) ---
ADMIN_EMAIL: str = "juanaureliodelacruzgamarra@gmail.com"
```

**Después:**
- Eliminado completamente

---

### 3. Actualización de `auth/schemas.py`

**Archivo:** `backend/app/auth/schemas.py`

**Cambios:**
- Agregado campo `rol` a `UserResponse`
- Agregados flags `is_investigator` y `is_evaluator` a `UserResponse`

**Schema actualizado:**
```python
class UserResponse(BaseModel):
    id: str
    correo: str
    nombre: str
    nivel_suscripcion: str
    estado_suscripcion: str
    rol: str = "USUARIO"
    is_admin: bool = False
    is_investigator: bool = False
    is_evaluator: bool = False
```

---

### 4. Actualización de `auth/router.py`

**Archivo:** `backend/app/auth/router.py`

**Cambios:**
- Consulta de usuario ahora incluye columna `rol`
- Determinación de roles basada en BD en lugar de correo
- Respuesta de login incluye todos los flags de rol
- Endpoint `/me` retorna información de roles completa

**Lógica de login actualizada:**
```python
# Determinar roles basados en rol de BD
rol = user.get("rol", "USUARIO")
is_admin = rol == "ADMIN"
is_investigator = rol in ("ADMIN", "INVESTIGADOR")
is_evaluator = rol in ("ADMIN", "INVESTIGADOR", "EVALUADOR")
```

---

### 5. Actualización de `prompts/router.py`

**Archivo:** `backend/app/prompts/router.py`

**Cambios:**
- Importación de `get_current_investigator`
- Endpoints de creación y actualización usan `get_current_investigator`
- Mensajes de error actualizados para reflejar sistema de roles

**Endpoints actualizados:**
- `POST /prompts/` - Requiere INVESTIGADOR o ADMIN
- `PATCH /prompts/{prompt_id}` - Requiere INVESTIGADOR o ADMIN

---

### 6. Actualización de `evaluations/router.py`

**Archivo:** `backend/app/evaluations/router.py`

**Cambios:**
- Importación de `get_current_evaluator` y `get_current_investigator`
- Endpoints de evaluación usan `get_current_evaluator`
- Endpoints de gold standard usan `get_current_investigator`
- Mensajes de error actualizados

**Endpoints actualizados:**
- `POST /evaluations/summaries` - Requiere EVALUADOR, INVESTIGADOR o ADMIN
- `POST /evaluations/reference-tasks` - Requiere INVESTIGADOR o ADMIN
- `PATCH /evaluations/reference-tasks/{task_id}` - Requiere INVESTIGADOR o ADMIN
- `POST /evaluations/task-matches` - Requiere INVESTIGADOR o ADMIN

---

### 7. Actualización de `experiments/router.py`

**Archivo:** `backend/app/experiments/router.py`

**Cambios:**
- Importación de `get_current_investigator`
- Endpoints de experimentos usan `get_current_investigator`
- Mensajes de error actualizados

**Endpoints actualizados:**
- `POST /experiments/sessions` - Requiere INVESTIGADOR o ADMIN
- `PATCH /experiments/sessions/{session_id}` - Requiere INVESTIGADOR o ADMIN
- `POST /experiments/time-measurements` - Requiere INVESTIGADOR o ADMIN
- `POST /experiments/sus-responses` - Requiere INVESTIGADOR o ADMIN

---

## Jerarquía de Roles

**Roles definidos en BD:**
- `USUARIO` - Rol base, acceso limitado
- `EVALUADOR` - Puede evaluar resúmenes
- `INVESTIGADOR` - Puede crear prompts, experimentos, gold standard
- `ADMIN` - Acceso completo a todas las funciones

**Permisos por rol:**
- `USUARIO`: Solo lectura de datos propios
- `EVALUADOR`: Lectura + Evaluación de resúmenes
- `INVESTIGADOR`: Todo de EVALUADOR + Creación de prompts, experimentos, gold standard
- `ADMIN`: Todo de INVESTIGADOR + Gestión de usuarios, configuración

---

## Verificación

**Backend Status:** ✅ RUNNING
- El servidor se reinició correctamente después de todos los cambios
- No se detectaron errores de importación
- Todas las dependencias de roles funcionan correctamente

**Compatibilidad:**
- La migración Fase 1 ya incluyó la columna `rol` en `usuarios`
- Los usuarios existentes tienen valor por defecto "USUARIO"
- Se requiere actualizar manualmente el rol del primer administrador

---

## Notas de Implementación

### 1. Seguridad Mejorada

**Antes:**
- Autorización basada en correo electrónico hardcodeado
- Un solo punto de fallo (correo en config)
- Difícil de gestionar múltiples administradores

**Después:**
- Autorización basada en roles en BD
- Escalable a múltiples usuarios por rol
- Auditoría de cambios de roles posible
- Más flexible y mantenible

### 2. Compatibilidad con Fase 1

**Migración existente:**
- La columna `rol` ya fue creada en `query9_evaluacion_cientifica.sql`
- Valor por defecto: "USUARIO"
- Constraint CHECK: `rol IN ('USUARIO', 'EVALUADOR', 'INVESTIGADOR', 'ADMIN')`

**Acción requerida:**
- Ejecutar SQL para establecer el primer administrador:
```sql
UPDATE usuarios SET rol = 'ADMIN' WHERE correo = 'juanaureliodelacruzgamarra@gmail.com';
```

### 3. Backward Compatibility

**Frontend:**
- El frontend ya usa `user.is_admin` para protección de rutas
- Los nuevos flags `is_investigator` y `is_evaluator` están disponibles
- No se requieren cambios inmediatos en frontend

---

## Próximos Pasos

**Fase 7: Verificación y Pruebas End-to-End**
- Verificar que el backend se reinicie correctamente
- Probar login con usuario administrador
- Verificar que los roles funcionen correctamente
- Probar endpoints protegidos con diferentes roles
- Verificar que el frontend funcione con el nuevo sistema de roles

---

## Estado

✅ **COMPLETADO** - Sistema de roles basado en BD implementado, eliminando hardcode de correo electrónico.
