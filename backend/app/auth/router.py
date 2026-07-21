"""
Router de autenticación.

Contiene los endpoints de login, registro y consulta del usuario
autenticado.  Replica la lógica de auth que existía en el app.py
de Streamlit.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.core.config import settings
from app.core.dependencies import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.core.supabase_client import SupabaseClient, get_supabase

router = APIRouter(prefix="/auth", tags=["Autenticación"])


# ------------------------------------------------------------------
# POST /auth/login
# ------------------------------------------------------------------

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión",
)
async def login(
    body: LoginRequest,
    sb: SupabaseClient = Depends(get_supabase),
) -> TokenResponse:
    """
    Valida las credenciales del usuario y devuelve un token JWT.

    1. Busca el correo en la tabla ``usuarios``.
    2. Verifica la contraseña con bcrypt.
    3. Genera un access_token JWT.
    """
    # Buscar usuario por correo
    rows = sb.select("usuarios", {
        "select": "id,correo,nombre,password_hash,nivel_suscripcion,estado_suscripcion,rol",
        "correo": f"eq.{body.email}",
    })
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas.",
        )

    user = rows[0]

    # Verificar contraseña
    if not verify_password(body.password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas.",
        )

    # Determinar roles basados en rol de BD
    rol = user.get("rol", "USUARIO")
    is_admin = rol == "ADMIN"
    is_investigator = rol in ("ADMIN", "INVESTIGADOR")
    is_evaluator = rol in ("ADMIN", "INVESTIGADOR", "EVALUADOR")

    # Crear token JWT (sub = id del usuario)
    access_token = create_access_token({"sub": str(user["id"])})

    return TokenResponse(
        access_token=access_token,
        user=UserResponse(
            id=user["id"],
            correo=user["correo"],
            nombre=user.get("nombre", ""),
            nivel_suscripcion=user.get("nivel_suscripcion", "basico"),
            estado_suscripcion=user.get("estado_suscripcion", "activo"),
            rol=rol,
            is_admin=is_admin,
            is_investigator=is_investigator,
            is_evaluator=is_evaluator,
        ),
    )


# ------------------------------------------------------------------
# POST /auth/register
# ------------------------------------------------------------------

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario",
)
async def register(
    body: RegisterRequest,
    sb: SupabaseClient = Depends(get_supabase),
) -> dict:
    """
    Crea un nuevo usuario en la tabla ``usuarios``.

    - Verifica que el correo no esté ya registrado.
    - Hashea la contraseña con bcrypt (passlib).
    - Inserta con nivel_suscripcion='basico' y estado_suscripcion='activo'.
    """
    # Verificar si el correo ya existe
    existing = sb.select("usuarios", {"correo": f"eq.{body.email}"})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con ese correo electrónico.",
        )

    # Crear registro
    new_user = {
        "correo": body.email,
        "password_hash": hash_password(body.password),
        "nombre": body.nombre,
        "nivel_suscripcion": "basico",
        "estado_suscripcion": "activo",
    }
    sb.insert("usuarios", [new_user])

    return {"message": "Usuario registrado exitosamente."}


# ------------------------------------------------------------------
# GET /auth/me
# ------------------------------------------------------------------

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obtener datos del usuario autenticado",
)
async def me(user: dict = Depends(get_current_user)) -> UserResponse:
    """
    Retorna los datos del usuario autenticado a partir de su token JWT.
    """
    rol = user.get("rol", "USUARIO")
    return UserResponse(
        id=user["id"],
        correo=user["correo"],
        nombre=user.get("nombre", ""),
        nivel_suscripcion=user.get("nivel_suscripcion", "basico"),
        estado_suscripcion=user.get("estado_suscripcion", "activo"),
        rol=rol,
        is_admin=user.get("is_admin", False),
        is_investigator=user.get("is_investigator", False),
        is_evaluator=user.get("is_evaluator", False),
    )
