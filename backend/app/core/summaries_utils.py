"""
Utilidades para procesamiento de transcripciones y generación de resúmenes.

Incluye:
- Limpieza de archivos .vtt de Zoom.
- División por chunks solapados.
- Prompts estandarizados para LLMs (Groq / OpenAI-compatible).
"""

from __future__ import annotations

import re


# ------------------------------------------------------------------
# Limpieza de VTT
# ------------------------------------------------------------------

def clean_vtt(content: str | bytes) -> str:
    """Elimina marcas WEBVTT, timestamps, identificadores y espacios extra."""
    if isinstance(content, bytes):
        text = content.decode("utf-8", errors="ignore")
    else:
        text = content

    # Normalizar saltos de línea
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Eliminar líneas WEBVTT y notas
    lines = [line for line in text.split("\n") if not line.startswith("WEBVTT")]

    # Regex de timestamp VTT: 00:00:00.000 --> 00:00:01.000
    timestamp_re = re.compile(r"\d{2}:\d{2}:\d{2}\.\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}\.\d{3}")

    # Regex de identificadores numéricos VTT
    id_re = re.compile(r"^\d+$")

    # Regex de tags VTT: <c>, <v Juan>, etc.
    tag_re = re.compile(r"<[^>]+>")

    cleaned_lines: list[str] = []
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if timestamp_re.match(line):
            continue
        if id_re.match(line):
            continue
        # Quitar tags, ej: <v Juan> -> "Juan"
        line = tag_re.sub("", line)
        line = line.strip()
        if line:
            cleaned_lines.append(line)

    # Unir repeticiones de hablante y líneas consecutivas
    return "\n".join(cleaned_lines)


# ------------------------------------------------------------------
# Chunks solapados
# ------------------------------------------------------------------

def overlapping_chunks(text: str, chunk_size: int = 4000, overlap: int = 200) -> list[str]:
    """Divide texto en chunks solapados para evitar pérdida de contexto."""
    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        if end >= len(text):
            break
        start = end - overlap
    return chunks


# ------------------------------------------------------------------
# Prompts
# ------------------------------------------------------------------

SYSTEM_SUMMARY_PROMPT = """Eres un asistente ejecutivo experto en redactar actas de reuniones en español.

Analiza el texto completo de la reunión y devuelve un JSON válido con las siguientes claves:

{
  "resumen_ejecutivo": "string",
  "decisiones": "string",
  "riesgos": "string",
  "proximos_pasos": "string",
  "tareas": [
    {
      "descripcion": "string",
      "responsable": "string o null",
      "fecha_vencimiento": "YYYY-MM-DD o null"
    }
  ]
}

Instrucciones:
- resumen_ejecutivo: máximo 3 párrafos con lo más importante acordado.
- decisiones: lista con viñetas de decisiones concretas tomadas.
- riesgos: lista con viñetas de bloqueos, riesgos o dependencias.
- proximos_pasos: lista con viñetas de acciones a seguir.
- tareas: extrae cada compromiso, intenta inferir responsable y fecha límite. Si no puedes inferir, usa null.
- No inventes información que no esté en el texto.
- Devuelve SOLO JSON válido, sin comentarios ni markdown."""


def build_summary_messages(transcript: str) -> list[dict[str, str]]:
    """Construye los mensajes para un LLM chat completions."""
    return [
        {"role": "system", "content": SYSTEM_SUMMARY_PROMPT},
        {"role": "user", "content": f"Texto de la reunión:\n\n{transcript}"},
    ]


def build_chunk_messages(chunk: str, chunk_number: int, total_chunks: int) -> list[dict[str, str]]:
    """Prompt para resumir un fragmento de una reunión larga."""
    prompt = (
        f"Este es el fragmento {chunk_number} de {total_chunks} de una reunión. "
        "Extrae los puntos clave, decisiones, tareas y responsables del siguiente texto. "
        "Devuelve SOLO JSON válido con: resumen_ejecutivo, decisiones, riesgos, proximos_pasos, tareas[]."
    )
    return [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"Texto del fragmento:\n\n{chunk}"},
    ]


def build_final_merge_messages(partial_summaries: str) -> list[dict[str, str]]:
    """Prompt para unificar resúmenes parciales."""
    return [
        {
            "role": "system",
            "content": (
                "Tienes resúmenes parciales de una reunión larga. "
                "Unifícalos en un acta corporativa coherente. "
                "Devuelve SOLO JSON válido con: resumen_ejecutivo, decisiones, riesgos, proximos_pasos, tareas[]."
            ),
        },
        {"role": "user", "content": f"Resúmenes parciales:\n\n{partial_summaries}"},
    ]
