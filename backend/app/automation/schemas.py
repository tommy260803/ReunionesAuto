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


class SummaryCallbackPayload(BaseModel):
    job_id: str
    estado: Literal["finalizado", "error"] = "finalizado"
    resumen: Optional[str] = None
    resumen_ejecutivo: Optional[str] = None
    decisiones: Optional[str] = None
    riesgos: Optional[str] = None
    proximos_pasos: Optional[str] = None
    tareas: list[dict] = []
    error_detalle: Optional[str] = None


class ZoomRecordingRequest(BaseModel):
    reunion_id: str


class SummaryJobStatus(BaseModel):
    id: str
    reunion_id: str
    estado: str
    fuente: str
    resumen_texto: Optional[str] = None
    error_detalle: Optional[str] = None
    fecha_actualizacion: Optional[str] = None
