"""
Esquemas Pydantic para el módulo de reuniones.
"""

from typing import Optional
from pydantic import BaseModel, HttpUrl

class MeetingUpdateRequest(BaseModel):
    tema: Optional[str] = None
    fecha_inicio: Optional[str] = None
    duracion_minutos: Optional[int] = None
    tipo: Optional[str] = None
    direccion: Optional[str] = None
    estado: Optional[str] = None
    join_url: Optional[str] = None
    start_url: Optional[str] = None
    id_externo: Optional[str] = None

class MeetingResponse(BaseModel):
    id: str
    tema: Optional[str] = None
    fecha_inicio: Optional[str] = None
    duracion_minutos: Optional[int] = None
    proveedor: Optional[str] = None
    id_externo: Optional[str] = None
    join_url: Optional[str] = None
    start_url: Optional[str] = None
    estado: Optional[str] = None
    creador_id: Optional[str] = None
    tipo: Optional[str] = None
    direccion: Optional[str] = None
