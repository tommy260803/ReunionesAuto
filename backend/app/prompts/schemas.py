"""
Schemas Pydantic para el módulo de prompts.
"""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class PromptVersionBase(BaseModel):
    nombre: str = Field(..., max_length=120, description="Nombre del prompt")
    version: str = Field(..., max_length=30, description="Versión semántica")
    contenido: str = Field(..., description="Contenido completo del prompt")
    objetivo: Optional[str] = Field(None, description="Descripción del propósito")
    proveedor: Optional[str] = Field(None, max_length=80, description="Proveedor de IA")
    modelo_recomendado: Optional[str] = Field(None, max_length=120, description="Modelo recomendado")
    activo: bool = Field(True, description="Si está activo para uso")


class PromptVersionCreate(PromptVersionBase):
    pass


class PromptVersionUpdate(BaseModel):
    contenido: Optional[str] = None
    objetivo: Optional[str] = None
    proveedor: Optional[str] = None
    modelo_recomendado: Optional[str] = None
    activo: Optional[bool] = None


class PromptVersionResponse(PromptVersionBase):
    id: str
    creado_por: Optional[str] = None
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class PromptVersionListResponse(BaseModel):
    id: str
    nombre: str
    version: str
    objetivo: Optional[str]
    proveedor: Optional[str]
    modelo_recomendado: Optional[str]
    activo: bool
    creado_por: Optional[str]
    fecha_creacion: datetime

    class Config:
        from_attributes = True
