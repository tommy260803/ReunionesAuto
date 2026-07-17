"""
Cliente REST para Supabase.

Replica los helpers sb_select / sb_insert del app.py original pero
extiende la interfaz con update, delete y upsert.  Utiliza la librería
requests directamente (sin SDK de Supabase).

Añade métodos de Storage usando la service_role_key para gestionar
archivos privados de grabaciones de reuniones.
"""

from __future__ import annotations

import json
from typing import Any

import requests

from app.core.config import settings


class SupabaseClient:
    """Cliente HTTP que habla con la API REST de Supabase."""

    def __init__(self, service_role: bool = False) -> None:
        self.base_url: str = f"{settings.SUPABASE_URL}/rest/v1"
        key = settings.SUPABASE_SERVICE_ROLE_KEY if service_role else settings.SUPABASE_ANON_KEY
        if service_role and not key:
            raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY no está configurada.")
        self.headers: dict[str, str] = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
        self.timeout: int = 30
        self._storage_headers: dict[str, str] = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
        }
        self.storage_url: str = f"{settings.SUPABASE_URL}/storage/v1"

    # ------------------------------------------------------------------
    # Storage helpers
    # ------------------------------------------------------------------

    def storage_upload(
        self,
        bucket: str,
        path: str,
        content: bytes,
        content_type: str,
        upsert: bool = False,
    ) -> dict:
        headers = {**self._storage_headers, "Content-Type": content_type}
        if upsert:
            headers["x-upsert"] = "true"
        url = f"{self.storage_url}/object/{bucket}/{path}"
        r = requests.post(url, headers=headers, data=content, timeout=self.timeout * 2)
        r.raise_for_status()
        try:
            return r.json()
        except ValueError:
            return {"status": "success"}

    def storage_create_signed_url(
        self, bucket: str, path: str, expires_in: int = 3600
    ) -> str:
        url = f"{self.storage_url}/object/sign/{bucket}/{path}"
        r = requests.post(
            url,
            headers={**self._storage_headers, "Content-Type": "application/json"},
            json={"expiresIn": expires_in},
            timeout=self.timeout,
        )
        r.raise_for_status()
        data = r.json()
        signed = data.get("signedURL")
        if not signed:
            raise RuntimeError("No se pudo generar URL firmada")
        if signed.startswith("http"):
            return signed
        # Supabase returns a relative Storage path such as
        # `/object/sign/<bucket>/<path>?token=...`; it must be joined with
        # `/storage/v1`, not with the project root.
        return f"{self.storage_url}/{signed.lstrip('/')}"

    def storage_delete(self, bucket: str, paths: list[str]) -> dict:
        url = f"{self.storage_url}/object/{bucket}"
        r = requests.delete(
            url,
            headers={**self._storage_headers, "Content-Type": "application/json"},
            json={"prefixes": paths},
            timeout=self.timeout,
        )
        r.raise_for_status()
        try:
            return r.json()
        except ValueError:
            return {"status": "success"}

    # ------------------------------------------------------------------
    # Métodos CRUD
    # ------------------------------------------------------------------

    def select(self, table: str, params: dict[str, Any] | None = None) -> list[dict]:
        """
        Consulta registros de una tabla.

        Equivale a sb_select() del Streamlit original.
        """
        r = requests.get(
            f"{self.base_url}/{table}",
            headers=self.headers,
            params=params or {},
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def insert(self, table: str, rows: list[dict] | dict) -> dict | list:
        """
        Inserta una o varias filas en una tabla.

        Equivale a sb_insert() del Streamlit original.
        """
        r = requests.post(
            f"{self.base_url}/{table}",
            headers=self.headers,
            data=json.dumps(rows),
            timeout=self.timeout,
        )
        r.raise_for_status()
        try:
            return r.json()
        except ValueError:
            return {"status": "success"}

    def update(self, table: str, data: dict, params: dict[str, Any]) -> dict | list:
        """
        Actualiza registros que coincidan con los filtros en *params*.

        Ejemplo de params: {"id": "eq.5"}
        """
        r = requests.patch(
            f"{self.base_url}/{table}",
            headers=self.headers,
            data=json.dumps(data),
            params=params,
            timeout=self.timeout,
        )
        r.raise_for_status()
        try:
            return r.json()
        except ValueError:
            return {"status": "success"}

    def delete(self, table: str, params: dict[str, Any]) -> dict | list:
        """
        Elimina registros que coincidan con los filtros en *params*.

        Ejemplo de params: {"id": "eq.5"}
        """
        r = requests.delete(
            f"{self.base_url}/{table}",
            headers=self.headers,
            params=params,
            timeout=self.timeout,
        )
        r.raise_for_status()
        try:
            return r.json()
        except ValueError:
            return {"status": "success"}

    def upsert(self, table: str, rows: list[dict] | dict) -> dict | list:
        """
        Inserta o actualiza (upsert) registros.

        Usa la cabecera Prefer: resolution=merge-duplicates de PostgREST.
        """
        headers = {
            **self.headers,
            "Prefer": "resolution=merge-duplicates",
        }
        r = requests.post(
            f"{self.base_url}/{table}",
            headers=headers,
            data=json.dumps(rows),
            timeout=self.timeout,
        )
        r.raise_for_status()
        try:
            return r.json()
        except ValueError:
            return {"status": "success"}


# ------------------------------------------------------------------
# Instancias singleton separadas por rol
# ------------------------------------------------------------------
_anon_client: SupabaseClient | None = None
_service_client: SupabaseClient | None = None


def get_supabase(service_role: bool = False) -> SupabaseClient:
    """Devuelve la instancia singleton del cliente Supabase.

    Usa service_role=True únicamente en endpoints de backend que requieren
    acceso administrativo a Storage o a tablas privadas.
    """
    global _anon_client, _service_client
    if service_role:
        if _service_client is None:
            _service_client = SupabaseClient(service_role=True)
        return _service_client
    if _anon_client is None:
        _anon_client = SupabaseClient(service_role=False)
    return _anon_client
