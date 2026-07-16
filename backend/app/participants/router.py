"""
Router de participantes.

Replica la lógica de view_participantes.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.participants.schemas import ParticipantResponse, ParticipantCreateRequest, ParticipantUpdateRequest
from app.core.dependencies import get_current_user, get_current_admin
from app.core.supabase_client import SupabaseClient, get_supabase

router = APIRouter(prefix="/participants", tags=["Participantes"])

@router.get("/meeting/{meeting_id}", response_model=List[ParticipantResponse], summary="Listar participantes de una reunión")
async def list_participants(
    meeting_id: str,
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase)
):
    """
    Lista los participantes de una reunión específica.
    """
    rows = sb.select(
        "participantes", 
        {
            "select": "id,usuario_id,correo,rol,estado_invitacion,fecha_creacion,reunion_id",
            "reunion_id": f"eq.{meeting_id}"
        }
    )
    return [ParticipantResponse(
        id=str(row["id"]),
        reunion_id=str(row["reunion_id"]),
        usuario_id=str(row.get("usuario_id")) if row.get("usuario_id") else None,
        correo=row["correo"],
        rol=row.get("rol", "participante"),
        estado_invitacion=row.get("estado_invitacion", "enviado"),
        fecha_creacion=row.get("fecha_creacion")
    ) for row in rows]

@router.post("", response_model=dict, summary="Agregar participante (solo admin)", status_code=201)
async def add_participant(
    body: ParticipantCreateRequest,
    admin: dict = Depends(get_current_admin),
    sb: SupabaseClient = Depends(get_supabase)
):
    try:
        sb.insert("participantes", [{
            "reunion_id": body.reunion_id,
            "correo": body.correo,
            "rol": body.rol,
            "estado_invitacion": "enviado"
        }])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "Participante agregado exitosamente."}

@router.patch("/{participant_id}", response_model=dict, summary="Actualizar participante (solo admin)")
async def update_participant(
    participant_id: str,
    body: ParticipantUpdateRequest,
    admin: dict = Depends(get_current_admin),
    sb: SupabaseClient = Depends(get_supabase)
):
    update_data = body.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    try:
        sb.update("participantes", data=update_data, params={"id": f"eq.{participant_id}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "Participante actualizado."}

@router.delete("/{participant_id}", response_model=dict, summary="Eliminar participante (solo admin)")
async def delete_participant(
    participant_id: str,
    admin: dict = Depends(get_current_admin),
    sb: SupabaseClient = Depends(get_supabase)
):
    try:
        sb.delete("participantes", params={"id": f"eq.{participant_id}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "Participante eliminado exitosamente."}
