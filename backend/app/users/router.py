"""
Router de usuarios.

Contiene los endpoints de gestión de usuarios (CRUD) para la fase 4.
Replica la lógica del panel de administración original de Streamlit.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.users.schemas import UserDetailResponse, UserUpdateRequest
from app.core.dependencies import get_current_user, get_current_admin
from app.core.supabase_client import SupabaseClient, get_supabase
from app.core.config import settings

router = APIRouter(prefix="/users", tags=["Usuarios"])


# ------------------------------------------------------------------
# GET /users
# ------------------------------------------------------------------

@router.get(
    "",
    response_model=List[UserDetailResponse],
    summary="Listar todos los usuarios (solo admin)",
)
async def list_users(
    admin: dict = Depends(get_current_admin),
    sb: SupabaseClient = Depends(get_supabase),
) -> List[UserDetailResponse]:
    """
    Retorna la lista de todos los usuarios registrados.
    Solo los administradores pueden acceder a este endpoint.
    """
    rows = sb.select(
        "usuarios",
        {"select": "id,nombre,correo,nivel_suscripcion,estado_suscripcion,fecha_creacion"}
    )
    
    users = []
    for row in rows:
        users.append(UserDetailResponse(
            id=str(row["id"]),
            correo=row["correo"],
            nombre=row.get("nombre", ""),
            nivel_suscripcion=row.get("nivel_suscripcion", "basico"),
            estado_suscripcion=row.get("estado_suscripcion", "activo"),
            fecha_creacion=row.get("fecha_creacion"),
            is_admin=(row.get("rol", "USUARIO") == "ADMIN")
        ))
    return users


# ------------------------------------------------------------------
# GET /users/{id}
# ------------------------------------------------------------------

@router.get(
    "/{user_id}",
    response_model=UserDetailResponse,
    summary="Obtener detalle de un usuario",
)
async def get_user(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase),
) -> UserDetailResponse:
    """
    Retorna los datos de un usuario específico.
    Solo el administrador o el propio usuario pueden acceder.
    """
    if not current_user.get("is_admin") and str(current_user["id"]) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver a este usuario.",
        )

    rows = sb.select("usuarios", {"id": f"eq.{user_id}"})
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado.",
        )

    row = rows[0]
    return UserDetailResponse(
        id=str(row["id"]),
        correo=row["correo"],
        nombre=row.get("nombre", ""),
        nivel_suscripcion=row.get("nivel_suscripcion", "basico"),
        estado_suscripcion=row.get("estado_suscripcion", "activo"),
        fecha_creacion=row.get("fecha_creacion"),
        is_admin=(row.get("correo", "").lower() == settings.ADMIN_EMAIL.lower())
    )


# ------------------------------------------------------------------
# PATCH /users/{id}
# ------------------------------------------------------------------

@router.patch(
    "/{user_id}",
    response_model=dict,
    summary="Actualizar usuario (solo admin)",
)
async def update_user(
    user_id: str,
    body: UserUpdateRequest,
    admin: dict = Depends(get_current_admin),
    sb: SupabaseClient = Depends(get_supabase),
) -> dict:
    """
    Actualiza datos de un usuario.
    Solo el administrador puede actualizar otros usuarios, incluyendo su nivel y estado.
    """
    # Exclude unset fields
    update_data = body.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se enviaron datos para actualizar.",
        )
        
    try:
        sb.update(
            "usuarios",
            data=update_data,
            params={"id": f"eq.{user_id}"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando usuario: {str(e)}"
        )

    return {"message": "Usuario actualizado exitosamente."}


# ------------------------------------------------------------------
# DELETE /users/{id}
# ------------------------------------------------------------------

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar usuario (solo admin)",
)
async def delete_user(
    user_id: str,
    admin: dict = Depends(get_current_admin),
    sb: SupabaseClient = Depends(get_supabase),
) -> dict:
    """
    Elimina permanentemente un usuario.
    Solo el administrador puede eliminar usuarios.
    """
    try:
        sb.delete("usuarios", params={"id": f"eq.{user_id}"})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error eliminando usuario: {str(e)}"
        )

    return {"message": "Usuario eliminado exitosamente."}
