"""
Esquemas Pydantic para el módulo de usuarios.

Define los modelos de request y response utilizados en los endpoints
de consulta y modificación de usuarios.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# ------------------------------------------------------------------
# Requests
# ------------------------------------------------------------------

class UserUpdateRequest(BaseModel):
    """Cuerpo de la petición para actualizar un usuario."""

    nombre: Optional[str] = Field(None, description="Nombre completo del usuario")
    correo: Optional[EmailStr] = Field(None, description="Correo electrónico del usuario")
    nivel_suscripcion: Optional[str] = Field(None, description="Nivel de suscripción (ej. basico, pro, enterprise)")
    estado_suscripcion: Optional[str] = Field(None, description="Estado de suscripción (ej. activo, suspendido, cancelado)")


# ------------------------------------------------------------------
# Responses
# ------------------------------------------------------------------

class UserDetailResponse(BaseModel):
    """Datos detallados del usuario para respuestas de la API."""

    id: str
    correo: str
    nombre: str
    nivel_suscripcion: str
    estado_suscripcion: str
    fecha_creacion: Optional[str] = None
    is_admin: bool = False
