"""
Esquemas Pydantic para el módulo de resúmenes.
"""

from typing import Optional
from pydantic import BaseModel

class SummaryResponse(BaseModel):
    id: str
    reunion_id: str
    resumen: str
    fecha_creacion: Optional[str] = None


class SummaryDetailResponse(BaseModel):
    resumen_ejecutivo: Optional[str] = None
    decisiones: Optional[str] = None
    riesgos: Optional[str] = None
    proximos_pasos: Optional[str] = None
    fecha_actualizacion: Optional[str] = None
