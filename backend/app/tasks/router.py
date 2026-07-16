"""
Router de tareas.

Replica la lógica de view_tareas.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime

from app.tasks.schemas import TaskResponse, TaskCreateRequest, TaskUpdateRequest, TasksMetricsResponse
from app.core.dependencies import get_current_user, get_current_admin
from app.core.supabase_client import SupabaseClient, get_supabase

router = APIRouter(prefix="/tasks", tags=["Tareas"])

@router.get("", response_model=List[TaskResponse], summary="Listar tareas")
async def list_tasks(
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase)
):
    """
    Lista todas las tareas, incluyendo el nombre de la reunión asociada.
    """
    tareas = sb.select(
        "tareas", 
        {"select": "id,reunion_id,descripcion,asignado_a_correo,estado,fecha_vencimiento,fecha_creacion"}
    )
    
    if not tareas:
        return []

    reuniones_ids = list(set(t['reunion_id'] for t in tareas))
    reuniones_info = {}
    
    # Procesar en lotes (como en Streamlit) o todo de una vez si es simple
    if reuniones_ids:
        params = {
            "select": "id,tema,fecha_inicio",
            "id": f"in.({','.join(str(r) for r in reuniones_ids)})"
        }
        reuniones = sb.select("reuniones", params)
        for r in reuniones:
            fecha_str = r.get('fecha_inicio', '').split('T')[0] if r.get('fecha_inicio') else 'Sin fecha'
            reuniones_info[str(r['id'])] = f"{r.get('tema', 'Sin tema')} ({fecha_str})"
            
    response = []
    for t in tareas:
        response.append(TaskResponse(
            id=str(t["id"]),
            reunion_id=str(t["reunion_id"]),
            descripcion=t.get("descripcion", ""),
            asignado_a_correo=t.get("asignado_a_correo"),
            estado=t.get("estado", "pendiente"),
            fecha_vencimiento=t.get("fecha_vencimiento"),
            fecha_creacion=t.get("fecha_creacion"),
            reunion_nombre=reuniones_info.get(str(t["reunion_id"]), "Reunión desconocida")
        ))
    return response

@router.get("/metrics", response_model=TasksMetricsResponse, summary="Obtener métricas de tareas")
async def get_tasks_metrics(
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase)
):
    """
    Calcula métricas generales de las tareas (total, pendientes, atrasadas).
    """
    tareas = sb.select("tareas", {"select": "estado,fecha_vencimiento"})
    
    total = len(tareas)
    completadas = 0
    pendientes = 0
    en_progreso = 0
    atrasadas = 0
    
    hoy = datetime.now().date()
    
    for t in tareas:
        estado = t.get("estado", "pendiente").replace(" ", "_")
        if estado == "completada":
            completadas += 1
        elif estado == "pendiente":
            pendientes += 1
        elif estado == "en_progreso":
            en_progreso += 1
            
        fecha_venc = t.get("fecha_vencimiento")
        if fecha_venc and estado != "completada":
            try:
                # Truncar la Z o la parte de tiempo si existe
                fecha_venc_str = fecha_venc.split("T")[0]
                fecha_venc_dt = datetime.strptime(fecha_venc_str, "%Y-%m-%d").date()
                if fecha_venc_dt < hoy:
                    atrasadas += 1
            except ValueError:
                pass
                
    porcentaje = (completadas / total * 100) if total > 0 else 0.0
    
    return TasksMetricsResponse(
        total=total,
        completadas=completadas,
        pendientes=pendientes,
        en_progreso=en_progreso,
        atrasadas=atrasadas,
        porcentaje_avance=porcentaje
    )

@router.post("", response_model=dict, summary="Crear tarea", status_code=201)
async def create_task(
    body: TaskCreateRequest,
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase)
):
    try:
        sb.insert("tareas", [{
            "reunion_id": body.reunion_id,
            "descripcion": body.descripcion,
            "asignado_a_correo": body.asignado_a_correo,
            "estado": body.estado.replace(" ", "_"),
            "fecha_vencimiento": body.fecha_vencimiento
        }])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "Tarea creada exitosamente."}

@router.patch("/{task_id}", response_model=dict, summary="Actualizar tarea")
async def update_task(
    task_id: str,
    body: TaskUpdateRequest,
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase)
):
    update_data = body.model_dump(exclude_unset=True)
    if update_data.get("estado"):
        update_data["estado"] = update_data["estado"].replace(" ", "_")
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    try:
        sb.update("tareas", data=update_data, params={"id": f"eq.{task_id}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "Tarea actualizada."}

@router.delete("/{task_id}", response_model=dict, summary="Eliminar tarea (solo admin)")
async def delete_task(
    task_id: str,
    admin: dict = Depends(get_current_admin),
    sb: SupabaseClient = Depends(get_supabase)
):
    try:
        sb.delete("tareas", params={"id": f"eq.{task_id}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "Tarea eliminada exitosamente."}
