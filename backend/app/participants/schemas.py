"""
Esquemas Pydantic para el módulo de participantes.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr

class ParticipantCreateRequest(BaseModel):
    reunion_id: str
    correo: EmailStr
    rol: str = "participante"

class ParticipantUpdateRequest(BaseModel):
    correo: Optional[EmailStr] = None
    rol: Optional[str] = None
    estado_invitacion: Optional[str] = None

class ParticipantResponse(BaseModel):
    id: str
    reunion_id: str
    usuario_id: Optional[str] = None
    correo: str
    rol: str
    estado_invitacion: str
    fecha_creacion: Optional[str] = None
