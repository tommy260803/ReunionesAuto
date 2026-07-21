"""
Schemas Pydantic para el módulo de experimentos.
"""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class ExperimentSessionBase(BaseModel):
    nombre: str = Field(..., max_length=160, description="Nombre del experimento")
    descripcion: Optional[str] = Field(None, description="Descripción detallada")
    investigador_id: str = Field(..., description="ID del investigador")
    condicion: str = Field(..., max_length=80, description="Condición experimental")
    prompt_version_id: Optional[str] = Field(None, description="ID de versión de prompt")
    modelo: Optional[str] = Field(None, max_length=120, description="Modelo utilizado")
    configuracion: Optional[dict] = Field(None, description="Configuración adicional")
    estado: str = Field("PLANIFICADO", description="Estado del experimento")


class ExperimentSessionCreate(ExperimentSessionBase):
    pass


class ExperimentSessionUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=160)
    descripcion: Optional[str] = None
    condicion: Optional[str] = Field(None, max_length=80)
    prompt_version_id: Optional[str] = None
    modelo: Optional[str] = Field(None, max_length=120)
    configuracion: Optional[dict] = None
    estado: Optional[str] = None
    fecha_fin: Optional[datetime] = None


class ExperimentSessionResponse(ExperimentSessionBase):
    id: str
    fecha_inicio: datetime
    fecha_fin: Optional[datetime]

    class Config:
        from_attributes = True


class ExperimentSessionListResponse(BaseModel):
    id: str
    nombre: str
    descripcion: Optional[str]
    investigador_id: str
    condicion: str
    prompt_version_id: Optional[str]
    modelo: Optional[str]
    estado: str
    fecha_inicio: datetime
    fecha_fin: Optional[datetime]

    class Config:
        from_attributes = True


class TimeMeasurementBase(BaseModel):
    experiment_session_id: Optional[str] = Field(None, description="ID de sesión experimental")
    reunion_id: str = Field(..., description="ID de la reunión")
    participante_id: Optional[str] = Field(None, description="ID del participante")
    condicion: str = Field(..., description="Condición experimental")
    tiempo_elaboracion_segundos: Optional[int] = Field(None, ge=0, description="Tiempo de elaboración")
    tiempo_revision_segundos: Optional[int] = Field(None, ge=0, description="Tiempo de revisión")
    tiempo_total_segundos: Optional[int] = Field(None, ge=0, description="Tiempo total")
    errores_detectados: int = Field(0, ge=0, description="Errores detectados")


class TimeMeasurementCreate(TimeMeasurementBase):
    pass


class TimeMeasurementResponse(TimeMeasurementBase):
    id: str
    fecha_registro: datetime

    class Config:
        from_attributes = True


class SusResponseBase(BaseModel):
    experiment_session_id: Optional[str] = Field(None, description="ID de sesión experimental")
    usuario_id: str = Field(..., description="ID del usuario")
    q1: int = Field(..., ge=1, le=5, description="Pregunta 1")
    q2: int = Field(..., ge=1, le=5, description="Pregunta 2")
    q3: int = Field(..., ge=1, le=5, description="Pregunta 3")
    q4: int = Field(..., ge=1, le=5, description="Pregunta 4")
    q5: int = Field(..., ge=1, le=5, description="Pregunta 5")
    q6: int = Field(..., ge=1, le=5, description="Pregunta 6")
    q7: int = Field(..., ge=1, le=5, description="Pregunta 7")
    q8: int = Field(..., ge=1, le=5, description="Pregunta 8")
    q9: int = Field(..., ge=1, le=5, description="Pregunta 9")
    q10: int = Field(..., ge=1, le=5, description="Pregunta 10")
    observaciones: Optional[str] = Field(None, description="Comentarios")


class SusResponseCreate(SusResponseBase):
    pass


class SusResponseResponse(SusResponseBase):
    id: str
    puntaje_sus: Optional[float]
    fecha_registro: datetime

    class Config:
        from_attributes = True
