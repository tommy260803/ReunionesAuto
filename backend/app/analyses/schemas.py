"""Schemas Pydantic para el módulo de análisis estadístico."""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class StatisticalAnalysisCreate(BaseModel):
    """Schema para crear un nuevo análisis estadístico."""
    
    nombre: str = Field(..., min_length=1, max_length=180, description="Nombre del análisis")
    objetivo: str | None = Field(None, description="Objetivo del análisis")
    variable_resultado: str = Field(..., max_length=120, description="Variable de resultado")
    variable_grupo: str | None = Field(None, max_length=120, description="Variable de agrupación")
    diseno: Literal["INDEPENDIENTE", "PAREADO", "MEDIDAS_REPETIDAS"] = Field(
        ..., description="Diseño del análisis"
    )
    prueba_solicitada: str | None = Field(None, max_length=80, description="Prueba solicitada")
    alpha: float = Field(default=0.05, ge=0.001, le=0.999, description="Nivel de significancia")
    correccion_multiple: Literal["BONFERRONI", "HOLM", "NONE"] | None = Field(
        default=None, description="Corrección por comparaciones múltiples"
    )
    filtros: dict[str, Any] = Field(default_factory=dict, description="Filtros aplicados")
    configuracion: dict[str, Any] = Field(default_factory=dict, description="Configuración adicional")


class StatisticalAnalysisUpdate(BaseModel):
    """Schema para actualizar un análisis estadístico."""
    
    nombre: str | None = Field(None, min_length=1, max_length=180)
    objetivo: str | None = None
    prueba_solicitada: str | None = Field(None, max_length=80)
    alpha: float | None = Field(None, ge=0.001, le=0.999)
    correccion_multiple: Literal["BONFERRONI", "HOLM", "NONE"] | None = None
    filtros: dict[str, Any] | None = None
    configuracion: dict[str, Any] | None = None
    estado: Literal["PLANIFICADO", "VALIDADO", "EJECUTANDO", "COMPLETADO", "ERROR", "CANCELADO"] | None = None


class StatisticalAnalysisResponse(BaseModel):
    """Schema para respuesta de análisis estadístico."""
    
    id: UUID
    experiment_session_id: UUID | None
    nombre: str
    objetivo: str | None
    variable_resultado: str
    variable_grupo: str | None
    diseno: str
    prueba_solicitada: str | None
    prueba_ejecutada: str
    alpha: float
    correccion_multiple: str | None
    filtros: dict[str, Any]
    configuracion: dict[str, Any]
    estado: str
    datos_hash: str | None
    codigo_version: str | None
    creado_por: UUID
    fecha_creacion: datetime
    fecha_ejecucion: datetime | None
    
    class Config:
        from_attributes = True


class DataQualityValidationRequest(BaseModel):
    """Schema para solicitud de validación de calidad de datos."""
    
    data: dict[str, Any] = Field(..., description="Datos a validar")
    test_type: str = Field(..., description="Tipo de prueba estadística")
    design: Literal["independent", "paired", "repeated_measures"] = Field(
        default="independent", description="Diseño del análisis"
    )
    min_observations: int = Field(default=5, ge=1, description="Mínimo de observaciones requeridas")


class DataQualityValidationResponse(BaseModel):
    """Schema para respuesta de validación de calidad de datos."""
    
    status: Literal["ok", "warnings", "invalid_data", "insufficient_data"]
    reason: str | None
    can_proceed: bool
    warnings: list[str]
    errors: list[str]
    quality_report: dict[str, Any]
    test_type: str
    design: str


class AnalysisExecutionRequest(BaseModel):
    """Schema para solicitud de ejecución de análisis."""
    
    analysis_id: UUID = Field(..., description="ID del análisis a ejecutar")


class AnalysisResultResponse(BaseModel):
    """Schema para respuesta de resultados de análisis."""
    
    id: UUID
    analysis_id: UUID
    resultado: dict[str, Any]
    descriptivos: dict[str, Any] | None
    supuestos: dict[str, Any] | None
    efecto: dict[str, Any] | None
    intervalos: dict[str, Any] | None
    advertencias: dict[str, Any] | None
    interpretacion: str | None
    fecha_registro: datetime
    
    class Config:
        from_attributes = True


class AnalysisRerunRequest(BaseModel):
    """Schema para solicitud de reejecución de análisis."""
    
    force: bool = Field(default=False, description="Forzar reejecución aunque los datos no hayan cambiado")
