"""
Esquemas Pydantic para el módulo de automatización (n8n).
"""

from typing import Literal, Optional
from pydantic import BaseModel

class CreateMeetingWebhookRequest(BaseModel):
    tema: str
    fecha: str
    hora: str
    duracion_minutos: int
    participantes: list[str]

class GenerateVirtualSummaryRequest(BaseModel):
    reunion_id: str

class MeetingDraft(BaseModel):
    tema: str
    fecha_inicio: str
    duracion_minutos: int = 60
    tipo: Literal["virtual", "presencial", "mixta"] = "virtual"
    direccion: Optional[str] = None
    correos: list[str] = []


class ChatRequest(BaseModel):
    mensaje: str = ""
    accion: Literal["borrador", "confirmar", "cancelar"] = "borrador"
    borrador: Optional[MeetingDraft] = None
