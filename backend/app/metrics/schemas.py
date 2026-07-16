"""
Esquemas Pydantic para el módulo de métricas.
"""

from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class N8nMetricResponse(BaseModel):
    id: str
    endpoint: str
    tiempo_respuesta: float
    estado: str
    fecha: str
    codigo_estado: Optional[int] = None
    reunion_id: Optional[str] = None
    tamano_respuesta: Optional[int] = None
    detalles: Optional[str] = None


class MetricDailyCount(BaseModel):
    fecha: str
    cantidad: int


class EndpointLatency(BaseModel):
    endpoint: str
    tiempo_promedio: float
    cantidad: int


class N8nMetricsStatsResponse(BaseModel):
    total_peticiones: int
    exitosas: int
    fallidas: int
    tasa_exito: float
    tiempo_promedio: float
    por_dia: List[MetricDailyCount]
    por_endpoint: List[EndpointLatency]
    logs: List[N8nMetricResponse]
