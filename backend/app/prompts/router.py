"""
Router de gestión de versiones de prompts.

Permite crear, listar, actualizar y desactivar versiones de prompts
para experimentos y ejecuciones de IA.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.core.dependencies import get_current_user, get_current_investigator
from app.core.supabase_client import SupabaseClient, get_supabase
from app.prompts.schemas import (
    PromptVersionCreate,
    PromptVersionUpdate,
    PromptVersionResponse,
    PromptVersionListResponse,
)

router = APIRouter(prefix="/prompts", tags=["Prompts"])


@router.post(
    "/",
    response_model=PromptVersionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva versión de prompt"
)
async def create_prompt(
    body: PromptVersionCreate,
    user: dict = Depends(get_current_investigator),
    sb: SupabaseClient = Depends(get_supabase),
) -> PromptVersionResponse:
    """
    Crea una nueva versión de prompt.
    
    Requiere rol de INVESTIGADOR o ADMIN.
    """
    # Verificar rol (ahora basado en BD)
    if not user.get("is_investigator"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo investigadores y administradores pueden crear prompts.",
        )
    
    # Verificar que no exista la combinación nombre+versión
    existing = sb.select(
        "prompt_versions",
        {
            "nombre": f"eq.{body.nombre}",
            "version": f"eq.{body.version}",
        },
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una versión con este nombre y número de versión.",
        )
    
    # Crear prompt
    new_prompt = {
        "nombre": body.nombre,
        "version": body.version,
        "contenido": body.contenido,
        "objetivo": body.objetivo,
        "proveedor": body.proveedor,
        "modelo_recomendado": body.modelo_recomendado,
        "activo": body.activo,
        "creado_por": user["id"],
    }
    
    result = sb.insert("prompt_versions", [new_prompt])
    
    if not result or isinstance(result, dict) and "status" in result:
        # Si la inserción fue exitosa pero no retornó datos, consultar el creado
        created = sb.select(
            "prompt_versions",
            {
                "nombre": f"eq.{body.nombre}",
                "version": f"eq.{body.version}",
                "limit": "1",
            },
        )
        if created:
            row = created[0]
            return PromptVersionResponse(
                id=str(row["id"]),
                nombre=row["nombre"],
                version=row["version"],
                contenido=row["contenido"],
                objetivo=row.get("objetivo"),
                proveedor=row.get("proveedor"),
                modelo_recomendado=row.get("modelo_recomendado"),
                activo=row["activo"],
                creado_por=str(row["creado_por"]) if row.get("creado_por") else None,
                fecha_creacion=row["fecha_creacion"],
            )
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Error al crear el prompt.",
    )


@router.get(
    "/",
    response_model=List[PromptVersionListResponse],
    summary="Listar versiones de prompts"
)
async def list_prompts(
    activo_only: bool = False,
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase),
) -> List[PromptVersionListResponse]:
    """
    Lista todas las versiones de prompts.
    
    Parámetros:
    - activo_only: Si es True, solo retorna prompts activos.
    """
    params = {
        "select": "id,nombre,version,objetivo,proveedor,modelo_recomendado,activo,creado_por,fecha_creacion",
        "order": "nombre.asc,version.desc",
    }
    
    if activo_only:
        params["activo"] = "eq.true"
    
    rows = sb.select("prompt_versions", params)
    
    return [
        PromptVersionListResponse(
            id=str(row["id"]),
            nombre=row["nombre"],
            version=row["version"],
            objetivo=row.get("objetivo"),
            proveedor=row.get("proveedor"),
            modelo_recomendado=row.get("modelo_recomendado"),
            activo=row["activo"],
            creado_por=str(row["creado_por"]) if row.get("creado_por") else None,
            fecha_creacion=row["fecha_creacion"],
        )
        for row in rows
    ]


@router.get(
    "/{prompt_id}",
    response_model=PromptVersionResponse,
    summary="Obtener versión de prompt por ID"
)
async def get_prompt(
    prompt_id: str,
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase),
) -> PromptVersionResponse:
    """
    Obtiene los detalles de una versión específica de prompt.
    """
    rows = sb.select(
        "prompt_versions",
        {
            "id": f"eq.{prompt_id}",
            "limit": "1",
        },
    )
    
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt no encontrado.",
        )
    
    row = rows[0]
    return PromptVersionResponse(
        id=str(row["id"]),
        nombre=row["nombre"],
        version=row["version"],
        contenido=row["contenido"],
        objetivo=row.get("objetivo"),
        proveedor=row.get("proveedor"),
        modelo_recomendado=row.get("modelo_recomendado"),
        activo=row["activo"],
        creado_por=str(row["creado_por"]) if row.get("creado_por") else None,
        fecha_creacion=row["fecha_creacion"],
    )


@router.patch(
    "/{prompt_id}",
    response_model=PromptVersionResponse,
    summary="Actualizar versión de prompt"
)
async def update_prompt(
    prompt_id: str,
    body: PromptVersionUpdate,
    user: dict = Depends(get_current_investigator),
    sb: SupabaseClient = Depends(get_supabase),
) -> PromptVersionResponse:
    """
    Actualiza una versión de prompt existente.
    
    Nota: Para mantener inmutabilidad, se recomienda crear una nueva versión
    en lugar de modificar una existente. Este endpoint está disponible para
    correcciones menores.
    
    Requiere rol de INVESTIGADOR o ADMIN.
    """
    if not user.get("is_investigator"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo investigadores y administradores pueden actualizar prompts.",
        )
    
    # Construir datos de actualización
    update_data = {}
    if body.contenido is not None:
        update_data["contenido"] = body.contenido
    if body.objetivo is not None:
        update_data["objetivo"] = body.objetivo
    if body.proveedor is not None:
        update_data["proveedor"] = body.proveedor
    if body.modelo_recomendado is not None:
        update_data["modelo_recomendado"] = body.modelo_recomendado
    if body.activo is not None:
        update_data["activo"] = body.activo
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se proporcionaron datos para actualizar.",
        )
    
    # Actualizar
    sb.update(
        "prompt_versions",
        update_data,
        {"id": f"eq.{prompt_id}"},
    )
    
    # Retornar el prompt actualizado
    return await get_prompt(prompt_id, user, sb)


@router.delete(
    "/{prompt_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desactivar versión de prompt"
)
async def delete_prompt(
    prompt_id: str,
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase),
):
    """
    Desactiva una versión de prompt (soft delete).
    
    En lugar de eliminar físicamente, se marca como inactivo.
    
    Requiere rol de ADMIN.
    """
    if not user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden desactivar prompts.",
        )
    
    # Verificar que existe
    existing = sb.select(
        "prompt_versions",
        {
            "id": f"eq.{prompt_id}",
            "limit": "1",
        },
    )
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt no encontrado.",
        )
    
    # Desactivar (soft delete)
    sb.update(
        "prompt_versions",
        {"activo": False},
        {"id": f"eq.{prompt_id}"},
    )
    
    return None
