"""
Configuración central de la aplicación.

Carga las variables de entorno desde el archivo .env ubicado en la raíz
del proyecto (directorio padre de backend/) y define constantes globales
para JWT, algoritmos y tiempos de expiración.
"""

from pathlib import Path
from pydantic_settings import BaseSettings

# Ruta al .env en la raíz del proyecto (zoom2/.env)
_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    """Esquema de configuración validado con pydantic-settings."""

    # --- Supabase ---
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # --- Storage ---
    SUPABASE_STORAGE_BUCKET: str = "grabaciones-reuniones"
    RECORDING_MAX_AGE_DAYS: int = 7

    # --- n8n Webhooks ---
    N8N_CREATE_MEETING_WEBHOOK_URL: str = ""
    N8N_DRAFT_MEETING_WEBHOOK_URL: str = ""
    N8N_RESUMEN_VIRTUAL_WEBHOOK_URL: str = ""
    N8N_RESUMEN_PRESENCIAL_WEBHOOK_URL: str = ""
    N8N_CALLBACK_SECRET: str = ""
    N8N_PROCESS_RECORDING_WEBHOOK_URL: str = ""
    BACKEND_PUBLIC_URL: str = ""

    # --- JWT / Seguridad ---
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas

    # --- Zoom Server-to-Server OAuth ---
    ZOOM_ACCOUNT_ID: str = ""
    ZOOM_CLIENT_ID: str = ""
    ZOOM_CLIENT_SECRET: str = ""

    # --- Correo del administrador (hardcoded) ---
    ADMIN_EMAIL: str = "juanaureliodelacruzgamarra@gmail.com"

    model_config = {
        "env_file": str(_ENV_FILE),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


# Instancia singleton – se importa donde se necesite
settings = Settings()
