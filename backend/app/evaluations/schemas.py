"""
Schemas Pydantic para el módulo de evaluaciones de resúmenes.
"""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class SummaryEvaluationBase(BaseModel):
    reunion_id: str = Field(..., description="ID de la reunión")
    summary_version_id: str = Field(..., description="ID de la versión del resumen")
    evaluador_id: str = Field(..., description="ID del evaluador")
    fidelidad: Optional[int] = Field(None, ge=1, le=5, description="Fidelidad (1-5)")
    cobertura: Optional[int] = Field(None, ge=1, le=5, description="Cobertura (1-5)")
    claridad: Optional[int] = Field(None, ge=1, le=5, description="Claridad (1-5)")
    coherencia: Optional[int] = Field(None, ge=1, le=5, description="Coherencia (1-5)")
    concision: Optional[int] = Field(None, ge=1, le=5, description="Concisión (1-5)")
    utilidad: Optional[int] = Field(None, ge=1, le=5, description="Utilidad (1-5)")
    acuerdos_correctos: Optional[int] = Field(None, ge=1, le=5, description="Acuerdos correctos (1-5)")
    responsables_correctos: Optional[int] = Field(None, ge=1, le=5, description="Responsables correctos (1-5)")
    fechas_correctas: Optional[int] = Field(None, ge=1, le=5, description="Fechas correctas (1-5)")
    omisiones: int = Field(0, ge=0, description="Conteo de omisiones")
    afirmaciones_no_respaldadas: int = Field(0, ge=0, description="Afirmaciones sin evidencia")
    contradicciones: int = Field(0, ge=0, description="Contradicciones detectadas")
    aprobado_sin_cambios: Optional[bool] = Field(None, description="Aprobado sin editar")
    observaciones: Optional[str] = Field(None, description="Comentarios del evaluador")


class SummaryEvaluationCreate(SummaryEvaluationBase):
    pass


class SummaryEvaluationUpdate(BaseModel):
    fidelidad: Optional[int] = Field(None, ge=1, le=5)
    cobertura: Optional[int] = Field(None, ge=1, le=5)
    claridad: Optional[int] = Field(None, ge=1, le=5)
    coherencia: Optional[int] = Field(None, ge=1, le=5)
    concision: Optional[int] = Field(None, ge=1, le=5)
    utilidad: Optional[int] = Field(None, ge=1, le=5)
    acuerdos_correctos: Optional[int] = Field(None, ge=1, le=5)
    responsables_correctos: Optional[int] = Field(None, ge=1, le=5)
    fechas_correctas: Optional[int] = Field(None, ge=1, le=5)
    omisiones: Optional[int] = Field(None, ge=0)
    afirmaciones_no_respaldadas: Optional[int] = Field(None, ge=0)
    contradicciones: Optional[int] = Field(None, ge=0)
    aprobado_sin_cambios: Optional[bool] = None
    observaciones: Optional[str] = None


class SummaryEvaluationResponse(SummaryEvaluationBase):
    id: str
    fecha_evaluacion: datetime

    class Config:
        from_attributes = True


class SummaryEvaluationListResponse(BaseModel):
    id: str
    reunion_id: str
    summary_version_id: str
    evaluador_id: str
    fidelidad: Optional[int]
    cobertura: Optional[int]
    claridad: Optional[int]
    coherencia: Optional[int]
    concision: Optional[int]
    utilidad: Optional[int]
    acuerdos_correctos: Optional[int]
    responsables_correctos: Optional[int]
    fechas_correctas: Optional[int]
    omisiones: int
    afirmaciones_no_respaldadas: int
    contradicciones: int
    aprobado_sin_cambios: Optional[bool]
    fecha_evaluacion: datetime

    class Config:
        from_attributes = True


class ReferenceTaskBase(BaseModel):
    reunion_id: str = Field(..., description="ID de la reunión")
    descripcion: str = Field(..., description="Descripción de la tarea")
    responsable_referencia: Optional[str] = Field(None, description="Responsable correcto")
    fecha_limite_referencia: Optional[str] = Field(None, description="Fecha límite correcta")
    validado: bool = Field(False, description="Si está validado como gold standard")


class ReferenceTaskCreate(ReferenceTaskBase):
    pass


class ReferenceTaskUpdate(BaseModel):
    descripcion: Optional[str] = None
    responsable_referencia: Optional[str] = None
    fecha_limite_referencia: Optional[str] = None
    validado: Optional[bool] = None


class ReferenceTaskResponse(ReferenceTaskBase):
    id: str
    creado_por: str
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class TaskMatchBase(BaseModel):
    reunion_id: str = Field(..., description="ID de la reunión")
    ai_execution_id: Optional[str] = Field(None, description="ID de ejecución IA")
    reference_task_id: str = Field(..., description="ID de tarea de referencia")
    detected_task_id: Optional[str] = Field(None, description="ID de tarea detectada")
    resultado: str = Field(..., description="TP, FP, FN, TN")
    similitud: Optional[float] = Field(None, ge=0, le=1, description="Puntuación de similitud")
    observaciones: Optional[str] = None


class TaskMatchCreate(TaskMatchBase):
    validado_por: Optional[str] = Field(None, description="ID de usuario que validó")


class TaskMatchResponse(TaskMatchBase):
    id: str
    validado_por: Optional[str]
    fecha_registro: datetime

    class Config:
        from_attributes = True
