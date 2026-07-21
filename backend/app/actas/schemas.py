"""
Esquemas Pydantic para el módulo de actas.
"""

from typing import Optional
from pydantic import BaseModel


class ActaCreateRequest(BaseModel):
    reunion_id: str
    titulo: Optional[str] = "Acta de Reunión"
    tipo_reunion: Optional[str] = "virtual"
    participantes: Optional[str] = None
    orden_dia: Optional[str] = None
    observaciones: Optional[str] = None


class ActaUpdateRequest(BaseModel):
    titulo: Optional[str] = None
    contenido: Optional[str] = None
    estado: Optional[str] = None
    participantes: Optional[str] = None
    orden_dia: Optional[str] = None
    decisiones: Optional[str] = None
    tareas_extraidas: Optional[str] = None
    proximos_pasos: Optional[str] = None
    observaciones: Optional[str] = None


class ActaResponse(BaseModel):
    id: str
    reunion_id: str
    numero: Optional[int] = None
    titulo: str
    tipo_reunion: str
    contenido: Optional[str] = None
    formato_origen: str
    estado: str
    fecha_reunion: Optional[str] = None
    participantes: Optional[str] = None
    orden_dia: Optional[str] = None
    decisiones: Optional[str] = None
    tareas_extraidas: Optional[str] = None
    proximos_pasos: Optional[str] = None
    observaciones: Optional[str] = None
    fecha_creacion: Optional[str] = None
    fecha_actualizacion: Optional[str] = None


class ActaListResponse(BaseModel):
    id: str
    reunion_id: str
    numero: Optional[int] = None
    titulo: str
    tipo_reunion: str
    formato_origen: str
    estado: str
    fecha_reunion: Optional[str] = None
    fecha_creacion: Optional[str] = None


class ActaGenerateRequest(BaseModel):
    reunion_id: str
    titulo: Optional[str] = "Acta de Reunión"
    participantes: Optional[str] = None
    orden_dia: Optional[str] = None
    observaciones: Optional[str] = None
