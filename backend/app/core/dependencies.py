"""
Dependencias reutilizables de FastAPI.

Provee funciones que se inyectan en los endpoints para obtener el
usuario autenticado o verificar permisos de administrador.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings
from app.core.security import decode_access_token
from app.core.supabase_client import SupabaseClient, get_supabase

# Esquema Bearer – extrae el token del header Authorization
_bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    sb: SupabaseClient = Depends(get_supabase),
) -> dict:
    """
    Extrae y valida el JWT del header Authorization.

    Consulta el usuario en Supabase y retorna sus datos.
    Lanza HTTP 401 si el token es inválido o el usuario no existe.
    """
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sin identificador de usuario.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Consultar el usuario en Supabase
    rows = sb.select("usuarios", {"id": f"eq.{user_id}"})
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = rows[0]
    # Agregar flag de administrador
    user["is_admin"] = (
        user.get("correo", "").lower() == settings.ADMIN_EMAIL.lower()
    )
    return user


async def get_current_admin(
    user: dict = Depends(get_current_user),
) -> dict:
    """
    Verifica que el usuario autenticado sea administrador.

    Lanza HTTP 403 si el correo no coincide con ADMIN_EMAIL.
    """
    if not user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido a administradores.",
        )
    return user
