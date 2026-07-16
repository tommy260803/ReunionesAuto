"""
Router de reuniones.

Replica la vista view_reuniones.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.meetings.schemas import MeetingResponse, MeetingUpdateRequest
from app.core.dependencies import get_current_user, get_current_admin
from app.core.supabase_client import SupabaseClient, get_supabase

router = APIRouter(prefix="/meetings", tags=["Reuniones"])

@router.get("", response_model=List[MeetingResponse], summary="Listar reuniones")
async def list_meetings(
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase)
):
    """
    Lista todas las reuniones. 
    En un entorno real, los usuarios no admin solo verían sus reuniones.
    Por ahora, según el app.py, se extraen todas.
    """
    rows = sb.select(
        "reuniones", 
        {
            "select": "id,tema,fecha_inicio,duracion_minutos,proveedor,id_externo,join_url,start_url,estado,creador_id,tipo,direccion",
            "order": "fecha_creacion.desc"
        }
    )
    return [MeetingResponse(**row) for row in rows]

@router.get("/{meeting_id}", response_model=MeetingResponse, summary="Detalle de reunión")
async def get_meeting(
    meeting_id: str,
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase)
):
    rows = sb.select(
        "reuniones", 
        {
            "select": "id,tema,fecha_inicio,duracion_minutos,proveedor,id_externo,join_url,start_url,estado,creador_id,tipo,direccion",
            "id": f"eq.{meeting_id}"
        }
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Reunión no encontrada")
    return MeetingResponse(**rows[0])

@router.patch("/{meeting_id}", response_model=dict, summary="Actualizar reunión (solo admin)")
async def update_meeting(
    meeting_id: str,
    body: MeetingUpdateRequest,
    admin: dict = Depends(get_current_admin),
    sb: SupabaseClient = Depends(get_supabase)
):
    update_data = body.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    try:
        sb.update("reuniones", data=update_data, params={"id": f"eq.{meeting_id}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "Reunión actualizada"}


@router.delete("/{meeting_id}", response_model=dict, summary="Eliminar reunión (solo admin)")
async def delete_meeting(
    meeting_id: str,
    admin: dict = Depends(get_current_admin),
    sb: SupabaseClient = Depends(get_supabase),
):
    try:
        sb.delete("reuniones", params={"id": f"eq.{meeting_id}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "Reunión eliminada"}
