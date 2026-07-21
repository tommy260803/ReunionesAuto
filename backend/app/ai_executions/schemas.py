"""
Schemas Pydantic para el módulo de ejecuciones de IA.
"""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Any


class AIExecutionBase(BaseModel):
    reunion_id: str = Field(..., description="ID de la reunión")
    prompt_version_id: Optional[str] = Field(None, description="ID de la versión del prompt")
    proveedor: str = Field(..., max_length=80, description="Proveedor de IA")
    modelo: str = Field(..., max_length=120, description="Modelo utilizado")
    temperatura: Optional[float] = Field(None, description="Parámetro de temperatura")
    parametros: Optional[dict] = Field(None, description="Parámetros adicionales")
    workflow_version: Optional[str] = Field(None, max_length=50, description="Versión del workflow")
    input_hash: Optional[str] = Field(None, max_length=128, description="Hash de entrada")


class AIExecutionCreate(AIExecutionBase):
    respuesta_original: Optional[str] = None
    respuesta_procesada: Optional[dict] = None
    tokens_entrada: Optional[int] = None
    tokens_salida: Optional[int] = None
    costo_estimado: Optional[float] = None
    tiempo_ms: Optional[int] = None
    reintentos: int = Field(0, description="Número de reintentos")
    estado: str = Field(..., description="Estado de la ejecución")
    tipo_error: Optional[str] = Field(None, max_length=120)
    mensaje_error: Optional[str] = None


class AIExecutionUpdate(BaseModel):
    respuesta_original: Optional[str] = None
    respuesta_procesada: Optional[dict] = None
    tokens_entrada: Optional[int] = None
    tokens_salida: Optional[int] = None
    costo_estimado: Optional[float] = None
    tiempo_ms: Optional[int] = None
    reintentos: Optional[int] = None
    estado: Optional[str] = None
    tipo_error: Optional[str] = None
    mensaje_error: Optional[str] = None
    fecha_fin: Optional[datetime] = None


class AIExecutionResponse(AIExecutionBase):
    id: str
    respuesta_original: Optional[str]
    respuesta_procesada: Optional[dict]
    tokens_entrada: Optional[int]
    tokens_salida: Optional[int]
    costo_estimado: Optional[float]
    tiempo_ms: Optional[int]
    reintentos: int
    estado: str
    tipo_error: Optional[str]
    mensaje_error: Optional[str]
    iniciado_por: Optional[str]
    fecha_inicio: datetime
    fecha_fin: Optional[datetime]

    class Config:
        from_attributes = True


class AIExecutionListResponse(BaseModel):
    id: str
    reunion_id: str
    prompt_version_id: Optional[str]
    proveedor: str
    modelo: str
    estado: str
    fecha_inicio: datetime
    fecha_fin: Optional[datetime]
    tiempo_ms: Optional[int]

    class Config:
        from_attributes = True
