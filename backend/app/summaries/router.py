"""
Router de resúmenes.

Permite consultar los resúmenes generados para las reuniones.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.summaries.schemas import SummaryResponse
from app.core.dependencies import get_current_user
from app.core.supabase_client import SupabaseClient, get_supabase

router = APIRouter(prefix="/summaries", tags=["Resúmenes"])

@router.get("/meeting/{meeting_id}", response_model=SummaryResponse, summary="Obtener el resumen de una reunión")
async def get_meeting_summary(
    meeting_id: str,
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase)
):
    """
    Retorna el resumen de una reunión, si existe. 
    Usado por el frontend para mostrar el resumen o hacer polling después de enviar un PDF.
    """
    rows = sb.select(
        "resumenes", 
        {
            "select": "id,reunion_id,resumen,fecha_creacion",
            "reunion_id": f"eq.{meeting_id}"
        }
    )
    
    if not rows or not rows[0].get("resumen"):
        raise HTTPException(status_code=404, detail="Resumen no encontrado o aún en proceso.")
        
    row = rows[0]
    return SummaryResponse(
        id=str(row["id"]),
        reunion_id=str(row["reunion_id"]),
        resumen=row["resumen"],
        fecha_creacion=row.get("fecha_creacion")
    )
