"""
Servicio de generación de actas con IA.

Extrae texto de documentos, lo envía a un LLM y genera
un acta estructurada con secciones formales.
"""

from __future__ import annotations

import json
import re
from typing import Any, Optional

import requests

from app.core.config import settings


# ------------------------------------------------------------------
# Prompt para generación de acta
# ------------------------------------------------------------------

ACTA_SYSTEM_PROMPT = """Eres un secretario corporativo experto en redacción de actas de reuniones.

A partir del texto proporcionado, genera un ACTA DE REUNIÓN formal y estructurada en español.

El acta debe incluir las siguientes secciones claramente delimitadas:

# ACTA DE REUNIÓN

## Información General
- **Número de acta:** [auto]
- **Fecha de la reunión:** [inferir del texto o indicar "No especificada"]
- **Tipo de reunión:** [virtual/presencial/mixta]
- **Duración:** [inferir del texto o indicar "No especificada"]

## Participantes
Lista de asistentes mencionados en el texto con sus roles si están disponibles.

## Orden del día / Temas tratados
Puntos principales discutidos en la reunión.

## Desarrollo de la reunión
Resumen detallado de lo tratado en cada tema.

## Decisiones tomadas
Lista de acuerdos y decisiones concretas adoptados.

## Tareas y compromisos
Tabla con: descripción, responsable (si se menciona), fecha límite (si se menciona).

## Próximos pasos
Acciones a seguir después de la reunión.

## Observaciones
Cualquier nota adicional relevante.

Instrucciones:
- Sé preciso y no inventes información que no esté en el texto.
- Si un dato no está disponible, indica "No especificado".
- Usa formato markdown limpio.
- Devuelve SOLO el acta en markdown, sin comentarios adicionales."""


# ------------------------------------------------------------------
# Llamada al LLM
# ------------------------------------------------------------------

def _call_llm(messages: list[dict[str, str]]) -> str:
    """Llama a un LLM compatible con la API de OpenAI (Groq, OpenAI, etc.)."""
    api_key = settings.GROQ_API_KEY or settings.OPENAI_API_KEY
    base_url = settings.LLM_BASE_URL
    model = settings.LLM_MODEL

    if not api_key:
        raise RuntimeError(
            "No hay API key configurada para LLM. "
            "Configura GROQ_API_KEY o OPENAI_API_KEY en .env"
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 4096,
    }

    resp = requests.post(
        f"{base_url}/chat/completions",
        headers=headers,
        json=payload,
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


# ------------------------------------------------------------------
# Generación de acta
# ------------------------------------------------------------------

def generate_acta(
    texto_documento: str,
    titulo: str = "Acta de Reunión",
    tipo_reunion: str = "virtual",
    participantes: Optional[str] = None,
    orden_dia: Optional[str] = None,
    observaciones: Optional[str] = None,
) -> dict[str, Any]:
    """
    Genera un acta estructurada a partir del texto extraído de un documento.
    
    Retorna un dict con las secciones del acta:
    - contenido: markdown completo del acta
    - decisiones: sección de decisiones
    - tareas_extraidas: tareas encontradas
    - proximos_pasos: próximos pasos
    """
    context_parts = [f"**Título:** {titulo}"]
    context_parts.append(f"**Tipo de reunión:** {tipo_reunion}")

    if participantes:
        context_parts.append(f"**Participantes conocidos:** {participantes}")
    if orden_dia:
        context_parts.append(f"**Orden del día proporcionado:** {orden_dia}")
    if observaciones:
        context_parts.append(f"**Observaciones adicionales:** {observaciones}")

    context = "\n".join(context_parts)

    user_message = (
        f"{context}\n\n"
        f"---\n\n"
        f"**Texto del documento a procesar:**\n\n{texto_documento}"
    )

    messages = [
        {"role": "system", "content": ACTA_SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    contenido = _call_llm(messages)

    decisiones = _extract_section(contenido, "Decisiones tomadas")
    tareas = _extract_section(contenido, "Tareas y compromisos")
    proximos = _extract_section(contenido, "Próximos pasos")

    return {
        "contenido": contenido,
        "decisiones": decisiones,
        "tareas_extraidas": tareas,
        "proximos_pasos": proximos,
    }


def _extract_section(markdown: str, section_title: str) -> Optional[str]:
    """Extrae una sección específica del markdown generado."""
    pattern = rf"##\s*{re.escape(section_title)}\s*\n(.*?)(?=\n##\s|\Z)"
    match = re.search(pattern, markdown, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else None
