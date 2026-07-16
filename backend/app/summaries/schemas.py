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
