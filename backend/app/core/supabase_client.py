"""
Cliente REST para Supabase.

Replica los helpers sb_select / sb_insert del app.py original pero
extiende la interfaz con update, delete y upsert.  Utiliza la librería
requests directamente (sin SDK de Supabase).
"""

from __future__ import annotations

import json
from typing import Any

import requests

from app.core.config import settings


class SupabaseClient:
    """Cliente HTTP que habla con la API REST de Supabase."""

    def __init__(self) -> None:
        self.base_url: str = f"{settings.SUPABASE_URL}/rest/v1"
        self.headers: dict[str, str] = {
            "apikey": settings.SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {settings.SUPABASE_ANON_KEY}",
            "Content-Type": "application/json",
        }
        self.timeout: int = 30

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
# Instancia singleton utilizada como dependencia de FastAPI
# ------------------------------------------------------------------
_client: SupabaseClient | None = None


def get_supabase() -> SupabaseClient:
    """Devuelve la instancia singleton del cliente Supabase."""
    global _client
    if _client is None:
        _client = SupabaseClient()
    return _client
