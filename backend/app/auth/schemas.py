"""
Esquemas Pydantic para el módulo de autenticación.

Define los modelos de request y response utilizados en los endpoints
de login, registro y consulta de usuario.
"""

from pydantic import BaseModel, EmailStr, Field


# ------------------------------------------------------------------
# Requests
# ------------------------------------------------------------------

class LoginRequest(BaseModel):
    """Cuerpo de la petición de inicio de sesión."""

    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    password: str = Field(..., min_length=1, description="Contraseña del usuario")


class RegisterRequest(BaseModel):
    """Cuerpo de la petición de registro."""

    email: EmailStr = Field(..., description="Correo electrónico del nuevo usuario")
    password: str = Field(..., min_length=6, description="Contraseña (mínimo 6 caracteres)")
    nombre: str = Field(..., min_length=1, description="Nombre completo del usuario")


# ------------------------------------------------------------------
# Responses
# ------------------------------------------------------------------

class UserResponse(BaseModel):
    """Datos públicos del usuario."""

    id: str
    correo: str
    nombre: str
    nivel_suscripcion: str
    estado_suscripcion: str
    rol: str = "USUARIO"
    is_admin: bool = False
    is_investigator: bool = False
    is_evaluator: bool = False


class TokenResponse(BaseModel):
    """Respuesta de autenticación exitosa con token JWT."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
