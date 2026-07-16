"""
Esquemas Pydantic para el módulo de tareas.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr

class TaskCreateRequest(BaseModel):
    reunion_id: str
    descripcion: str
    asignado_a_correo: Optional[EmailStr] = None
    estado: str = "pendiente"
    fecha_vencimiento: Optional[str] = None

class TaskUpdateRequest(BaseModel):
    descripcion: Optional[str] = None
    asignado_a_correo: Optional[EmailStr] = None
    estado: Optional[str] = None
    fecha_vencimiento: Optional[str] = None

class TaskResponse(BaseModel):
    id: str
    reunion_id: str
    descripcion: str
    asignado_a_correo: Optional[str] = None
    estado: str
    fecha_vencimiento: Optional[str] = None
    fecha_creacion: Optional[str] = None
    reunion_nombre: Optional[str] = None

class TasksMetricsResponse(BaseModel):
    total: int
    completadas: int
    pendientes: int
    en_progreso: int
    atrasadas: int
    porcentaje_avance: float
