"""
Utilidades de seguridad: hashing de contraseñas y manejo de JWT.

Usa passlib.hash.bcrypt para el hashing (mismo mecanismo que el
app.py de Streamlit) y python-jose para la creación/verificación
de tokens JWT.
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.hash import bcrypt

from app.core.config import settings


# ------------------------------------------------------------------
# Hashing de contraseñas
# ------------------------------------------------------------------

def hash_password(plain_password: str) -> str:
    """Genera un hash bcrypt a partir de una contraseña en texto plano."""
    return bcrypt.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica que una contraseña en texto plano coincida con su hash."""
    return bcrypt.verify(plain_password, hashed_password)


# ------------------------------------------------------------------
# Tokens JWT
# ------------------------------------------------------------------

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Crea un token JWT firmado.

    El payload incluye los datos proporcionados más un campo 'exp'
    con la fecha de expiración.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict | None:
    """
    Decodifica y valida un token JWT.

    Retorna el payload si el token es válido, o None si es inválido
    o ha expirado.
    """
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError:
        return None
