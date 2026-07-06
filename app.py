import os, json, requests
import time
import re
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from passlib.hash import bcrypt
import streamlit as st
from dotenv import load_dotenv
import altair as alt

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
N8N_URL = os.getenv("N8N_CREATE_MEETING_WEBHOOK_URL")
N8N_RESUMEN_VIRTUAL_URL = os.getenv("N8N_RESUMEN_VIRTUAL_WEBHOOK_URL")
N8N_RESUMEN_PRESENCIAL_URL = os.getenv("N8N_RESUMEN_PRESENCIAL_WEBHOOK_URL")

HEADERS = {
    "apikey": SUPABASE_ANON_KEY or "",
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    "Content-Type": "application/json",
}

st.set_page_config(
    page_title="Asistente de Reuniones",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAV_LABELS = {
    "Chat": "Chat asistido",
    "Usuarios": "Usuarios",
    "Reuniones": "Reuniones",
    "Tareas": "Tareas",
    "Resumen de reuniones": "Resúmenes",
    "Participantes": "Participantes",
    "Métricas": "Métricas",
    "Cerrar sesión": "Cerrar sesión",
}

NAV_ICONS = {
    "Chat": "💬",
    "Usuarios": "👥",
    "Reuniones": "📅",
    "Tareas": "✅",
    "Resumen de reuniones": "📝",
    "Participantes": "🤝",
    "Métricas": "📊",
    "Cerrar sesión": "🚪",
}

def inject_custom_styles():
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #111827 45%, #172554 100%);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.2rem;
    }

    [data-testid="stSidebar"] * {
        color: #e5eefb;
    }

    .sidebar-brand {
        padding: 1rem 1rem 0.5rem 1rem;
    }

    .sidebar-brand-card {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.24), rgba(14, 165, 233, 0.16));
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 18px;
        padding: 1rem;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.22);
    }

    .sidebar-eyebrow {
        font-size: 0.74rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #93c5fd;
        margin-bottom: 0.35rem;
        font-weight: 700;
    }

    .sidebar-title {
        font-size: 1.15rem;
        font-weight: 700;
        margin: 0;
        color: #f8fafc;
    }

    .sidebar-subtitle {
        font-size: 0.88rem;
        margin-top: 0.4rem;
        color: #cbd5e1;
        line-height: 1.45;
    }

    .sidebar-user-card {
        background: rgba(15, 23, 42, 0.52);
        border: 1px solid rgba(148, 163, 184, 0.14);
        border-radius: 16px;
        padding: 0.9rem 1rem;
        margin: 0.9rem 0 0.35rem 0;
    }

    .sidebar-user-name {
        font-size: 0.98rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 0.15rem;
    }

    .sidebar-user-meta {
        font-size: 0.82rem;
        color: #cbd5e1;
        line-height: 1.45;
    }

    .sidebar-chip {
        display: inline-block;
        margin-top: 0.6rem;
        padding: 0.2rem 0.55rem;
        border-radius: 999px;
        background: rgba(59, 130, 246, 0.18);
        color: #bfdbfe;
        font-size: 0.74rem;
        font-weight: 700;
    }

    .sidebar-section-title {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #93c5fd;
        margin: 1rem 0 0.4rem 0;
        font-weight: 700;
    }

    [data-testid="stSidebar"] [role="radiogroup"] > label {
        background: rgba(15, 23, 42, 0.42);
        border: 1px solid rgba(148, 163, 184, 0.12);
        border-radius: 14px;
        padding: 0.2rem 0.35rem;
        margin-bottom: 0.45rem;
        transition: all 0.18s ease;
    }

    [data-testid="stSidebar"] [role="radiogroup"] > label:hover {
        border-color: rgba(96, 165, 250, 0.7);
        background: rgba(30, 41, 59, 0.88);
        transform: translateX(2px);
    }

    [data-testid="stSidebar"] [role="radiogroup"] label[data-baseweb="radio"] > div:first-child {
        display: none;
    }

    [data-testid="stSidebar"] [role="radiogroup"] p {
        font-size: 0.95rem;
        font-weight: 600;
        color: #e2e8f0;
    }

    [data-testid="stSidebar"] [role="radiogroup"] > label:has(input:checked) {
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.38), rgba(14, 165, 233, 0.24));
        border-color: rgba(125, 211, 252, 0.75);
        box-shadow: 0 8px 20px rgba(2, 132, 199, 0.2);
    }

    [data-testid="stSidebar"] .stDateInput label,
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stTextInput label {
        color: #cbd5e1;
        font-weight: 600;
    }

    [data-testid="stSidebar"] hr {
        border-color: rgba(148, 163, 184, 0.14);
        margin-top: 1rem;
        margin-bottom: 0.85rem;
    }
    </style>
    """, unsafe_allow_html=True)

def render_sidebar(opciones_menu, admin):
    session = st.session_state.session or {}
    nombre = session.get("nombre", "Usuario")
    nivel = str(session.get("nivel", "basico")).capitalize()
    correo = session.get("correo", "")
    chip = "Administrador" if admin else f"Plan {nivel}"

    with st.sidebar:
        st.markdown("""
        <div class="sidebar-brand">
            <div class="sidebar-brand-card">
                <div class="sidebar-eyebrow">Zoom2</div>
                <p class="sidebar-title">Asistente de Reuniones</p>
                <div class="sidebar-subtitle">Organiza reuniones, tareas, participantes y resúmenes desde un solo panel.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="sidebar-user-card">
                <div class="sidebar-user-name">{nombre}</div>
                <div class="sidebar-user-meta">{correo}</div>
                <div class="sidebar-user-meta">Suscripción: {nivel}</div>
                <span class="sidebar-chip">{chip}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown('<div class="sidebar-section-title">Navegación</div>', unsafe_allow_html=True)
        return st.radio(
            "Navegación",
            opciones_menu,
            format_func=lambda page: f"{NAV_ICONS.get(page, '•')}  {NAV_LABELS.get(page, page)}",
            label_visibility="collapsed",
        )

def render_public_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-brand">
            <div class="sidebar-brand-card">
                <div class="sidebar-eyebrow">Zoom2</div>
                <p class="sidebar-title">Asistente de Reuniones</p>
                <div class="sidebar-subtitle">Programa reuniones, gestiona participantes y centraliza resúmenes y tareas desde un mismo lugar.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            """
            <div class="sidebar-user-card">
                <div class="sidebar-user-name">Acceso al sistema</div>
                <div class="sidebar-user-meta">Inicia sesión o crea una cuenta para habilitar el panel completo.</div>
                <span class="sidebar-chip">Modo público</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown('<div class="sidebar-section-title">Accesos</div>', unsafe_allow_html=True)
        st.caption("Usa las pestañas centrales para iniciar sesión o registrarte.")
        st.caption("Al ingresar verás el menú completo de navegación en esta barra lateral.")

def render_chat_styles():
    st.markdown("""
    <style>
    .chat-hero {
        background: linear-gradient(135deg, #eff6ff 0%, #eef2ff 55%, #f8fafc 100%);
        border: 1px solid #dbeafe;
        border-radius: 24px;
        padding: 1.4rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 14px 40px rgba(37, 99, 235, 0.08);
    }

    .chat-eyebrow {
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #2563eb;
        margin-bottom: 0.4rem;
    }

    .chat-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.35rem;
    }

    .chat-copy {
        font-size: 0.98rem;
        color: #475569;
        line-height: 1.6;
        margin-bottom: 0;
    }

    .chat-summary-card {
        background: #ffffff;
        border: 1px solid #dbeafe;
        border-radius: 20px;
        padding: 1.1rem 1rem;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05);
        height: 100%;
    }

    .chat-card-title {
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #2563eb;
        font-weight: 800;
        margin-bottom: 0.55rem;
    }

    .chat-card-text {
        font-size: 0.94rem;
        color: #334155;
        line-height: 1.55;
        margin: 0;
    }

    .chat-chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        margin-top: 0.75rem;
    }

    .chat-chip {
        display: inline-flex;
        align-items: center;
        padding: 0.3rem 0.7rem;
        border-radius: 999px;
        background: #eff6ff;
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .chat-panel {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 22px;
        padding: 1.1rem 1.15rem 0.9rem 1.15rem;
        box-shadow: 0 10px 32px rgba(15, 23, 42, 0.04);
        margin-bottom: 1rem;
    }

    .chat-panel-title {
        font-size: 1rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.25rem;
    }

    .chat-panel-copy {
        font-size: 0.92rem;
        color: #64748b;
        margin-bottom: 0.9rem;
    }

    .chat-empty-state {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border: 1px dashed #cbd5e1;
        border-radius: 20px;
        padding: 1rem 1.1rem;
        margin-bottom: 1rem;
    }

    .chat-empty-title {
        font-size: 1rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.35rem;
    }

    .chat-empty-copy {
        font-size: 0.92rem;
        color: #64748b;
        line-height: 1.55;
        margin-bottom: 0;
    }

    [data-testid="stChatMessage"] {
        border-radius: 20px;
        padding: 0.35rem 0.2rem;
    }

    [data-testid="stChatMessageContent"] {
        border-radius: 18px;
        padding: 0.85rem 1rem;
        border: 1px solid #e2e8f0;
        background: #ffffff;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.04);
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
        background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%);
        border-color: #bfdbfe;
    }

    [data-testid="stChatInput"] {
        border-top: 1px solid #e2e8f0;
        background: rgba(255,255,255,0.96);
        backdrop-filter: blur(8px);
    }

    div[data-testid="stExpander"] {
        border: none;
        background: transparent;
    }

    .chat-response-card {
        background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%);
        border: 1px solid #bbf7d0;
        border-radius: 18px;
        padding: 1rem 1.1rem;
        margin: 0.25rem 0;
    }

    .chat-response-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #166534;
        margin-bottom: 0.6rem;
    }

    .chat-response-row {
        display: flex;
        align-items: baseline;
        gap: 0.5rem;
        margin-bottom: 0.3rem;
    }

    .chat-response-label {
        font-size: 0.82rem;
        font-weight: 600;
        color: #64748b;
        min-width: 82px;
    }

    .chat-response-value {
        font-size: 0.94rem;
        color: #0f172a;
    }

    .chat-response-link {
        font-size: 0.94rem;
        color: #2563eb;
        word-break: break-all;
    }

    .chat-error-card {
        background: linear-gradient(135deg, #fef2f2 0%, #ffffff 100%);
        border: 1px solid #fecaca;
        border-radius: 18px;
        padding: 1rem 1.1rem;
        margin: 0.25rem 0;
    }

    .chat-error-title {
        font-size: 1rem;
        font-weight: 700;
        color: #991b1b;
        margin-bottom: 0.4rem;
    }

    .chat-error-detail {
        font-size: 0.9rem;
        color: #7f1d1d;
        line-height: 1.5;
    }

    .chat-clear-btn {
        margin-bottom: 0.5rem;
    }

    .chat-divider {
        margin: 0.75rem 0 0.25rem 0;
        border: none;
        border-top: 1px solid #e2e8f0;
    }
    </style>
    """, unsafe_allow_html=True)

def registrar_metrica_n8n(endpoint, tiempo_respuesta, estado, codigo_estado=None, reunion_id=None, tamano_respuesta=None, detalles=None):
    """
    Registra métricas de rendimiento de las peticiones a n8n en Supabase.
    
    Args:
        endpoint (str): Nombre del endpoint de n8n (ej: 'resumen_presencial')
        tiempo_respuesta (float): Tiempo de respuesta en segundos
        estado (str): 'éxito', 'error' o 'en_proceso'
        codigo_estado (int, optional): Código de estado HTTP de la respuesta
        reunion_id (str, optional): ID de la reunión relacionada
        tamano_respuesta (int, optional): Tamaño de la respuesta en bytes
        detalles (str, optional): Información adicional o mensaje de error
    """
    try:
        # Preparar los datos a insertar
        metrica = {
            'endpoint': endpoint,
            'tiempo_respuesta': tiempo_respuesta,
            'estado': estado,
            'fecha': datetime.now().isoformat(),
            'codigo_estado': codigo_estado,
            'reunion_id': reunion_id,
            'tamano_respuesta': tamano_respuesta,
            'detalles': detalles
        }
        
        # Insertar en Supabase usando sb_insert
        sb_insert('metricas_n8n', [metrica])
        
    except Exception as e:
        # No hacer nada si falla el registro de métricas
        # para no afectar el flujo principal
        print(f"Error al registrar métrica: {str(e)}")
        pass

# -------- Helpers Supabase --------
def sb_select(table, params):
    r = requests.get(f"{SUPABASE_URL}/rest/v1/{table}", headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def sb_insert(table, rows):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=HEADERS, data=json.dumps(rows), timeout=30)
    r.raise_for_status()
    try:
        return r.json()  # si hay JSON, lo devuelve
    except ValueError:
        return {"status": "success"}  # si viene vacío, igual regresamos OK

def save_resumen(reunion_id: str, resumen_texto: str) -> bool:
    try:
        existentes = sb_select("resumenes", {"select":"id,reunion_id", "reunion_id": f"eq.{reunion_id}"})
        if existentes:
            rid = existentes[0]["id"]
            requests.patch(
                f"{SUPABASE_URL}/rest/v1/resumenes",
                headers={**HEADERS, "Prefer": "return=representation"},
                params={"id": f"eq.{rid}"},
                data=json.dumps({"resumen": resumen_texto})
            )
        else:
            sb_insert("resumenes", [{"reunion_id": reunion_id, "resumen": resumen_texto}])
        return True
    except Exception:
        return False

def hash_pw(pw: str) -> str:
    return bcrypt.hash(pw)

def verify_pw(pw: str, hashed: str) -> bool:
    return bcrypt.verify(pw, hashed)

# -------- Admin helper --------
def is_admin() -> bool:
    try:
        ses = st.session_state.session or {}
        return str(ses.get("correo","")) == "juanaureliodelacruzgamarra@gmail.com"
    except Exception:
        return False

# -------- PDF Helper --------
def df_to_pdf_bytes(title: str, df: pd.DataFrame) -> bytes:
    # Configuración de márgenes y estilos
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=30,  # Reducido de 36
        rightMargin=30,  # Reducido de 36
        topMargin=40,
        bottomMargin=30
    )
    
    styles = getSampleStyleSheet()
    
    # Estilo para el texto normal
    normal_style = styles["Normal"]
    normal_style.fontSize = 8  # Tamaño de fuente reducido
    normal_style.leading = 10  # Espaciado entre líneas
    
    # Estilo para encabezados
    header_style = styles["Heading4"]
    header_style.fontSize = 9
    header_style.leading = 12
    header_style.alignment = 1  # Centrado
    
    story = []
    
    # Título
    title_style = styles["Title"]
    title_style.fontSize = 14
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 10))
    
    # Columnas a mostrar
    cols = [c for c in ["id", "nombre", "correo", "nivel_suscripcion", "estado_suscripcion", "fecha_creacion"] 
            if c in df.columns]
    
    # Definir anchos de columna (en puntos)
    col_widths = {
        'id': 40,
        'nombre': 100,
        'correo': 120,
        'nivel_suscripcion': 60,
        'estado_suscripcion': 60,
        'fecha_creacion': 80
    }
    
    # Filtrar y ordenar los anchos según las columnas disponibles
    available_widths = {k: v for k, v in col_widths.items() if k in cols}
    total_width = sum(available_widths.values())
    
    # Ajustar proporcionalmente si el ancho total excede el espacio disponible (aprox. 530 puntos)
    max_width = 530
    if total_width > max_width:
        ratio = max_width / total_width
        available_widths = {k: v * ratio for k, v in available_widths.items()}
    
    # Crear encabezados
    headers = []
    for col in cols:
        if col == 'id':
            headers.append(Paragraph("<b>ID</b>", header_style))
        elif col == 'nombre':
            headers.append(Paragraph("<b>Nombre</b>", header_style))
        elif col == 'correo':
            headers.append(Paragraph("<b>Correo</b>", header_style))
        elif col == 'nivel_suscripcion':
            headers.append(Paragraph("<b>Nivel</b>", header_style))
        elif col == 'estado_suscripcion':
            headers.append(Paragraph("<b>Estado</b>", header_style))
        elif col == 'fecha_creacion':
            headers.append(Paragraph("<b>Fecha</b>", header_style))
    
    data = [headers]
    
    # Agregar filas de datos
    for _, r in df[cols].iterrows():
        row = []
        for col in cols:
            text = str(r.get(col, "")).strip()
            # Usar Paragraph para permitir ajuste de texto
            p = Paragraph(text, normal_style)
            row.append(p)
        data.append(row)
    
    # Crear tabla con anchos personalizados
    table = Table(
        data,
        colWidths=[available_widths[col] for col in cols],
        repeatRows=1
    )
    
    # Aplicar estilos a la tabla
    table_style = [
        # Encabezado
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("FONTNAME", (0, 0), (-1, 0), 'Helvetica-Bold'),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        
        # Celdas de datos
        ("FONTNAME", (0, 1), (-1, -1), 'Helvetica'),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
        ("TOPPADDING", (0, 1), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        
        # Bordes
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("LINEBELOW", (0, 0), (-1, 0), 1, colors.black),
        
        # Colores alternados para filas
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#ffffff"), colors.HexColor("#f9f9f9")])
    ]
    
    # Aplicar estilos a la tabla
    table.setStyle(TableStyle(table_style))
    
    # Añadir la tabla al documento
    story.append(table)
    
    # Construir el PDF
    doc.build(story)
    
    # Obtener los bytes del PDF
    pdf_bytes = buf.getvalue()
    buf.close()
    
    return pdf_bytes

def tareas_to_pdf_bytes(title: str, df: pd.DataFrame) -> bytes:
    """
    Genera un PDF con las tareas, optimizado para mostrar información de tareas.
    """
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=30,
        rightMargin=30,
        topMargin=40,
        bottomMargin=30
    )
    
    styles = getSampleStyleSheet()
    
    # Estilo para el texto normal
    normal_style = styles["Normal"]
    normal_style.fontSize = 7
    normal_style.leading = 9
    
    # Estilo para encabezados
    header_style = styles["Heading4"]
    header_style.fontSize = 8
    header_style.leading = 10
    header_style.alignment = 1  # Centrado
    
    story = []
    
    # Título
    title_style = styles["Title"]
    title_style.fontSize = 14
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 10))
    
    # Columnas a mostrar para tareas
    cols = [c for c in ["reunion_nombre", "descripcion", "asignado_a_correo", "estado", "fecha_vencimiento"] 
            if c in df.columns]
    
    # Definir anchos de columna (en puntos)
    col_widths = {
        'reunion_nombre': 120,
        'descripcion': 180,
        'asignado_a_correo': 100,
        'estado': 60,
        'fecha_vencimiento': 70
    }
    
    # Filtrar anchos según columnas disponibles
    available_widths = {k: v for k, v in col_widths.items() if k in cols}
    total_width = sum(available_widths.values())
    
    # Ajustar proporcionalmente si excede el espacio disponible
    max_width = 530
    if total_width > max_width:
        ratio = max_width / total_width
        available_widths = {k: v * ratio for k, v in available_widths.items()}
    
    # Crear encabezados
    headers = []
    for col in cols:
        if col == 'reunion_nombre':
            headers.append(Paragraph("<b>Reunión</b>", header_style))
        elif col == 'descripcion':
            headers.append(Paragraph("<b>Tarea</b>", header_style))
        elif col == 'asignado_a_correo':
            headers.append(Paragraph("<b>Asignado a</b>", header_style))
        elif col == 'estado':
            headers.append(Paragraph("<b>Estado</b>", header_style))
        elif col == 'fecha_vencimiento':
            headers.append(Paragraph("<b>Vencimiento</b>", header_style))
    
    data = [headers]
    
    # Agregar filas de datos
    for _, r in df[cols].iterrows():
        row = []
        for col in cols:
            text = str(r.get(col, "")).strip()
            # Truncar texto muy largo para descripción
            if col == 'descripcion' and len(text) > 100:
                text = text[:97] + "..."
            p = Paragraph(text, normal_style)
            row.append(p)
        data.append(row)
    
    # Crear tabla con anchos personalizados
    table = Table(
        data,
        colWidths=[available_widths[col] for col in cols],
        repeatRows=1
    )
    
    # Aplicar estilos a la tabla
    table_style = [
        # Encabezado
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4a90e2")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), 'Helvetica-Bold'),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        
        # Celdas de datos
        ("FONTNAME", (0, 1), (-1, -1), 'Helvetica'),
        ("FONTSIZE", (0, 1), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
        ("TOPPADDING", (0, 1), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        
        # Bordes
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("LINEBELOW", (0, 0), (-1, 0), 1.5, colors.HexColor("#4a90e2")),
        
        # Colores alternados para filas
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#ffffff"), colors.HexColor("#f0f8ff")])
    ]
    
    # Aplicar estilos a la tabla
    table.setStyle(TableStyle(table_style))
    
    # Añadir la tabla al documento
    story.append(table)
    
    # Agregar pie de página con información
    story.append(Spacer(1, 20))
    footer_text = f"Total de tareas: {len(df)} | Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    footer_style = styles["Normal"]
    footer_style.fontSize = 8
    footer_style.textColor = colors.grey
    story.append(Paragraph(footer_text, footer_style))
    
    # Construir el PDF
    doc.build(story)
    
    # Obtener los bytes del PDF
    pdf_bytes = buf.getvalue()
    buf.close()
    
    return pdf_bytes

if "session" not in st.session_state:
    st.session_state.session = None
if "chat" not in st.session_state:
    st.session_state.chat = []

# -------- Auth Views --------
def view_login():
    st.subheader("Iniciar sesión")
    email = st.text_input("Correo", key="login_email")
    pw = st.text_input("Contraseña", type="password", key="login_pw")
    if st.button("Ingresar", use_container_width=True):
        try:
            data = sb_select("usuarios", {"select":"id,correo,nombre,password_hash,nivel_suscripcion,estado_suscripcion", "correo": f"eq.{email}"})
            if not data: st.error("Usuario no encontrado"); return
            u = data[0]
            if not verify_pw(pw, u["password_hash"]): st.error("Credenciales inválidas"); return
            st.session_state.session = {
                "id": u["id"], "correo": u["correo"], "nombre": u["nombre"],
                "nivel": u["nivel_suscripcion"], "estado": u["estado_suscripcion"]
            }
            st.success("¡Bienvenido!")
            st.rerun()
        except Exception as e:
            st.error(str(e))

def view_register():
    st.subheader("Registrarse")
    nombre = st.text_input("Nombre", key="reg_nombre")
    correo = st.text_input("Correo", key="reg_correo")
    pw = st.text_input("Contraseña", type="password", key="reg_pw")
    if st.button("Crear cuenta", use_container_width=True):
        if not (nombre and correo and pw): st.warning("Completa todo"); return
        try:
            sb_insert("usuarios", [{
                "nombre": nombre,
                "correo": correo,
                "password_hash": hash_pw(pw),
                "nivel_suscripcion": "basico",
                "estado_suscripcion": "activo"
            }])
            st.success("Cuenta creada. Inicia sesión.")
        except Exception as e:
            st.error(str(e))

# -------- Chat Reuniones --------
def view_chat():
    render_chat_styles()

    # Reset seguro de opciones antes de instanciar widgets
    if st.session_state.get("chat_reset_pending"):
        st.session_state["quick_email"] = ""
        st.session_state["direccion_reunion"] = ""
        st.session_state["tipo_reunion"] = "Virtual"
        st.session_state["chat_reset_pending"] = False

    tipo_actual = st.session_state.get("tipo_reunion", "Virtual")
    invitados_actuales = st.session_state.get("quick_email", "").strip()
    direccion_actual = st.session_state.get("direccion_reunion", "").strip()
    resumen_invitados = invitados_actuales if invitados_actuales else "Sin invitados precargados"
    resumen_direccion = direccion_actual if direccion_actual else "Se definirá desde el mensaje o quedará vacía"

    hero_col, summary_col = st.columns([2.2, 1.1], gap="large")
    with hero_col:
        st.markdown("""
        <div class="chat-hero">
            <div class="chat-eyebrow">Asistente conversacional</div>
            <div class="chat-title">💬 Chat asistido</div>
            <p class="chat-copy">Describe la reunión en lenguaje natural y el sistema completará el contexto con el tipo, invitados y dirección que definas aquí.</p>
            <div class="chat-chip-row">
                <span class="chat-chip">Lenguaje natural</span>
                <span class="chat-chip">Integración con n8n</span>
                <span class="chat-chip">Agenda guiada</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with summary_col:
        st.markdown(
            f"""
            <div class="chat-summary-card">
                <div class="chat-card-title">Resumen actual</div>
                <p class="chat-card-text"><strong>Tipo:</strong> {tipo_actual}</p>
                <p class="chat-card-text"><strong>Invitados:</strong> {resumen_invitados}</p>
                <p class="chat-card-text"><strong>Dirección:</strong> {resumen_direccion}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    if st.session_state.chat:
        col_chat_top, col_chat_clear = st.columns([5, 1])
        with col_chat_clear:
            if st.button("🔄 Nuevo chat", use_container_width=True, type="secondary"):
                st.session_state.chat = []
                st.rerun()
    else:
        st.markdown("""
        <div class="chat-empty-state">
            <div class="chat-empty-title">Comienza con una instrucción simple</div>
            <p class="chat-empty-copy">Ejemplo: “Programa una reunión mañana a las 11 am por 45 minutos con el equipo comercial y agrega a ana@empresa.com”.</p>
        </div>
        """, unsafe_allow_html=True)

    # Mostrar historial
    for role, text in st.session_state.chat:
        with st.chat_message(role):
            st.markdown(text, unsafe_allow_html=True)

    st.markdown("""
    <div class="chat-panel">
        <div class="chat-panel-title">Opciones rápidas de la reunión</div>
        <div class="chat-panel-copy">Estas opciones se agregan automáticamente a tu mensaje para que el chat tenga más contexto antes de enviarlo a n8n.</div>
    """, unsafe_allow_html=True)

    # Opciones de reunión (en un expander, sobre el input fijo)
    with st.expander("Configurar reunión", expanded=True):
        col_tipo, col_inv = st.columns([2,3])
        with col_tipo:
            st.radio("Tipo de reunión", ["Virtual","Presencial","Mixta"], horizontal=True, key="tipo_reunion")
        with col_inv:
            st.text_area(
                "Invitados",
                placeholder="ana@empresa.com\njuan@empresa.com",
                key="quick_email",
                height=80,
                help="Un email por línea o separados por coma",
            )
            raw_emails = st.session_state.get("quick_email", "").strip()
            if raw_emails:
                parsed = [e.strip() for e in re.split(r"[,\n]+", raw_emails) if e.strip()]
                if parsed:
                    chip_html = '<div style="display:flex;flex-wrap:wrap;gap:0.35rem;margin-top:0.1rem;">'
                    valido = 0
                    for e in parsed:
                        es_valido = bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", e))
                        if es_valido:
                            valido += 1
                        bg = "#dcfce7" if es_valido else "#fef2f2"
                        bd = "#86efac" if es_valido else "#fecaca"
                        co = "#166534" if es_valido else "#991b1b"
                        chip_html += f'<span style="display:inline-flex;align-items:center;padding:0.15rem 0.55rem;border-radius:999px;background:{bg};color:{co};border:1px solid {bd};font-size:0.75rem;font-weight:600;">{e}</span>'
                    chip_html += "</div>"
                    st.markdown(chip_html, unsafe_allow_html=True)
                    total = len(parsed)
                    if valido == total:
                        st.caption(f"✅ {total} invitado(s) válido(s)")
                    else:
                        st.caption(f"⚠️ {valido} válido(s), {total - valido} inválido(s)")
        if st.session_state.get("tipo_reunion") in ["Presencial", "Mixta"]:
            st.text_input("Dirección del lugar (si aplica)", placeholder="Av. Ejemplo 123, Sala A", key="direccion_reunion")
    st.markdown("</div>", unsafe_allow_html=True)

    # Entrada fija estilo chat (WhatsApp-like)
    prompt = st.chat_input("Escribe tu solicitud…")
    if prompt:
        extras = []
        if 'tipo_reunion' in st.session_state and st.session_state.tipo_reunion:
            extras.append(f"la reunión es de tipo {st.session_state.tipo_reunion.lower()}")
        if 'quick_email' in st.session_state and st.session_state.quick_email:
            raw = st.session_state.quick_email
            candidatos = [e.strip() for e in re.split(r"[,\n\s]+", raw) if e.strip()]
            if candidatos:
                if len(candidatos) == 1:
                    invitados_texto = candidatos[0]
                elif len(candidatos) == 2:
                    invitados_texto = f"{candidatos[0]} y {candidatos[1]}"
                else:
                    invitados_texto = ", ".join(candidatos[:-1]) + f" y {candidatos[-1]}"
                extras.append(f"invita también a {invitados_texto}")
        if st.session_state.get('direccion_reunion'):
            extras.append(f"la dirección es {st.session_state.direccion_reunion}")
        final_prompt = prompt if not extras else f"{prompt}. Por favor, {', y '.join(extras)}."

        st.session_state.chat.append(("user", final_prompt))
        with st.chat_message("user"):
            st.markdown(final_prompt)

        # Llamar a n8n
        if not N8N_URL:
            err_html = """
            <div class="chat-error-card">
                <div class="chat-error-title">⚠️ n8n no configurado</div>
                <div class="chat-error-detail">Define <strong>N8N_CREATE_MEETING_WEBHOOK_URL</strong> en el archivo <code>.env</code> para habilitar la creación de reuniones vía chat.</div>
            </div>
            """
            with st.chat_message("assistant"):
                st.markdown(err_html, unsafe_allow_html=True)
            st.session_state.chat.append(("assistant", err_html))
            st.session_state["chat_reset_pending"] = True
            st.rerun()
            return

        # Iniciar medición de tiempo
        inicio = time.time()
        payload = {"creador_id": st.session_state.session["id"], "mensaje": final_prompt}

        def esc_html(text):
            import html
            return html.escape(str(text))

        with st.spinner("Procesando solicitud con n8n…"):
            try:
                resp = requests.post(N8N_URL, json=payload, timeout=90)
                tiempo_respuesta = time.time() - inicio
                # Registrar métrica de la petición
                registrar_metrica_n8n(
                    endpoint="crear_reunion_chat",
                    tiempo_respuesta=tiempo_respuesta,
                    estado="éxito" if resp.status_code == 200 else "error",
                    codigo_estado=resp.status_code,
                    detalles=f"Tiempo de respuesta: {tiempo_respuesta:.2f}s"
                )
                
                if resp.status_code == 200:
                    data = resp.json()
                    tema = esc_html(data.get('meeting', {}).get('tema', ''))
                    fecha = esc_html(data.get('meeting', {}).get('fecha', ''))
                    tipo_resp = data.get('meeting', {}).get('tipo') or data.get('tipo')
                    dir_resp = data.get('meeting', {}).get('direccion') or data.get('direccion')
                    join_url = data.get('meeting', {}).get('join_url', '')

                    # Normalizar invitados a texto (preferir meeting.destinatarios)
                    participantes_emails = []
                    tema_val = data.get('meeting', {}).get('tema')
                    if tema_val:
                        try:
                            rlist = sb_select(
                                "reuniones",
                                {
                                    "select": "id,tema,fecha_inicio",
                                    "tema": f"eq.{tema_val}",
                                    "order": "fecha_inicio.desc",
                                    "limit": "1",
                                },
                            )
                            if rlist:
                                rid = rlist[0]["id"]
                                parts = sb_select(
                                    "participantes",
                                    {"select": "correo", "reunion_id": f"eq.{rid}"},
                                )
                                participantes_emails = [
                                    p.get("correo") for p in parts if p.get("correo")
                                ]
                        except Exception:
                            participantes_emails = []

                    if not participantes_emails:
                        raw_dest = data.get('meeting', {}).get('destinatarios')
                        if raw_dest is None:
                            raw_dest = data.get('destinatarios', [])
                        tmp = []
                        for d in raw_dest:
                            if isinstance(d, dict):
                                val = d.get("email") or d.get("correo") or d.get("name") or d.get("nombre") or d.get("value")
                                if val:
                                    tmp.append(str(val))
                            else:
                                tmp.append(str(d))
                        participantes_emails = tmp

                    invitados_html = esc_html(', '.join(participantes_emails)) if participantes_emails else ""
                    es_presencial = bool(tipo_resp) and str(tipo_resp).strip().lower() == "presencial"

                    rows_html = ""
                    rows_html += f'<div class="chat-response-row"><span class="chat-response-label">Tema</span><span class="chat-response-value">{tema}</span></div>'
                    rows_html += f'<div class="chat-response-row"><span class="chat-response-label">Fecha</span><span class="chat-response-value">{fecha}</span></div>'
                    if not es_presencial and join_url:
                        rows_html += f'<div class="chat-response-row"><span class="chat-response-label">Enlace</span><span class="chat-response-link"><a href="{esc_html(join_url)}" target="_blank">{esc_html(join_url)}</a></span></div>'
                    if invitados_html:
                        rows_html += f'<div class="chat-response-row"><span class="chat-response-label">Invitados</span><span class="chat-response-value">{invitados_html}</span></div>'
                    if not es_presencial:
                        if tipo_resp:
                            rows_html += f'<div class="chat-response-row"><span class="chat-response-label">Tipo</span><span class="chat-response-value">{esc_html(tipo_resp)}</span></div>'
                        if dir_resp:
                            rows_html += f'<div class="chat-response-row"><span class="chat-response-label">Dirección</span><span class="chat-response-value">{esc_html(dir_resp)}</span></div>'

                    resumen_html = f"""
                    <div class="chat-response-card">
                        <div class="chat-response-title">✅ Reunión creada</div>
                        {rows_html}
                    </div>
                    """
                    st.session_state.chat.append(("assistant", resumen_html))
                    with st.chat_message("assistant"):
                        st.markdown(resumen_html, unsafe_allow_html=True)
                    st.session_state["chat_reset_pending"] = True
                    st.rerun()
                else:
                    err_detail = esc_html(f"{resp.status_code} - {resp.text[:300]}")
                    registrar_metrica_n8n(
                        endpoint="crear_reunion_chat",
                        tiempo_respuesta=tiempo_respuesta,
                        estado="error",
                        codigo_estado=resp.status_code,
                        detalles=f"Error en la respuesta: {resp.text[:200]}"
                    )
                    err_html = f"""
                    <div class="chat-error-card">
                        <div class="chat-error-title">❌ Error al crear reunión</div>
                        <div class="chat-error-detail">{err_detail}</div>
                    </div>
                    """
                    st.session_state.chat.append(("assistant", err_html))
                    with st.chat_message("assistant"):
                        st.markdown(err_html, unsafe_allow_html=True)
                    st.session_state["chat_reset_pending"] = True
                    st.rerun()
            except Exception as e:
                tiempo_respuesta = time.time() - inicio if 'inicio' in locals() else 0
                registrar_metrica_n8n(
                    endpoint="crear_reunion_chat",
                    tiempo_respuesta=tiempo_respuesta,
                    estado="error",
                    detalles=f"Excepción: {str(e)}"
                )
                err_html = f"""
                <div class="chat-error-card">
                    <div class="chat-error-title">❌ Error de conexión</div>
                    <div class="chat-error-detail">{esc_html(str(e))}</div>
                </div>
                """
                st.session_state.chat.append(("assistant", err_html))
                with st.chat_message("assistant"):
                    st.markdown(err_html, unsafe_allow_html=True)
                st.session_state["chat_reset_pending"] = True
                st.rerun()


# -------- Usuarios --------
def view_usuarios():
    st.title("👥 Gestión de Usuarios")
    admin = is_admin()

    # -------- FILTROS --------
    st.subheader("Filtros")

    filtro_texto = st.text_input("Buscar por nombre o correo", placeholder="Escribe para filtrar...")
    filtro_nivel = st.selectbox("Filtrar por nivel", ["Todos", "basico", "pro", "enterprise"])
    filtro_estado = st.selectbox("Filtrar por estado", ["Todos", "activo", "cancelado", "suspendido"])

    # -------- OBTENER USUARIOS --------
    try:
        users = sb_select("usuarios", {"select":"id,nombre,correo,nivel_suscripcion,estado_suscripcion,fecha_creacion"})
    except Exception as e:
        st.error(f"Error cargando usuarios: {e}")
        return
    
    # Convert FECHA (streamlit needs)
    for u in users:
        if "fecha_creacion" in u and u["fecha_creacion"]:
            u["fecha_creacion"] = u["fecha_creacion"].replace("T", " ").replace("Z", "")

    users_df = pd.DataFrame(users)

    # -------- APLICAR FILTROS --------
    if filtro_texto:
        mask = users_df["nombre"].str.contains(filtro_texto, case=False, na=False) | \
               users_df["correo"].str.contains(filtro_texto, case=False, na=False)
        users_df = users_df[mask]

    if filtro_nivel != "Todos":
        users_df = users_df[users_df["nivel_suscripcion"] == filtro_nivel]

    if filtro_estado != "Todos":
        users_df = users_df[users_df["estado_suscripcion"] == filtro_estado]

    # Orden por fecha
    users_df = users_df.sort_values(by="fecha_creacion", ascending=False)

    # -------- Gráfico: Usuarios por nivel --------
    st.caption("Distribución por nivel de suscripción")
    try:
        cdata = users_df.groupby("nivel_suscripcion").size().reset_index(name="usuarios")
        chart = alt.Chart(cdata).mark_arc(innerRadius=40).encode(
            theta=alt.Theta("usuarios:Q", stack=True),
            color=alt.Color("nivel_suscripcion:N", scale=alt.Scale(scheme="category10")),
            tooltip=["nivel_suscripcion:N", "usuarios:Q"]
        ).properties(height=200)
        st.altair_chart(chart, use_container_width=True)
    except Exception:
        pass

    st.subheader("Usuarios")

    # -------- EDITOR DE TABLA --------
    edited_df = st.data_editor(
        users_df,
        use_container_width=True,
        hide_index=True,
        key="tabla_usuarios",
        column_config={
            "nombre": st.column_config.TextColumn("Nombre"),
            "correo": st.column_config.TextColumn("Correo"),
            "nivel_suscripcion": st.column_config.SelectboxColumn(
                "Nivel",
                options=["basico", "pro", "enterprise"]
            ),
            "estado_suscripcion": st.column_config.SelectboxColumn(
                "Estado",
                options=["activo", "cancelado", "suspendido"]
            ),
            "fecha_creacion": st.column_config.DatetimeColumn("Fecha Registro")
        },
        disabled=[
            "id", "fecha_creacion",
            *([] if admin else ["nombre","correo","nivel_suscripcion","estado_suscripcion"])
        ]
    )

    # Detectar cambios
    if admin and st.button("💾 Guardar cambios"):
        for i, row in edited_df.iterrows():
            original = next(u for u in users if u["id"] == row["id"])
            if dict(row) != original:
                try:
                    requests.patch(
                        f"{SUPABASE_URL}/rest/v1/usuarios",
                        headers={**HEADERS, "Prefer": "return=representation"},
                        params={"id": f"eq.{row['id']}"},
                        data=json.dumps({
                            "nombre": row["nombre"],
                            "correo": row["correo"],
                            "nivel_suscripcion": row["nivel_suscripcion"],
                            "estado_suscripcion": row["estado_suscripcion"]
                        })
                    )
                except Exception as e:
                    st.error(f"Error editando usuario {row['correo']}: {e}")

        st.success("✅ Cambios guardados")
        st.rerun()

    # -------- Exportar PDF --------
    col_exp1, col_exp2 = st.columns([1,3])
    with col_exp1:
        if st.button("📄 Exportar a PDF"):
            try:
                pdf_bytes = df_to_pdf_bytes("Reporte de Usuarios", users_df.reset_index(drop=True))
                st.session_state["usuarios_pdf_bytes"] = pdf_bytes
                st.success("PDF generado")
            except Exception as e:
                st.error(f"Error generando PDF: {e}")
    with col_exp2:
        if "usuarios_pdf_bytes" in st.session_state:
            st.download_button(
                label="⬇️ Descargar reporte PDF",
                data=st.session_state["usuarios_pdf_bytes"],
                file_name="reporte_usuarios.pdf",
                mime="application/pdf"
            )

    # -------- ELIMINAR USUARIO(S) --------
    if admin:
        st.subheader("Eliminar usuario(s)")
        # Construir opciones desde la tabla filtrada actual
        opciones = {}
        for r in users_df.to_dict("records"):
            label = f"{r.get('nombre','')} ({r.get('correo','')}) - ID {r.get('id')}"
            opciones[label] = r.get("id")

        seleccion_labels = st.multiselect(
            "Selecciona usuarios a eliminar",
            list(opciones.keys()),
            placeholder="Busca por nombre o correo"
        )

        confirm_text = st.text_input("Escribe ELIMINAR para confirmar", key="confirmar_eliminacion")
        eliminar_clicked = st.button("🗑 Eliminar seleccionados", type="primary")

        if eliminar_clicked:
            if not seleccion_labels:
                st.warning("No has seleccionado usuarios.")
            elif confirm_text.strip().upper() != "ELIMINAR":
                st.warning("Debes escribir ELIMINAR para confirmar.")
            else:
                errores = []
                for label in seleccion_labels:
                    user_id = opciones[label]
                    try:
                        requests.delete(
                            f"{SUPABASE_URL}/rest/v1/usuarios",
                            headers=HEADERS,
                            params={"id": f"eq.{user_id}"}
                        )
                    except Exception as e:
                        errores.append(f"ID {user_id}: {e}")
                if errores:
                    st.error("\n".join(["Errores al eliminar:"] + errores))
                else:
                    st.success("✅ Usuario(s) eliminado(s)")
                    st.rerun()

    # -------- CREAR NUEVO --------
    st.divider()
    if admin:
        st.subheader("➕ Registrar usuario nuevo")

    if admin:
        with st.form("nuevo_usuario"):
            nombre = st.text_input("Nombre")
            correo = st.text_input("Correo")
            pw = st.text_input("Contraseña", type="password")
            nivel = st.selectbox("Nivel", ["basico", "pro", "enterprise"])
            estado = st.selectbox("Estado", ["activo", "suspendido", "cancelado"])
            submit = st.form_submit_button("Crear usuario")

            if submit:
                if not (nombre and correo and pw):
                    st.warning("Completa todos los campos.")
                else:
                    sb_insert("usuarios", [{
                        "nombre": nombre,
                        "correo": correo,
                        "password_hash": hash_pw(pw),
                        "nivel_suscripcion": nivel,
                        "estado_suscripcion": estado
                    }])
                    st.success("✅ Usuario creado")
                    st.rerun()

# -------- Reuniones --------            
def view_reuniones():
    st.title("📅 Reuniones")
    admin = is_admin()

    # ---- Filtros ----
    col1, col2, col3 = st.columns(3)

    with col1:
        filtro_texto = st.text_input("Buscar por tema o creador", placeholder="ventas, actualización...")

    with col2:
        filtro_estado = st.selectbox("Estado", ["Todos", "programada", "completada", "cancelada"])

    with col3:
        filtro_fecha = st.date_input("Filtrar por fecha", value=None)

    # ---- Obtener reuniones ----
    try:
        reuniones = sb_select("reuniones", {"select":"id,tema,fecha_inicio,duracion_minutos,proveedor,id_externo,join_url,start_url,estado,creador_id,tipo,direccion"})
    except Exception as e:
        st.error(f"Error cargando reuniones: {e}")
        return

    # Formatear fechas
    for r in reuniones:
        r["fecha_inicio"] = r["fecha_inicio"].replace("T", " ").replace("Z", "") if r["fecha_inicio"] else r["fecha_inicio"]

    df = pd.DataFrame(reuniones)

    # ---- Aplicar filtros ----
    if filtro_texto:
        df = df[df["tema"].str.contains(filtro_texto, case=False, na=False)]

    if filtro_estado != "Todos":
        df = df[df["estado"] == filtro_estado]

    if filtro_fecha:
        filtro_str = filtro_fecha.strftime("%Y-%m-%d")
        df = df[df["fecha_inicio"].str.startswith(filtro_str)]

    df = df.sort_values(by="fecha_inicio", ascending=False)

    st.subheader("Reuniones registradas")

    edited_df = st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "tema": st.column_config.TextColumn("Tema"),
            "fecha_inicio": st.column_config.TextColumn("Fecha"),
            "duracion_minutos": st.column_config.NumberColumn("Duración (min)"),
            "estado": st.column_config.SelectboxColumn("Estado", options=["programada","completada","cancelada"]),
            "join_url": st.column_config.LinkColumn("Enlace Zoom"),
            "start_url": st.column_config.LinkColumn("Host Link"),
            "tipo": st.column_config.TextColumn("Tipo"),
            "direccion": st.column_config.TextColumn("Dirección")
        },
        disabled=(list(df.columns) if not admin else ["id", "creador_id", "id_externo", "proveedor", "tipo", "direccion"])
    )

    # ---- Gráficos compactos ----
    st.caption("Insights rápidos")
    colg1, colg2, colg3 = st.columns(3)
    # Reuniones por mes
    with colg1:
        try:
            dfg = df.copy()
            dfg["fecha_dt"] = pd.to_datetime(dfg["fecha_inicio"], errors="coerce")
            dfg = dfg.dropna(subset=["fecha_dt"]).copy()
            dfg["ym"] = dfg["fecha_dt"].dt.to_period("M").astype(str)
            cdata = dfg.groupby("ym").size().reset_index(name="reuniones")
            line = alt.Chart(cdata).mark_line(point=True, color="#1f77b4").encode(
                x=alt.X("ym:N", title="Mes"),
                y=alt.Y("reuniones:Q", title="Reuniones")
            )
            pts = alt.Chart(cdata).mark_point(size=60, color="#ff7f0e").encode(
                x="ym:N", y="reuniones:Q"
            )
            chart = (line + pts).properties(height=180)
            st.altair_chart(chart, use_container_width=True)
        except Exception:
            st.write("—")
    # Por tipo
    with colg2:
        try:
            cdata = df.groupby("tipo").size().reset_index(name="reuniones")
            chart = alt.Chart(cdata).mark_arc(innerRadius=40).encode(
                theta=alt.Theta("reuniones:Q", stack=True),
                color=alt.Color("tipo:N", scale=alt.Scale(scheme="category10")),
                tooltip=["tipo:N","reuniones:Q"]
            ).properties(height=200)
            st.altair_chart(chart, use_container_width=True)
        except Exception:
            st.write("—")
    # Por estado
    with colg3:
        try:
            cdata = df.groupby("estado").size().reset_index(name="reuniones")
            chart = alt.Chart(cdata).mark_bar(color="#6a3d9a").encode(
                y=alt.Y("estado:N", title="Estado", sort='-x'),
                x=alt.X("reuniones:Q", title="Reuniones"),
            ).properties(height=180)
            st.altair_chart(chart, use_container_width=True)
        except Exception:
            st.write("—")

    # ---- Guardar cambios (solo estado) ----
    if admin and st.button("💾 Guardar cambios"):
        for i, row in edited_df.iterrows():
            original = next(u for u in reuniones if u["id"] == row["id"])
            if row["estado"] != original["estado"]:
                try:
                    requests.patch(
                        f"{SUPABASE_URL}/rest/v1/reuniones",
                        headers={**HEADERS,"Prefer":"return=representation"},
                        params={"id": f"eq.{row['id']}"},
                        data=json.dumps({"estado": row["estado"]})
                    )
                except Exception as e:
                    st.error(f"Error actualizando reunión:: {e}")
        st.success("✅ Cambios guardados")
        st.rerun()

    # ---- Botones acción ----
    if admin:
        st.subheader("Acciones")

    # Selección por lista e ID
    opciones = {}
    for r in df.to_dict("records"):
        label = f"{r.get('tema','(Sin tema)')} — {r.get('fecha_inicio','')} (ID {r.get('id')})"
        opciones[label] = r.get("id")
    opciones_list = ["— Selecciona —"] + list(opciones.keys())
    sel_reu = st.selectbox("Escoge una reunión", opciones_list, key="sel_reu_admin")
    input_reu = st.text_input("O ingresa ID de reunión", key="id_reu_admin")

    chosen_id = None
    if sel_reu and sel_reu != "— Selecciona —":
        chosen_id = opciones[sel_reu]
    if input_reu:
        chosen_id = input_reu

    # Editar/Eliminar reunión seleccionada
    if admin and chosen_id:
        try:
            sel = sb_select("reuniones", {"select":"id,tema,fecha_inicio,duracion_minutos,proveedor,id_externo,join_url,start_url,estado,creador_id,tipo,direccion", "id": f"eq.{chosen_id}"})
        except Exception as e:
            st.error(f"Error cargando reunión: {e}")
            sel = []
        if sel:
            rec = sel[0]
            # Parse fecha Inicio
            try:
                dt = pd.to_datetime(rec.get("fecha_inicio")) if rec.get("fecha_inicio") else pd.to_datetime("now")
            except Exception:
                dt = pd.to_datetime("now")

            st.markdown("**Editar reunión**")
            etema = st.text_input("Tema", value=rec.get("tema") or "", key="edit_tema")
            cold, colt = st.columns(2)
            with cold:
                efecha = st.date_input("Fecha", value=dt.date(), key="edit_fecha")
            with colt:
                ehora = st.time_input("Hora", value=dt.time(), key="edit_hora")
            eduracion = st.number_input("Duración (min)", min_value=1, step=5, value=int(rec.get("duracion_minutos") or 30), key="edit_duracion")
            etipo = st.radio("Tipo", ["virtual","presencial","mixta"], index=["virtual","presencial","mixta"].index(str(rec.get("tipo") or "virtual").lower()), horizontal=True, key="edit_tipo")
            edireccion = st.text_input("Dirección (si aplica)", value=rec.get("direccion") or "", key="edit_direccion") if etipo in ["presencial","mixta"] else st.text_input("Dirección (si aplica)", value="", key="edit_direccion")
            eestado = st.selectbox("Estado", ["programada","completada","cancelada"], index=["programada","completada","cancelada"].index(rec.get("estado") or "programada"), key="edit_estado")
            ejoin = st.text_input("join_url", value=rec.get("join_url") or "", key="edit_join")
            estart = st.text_input("start_url", value=rec.get("start_url") or "", key="edit_start")
            eexterno = st.text_input("id_externo", value=rec.get("id_externo") or "", key="edit_externo")

            col_save, col_del = st.columns([2,1])
            with col_save:
                if st.button("💾 Guardar cambios", key="btn_save_reu"):
                    fecha_str = f"{efecha.isoformat()}T{ehora.strftime('%H:%M:%S')}"
                    payload = {
                        "tema": etema,
                        "fecha_inicio": fecha_str,
                        "duracion_minutos": int(eduracion),
                        "tipo": etipo,
                        "direccion": edireccion if etipo in ["presencial","mixta"] else None,
                        "estado": eestado,
                        "join_url": ejoin or None,
                        "start_url": estart or None,
                        "id_externo": eexterno or None,
                    }
                    try:
                        requests.patch(
                            f"{SUPABASE_URL}/rest/v1/reuniones",
                            headers={**HEADERS,"Prefer":"return=representation"},
                            params={"id": f"eq.{rec['id']}"},
                            data=json.dumps(payload)
                        )
                        st.success("✅ Reunión actualizada")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al actualizar: {e}")

            with col_del:
                if st.button("🗑 Eliminar reunión", key="btn_del_reu"):
                    try:
                        requests.delete(
                            f"{SUPABASE_URL}/rest/v1/reuniones",
                            headers=HEADERS,
                            params={"id": f"eq.{rec['id']}"}
                        )
                        st.success("Reunión eliminada")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al eliminar (verifica relaciones): {e}")

    if admin:
        st.divider()
        st.subheader("➕ Crear nueva reunión")
    if admin:
        ntema = st.text_input("Tema", key="new_tema")
        ncol1, ncol2 = st.columns(2)
        with ncol1:
            nfecha = st.date_input("Fecha", key="new_fecha")
        with ncol2:
            nhora = st.time_input("Hora", key="new_hora")
        nduracion = st.number_input("Duración (min)", min_value=1, step=5, value=30, key="new_duracion")
        ntipo = st.radio("Tipo", ["virtual","presencial","mixta"], horizontal=True, key="new_tipo")
        ndireccion = st.text_input("Dirección (si aplica)", key="new_direccion") if ntipo in ["presencial","mixta"] else st.text_input("Dirección (si aplica)", value="", key="new_direccion")

        if st.button("Crear reunión", key="btn_create_reu"):
            if not ntema:
                st.warning("Ingresa un tema")
            else:
                fecha_str = f"{nfecha.isoformat()}T{nhora.strftime('%H:%M:%S')}"
                row = {
                    "creador_id": st.session_state.session["id"],
                    "tema": ntema,
                    "fecha_inicio": fecha_str,
                    "duracion_minutos": int(nduracion),
                    "proveedor": "zoom",
                    "estado": "programada",
                    "tipo": ntipo,
                    "direccion": ndireccion if ntipo in ["presencial","mixta"] else None,
                }
                try:
                    sb_insert("reuniones", [row])
                    st.success("✅ Reunión creada")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error creando reunión: {e}")

# -------- Resumen de reuniones --------
def view_resumen_reuniones():
    st.title("📝 Resumen de reuniones")

    # Obtener reuniones con campos clave
    try:
        reuniones = sb_select(
            "reuniones",
            {"select": "id,tema,fecha_inicio,estado,tipo,direccion"}
        )
    except Exception as e:
        st.error(f"Error cargando reuniones: {e}")
        return

    # Formatear fecha para visualización
    for r in reuniones:
        if r.get("fecha_inicio"):
            r["fecha_inicio"] = r["fecha_inicio"].replace("T", " ").replace("Z", "")

    df_total = pd.DataFrame(reuniones)
    if df_total.empty:
        st.info("No hay reuniones registradas.")
        return

    # Asegurar columna tipo en minúsculas para filtro
    df_total["tipo"] = df_total["tipo"].astype(str).str.lower()

    col_v, col_p, col_m = st.columns(3)

    def render_columna(col, df_filtro, nombre, key_prefix):
      with col:
          st.subheader(nombre)
          mostrar_cols = [c for c in ["id","tema","fecha_inicio","estado","direccion"] if c in df_filtro.columns]
          st.dataframe(df_filtro[mostrar_cols].reset_index(drop=True), use_container_width=True)

          # Lista desplegable y/o búsqueda por ID de reunión
          opciones = {}
          for r in df_filtro.to_dict("records"):
              label = f"{r.get('tema','(Sin tema)')} — {r.get('fecha_inicio','')} (ID {r.get('id')})"
              opciones[label] = r.get("id")
          opciones_list = ["— Selecciona —"] + list(opciones.keys())
          sel_val = st.selectbox("Escoge una reunión", opciones_list, key=f"sel_{key_prefix}")

          st.caption("O busca por ID de la reunión")
          input_id = st.text_input("ID de reunión", key=f"id_{key_prefix}", placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")

          chosen_id = None
          if sel_val and sel_val != "— Selecciona —":
              chosen_id = opciones[sel_val]
          if input_id:
              chosen_id = input_id

          if chosen_id:
              # Buscar en el dataframe filtrado, o consultar directamente por ID
              fila = None
              if not df_filtro.empty and chosen_id in set(df_filtro["id"].astype(str)):
                  fila = df_filtro[df_filtro["id"].astype(str) == chosen_id].iloc[0].to_dict()
              else:
                  try:
                      q = sb_select(
                          "reuniones",
                          {"select":"id,tema,fecha_inicio,duracion_minutos,tipo,estado,direccion,join_url,start_url,proveedor,creador_id", "id": f"eq.{chosen_id}"}
                      )
                      if q:
                          fila = q[0]
                  except Exception as e:
                      st.error(f"Error buscando reunión: {e}")
                      return

              if fila:
                  # Detalles de la reunión
                  reunion_id = str(fila.get("id"))
                  st.markdown("**Detalles de la reunión**")
                  det = {
                      "ID": fila.get("id"),
                      "Tema": fila.get("tema"),
                      "Fecha": (fila.get("fecha_inicio") or "").replace("T"," ").replace("Z",""),
                      "Duración (min)": fila.get("duracion_minutos"),
                      "Tipo": fila.get("tipo"),
                      "Estado": fila.get("estado"),
                      "Dirección": fila.get("direccion"),
                      "Enlace": fila.get("join_url"),
                  }
                  st.json(det)
                  # Ver participantes de la reunión
                  if st.button("👥 Ver participantes", key=f"ver_part_{key_prefix}"):
                      try:
                          parts = sb_select(
                              "participantes",
                              {"select":"correo,rol,estado_invitacion,fecha_creacion", "reunion_id": f"eq.{reunion_id}"}
                          )
                          if not parts:
                              st.info("No hay participantes registrados para esta reunión.")
                          else:
                              # Formatear fecha
                              for p in parts:
                                  if p.get("fecha_creacion"):
                                      p["fecha_creacion"] = p["fecha_creacion"].replace("T"," ").replace("Z","")
                              with st.expander("Participantes", expanded=False):
                                  st.dataframe(pd.DataFrame(parts), use_container_width=True)
                                  # Métricas rápidas
                                  total = len(parts)
                                  orgs = sum(1 for p in parts if str(p.get("rol","")) == "organizador")
                                  partics = sum(1 for p in parts if str(p.get("rol","")) == "participante")
                                  m1, m2, m3 = st.columns(3)
                                  m1.metric("Total", total)
                                  m2.metric("Organizadores", orgs)
                                  m3.metric("Participantes", partics)
                                  # Donut de estados de invitación
                                  try:
                                      dfc = pd.DataFrame(parts)
                                      cdata = dfc.groupby("estado_invitacion").size().reset_index(name="conteo")
                                      chart = alt.Chart(cdata).mark_arc(innerRadius=40).encode(
                                          theta=alt.Theta("conteo:Q", stack=True),
                                          color=alt.Color("estado_invitacion:N", scale=alt.Scale(scheme="pastel2")),
                                          tooltip=["estado_invitacion:N","conteo:Q"]
                                      ).properties(height=180)
                                      st.altair_chart(chart, use_container_width=True)
                                  except Exception:
                                      pass
                      except Exception as e:
                          st.error(f"Error cargando participantes: {e}")

                  # Resumen existente
                  try:
                      res = sb_select(
                          "resumenes",
                          {"select": "id,reunion_id,resumen,fecha_creacion", "reunion_id": f"eq.{reunion_id}"}
                      )
                  except Exception as e:
                      st.error(f"Error cargando resumen: {e}")
                      return

                  if res:
                      item = res[0]
                      st.markdown("**Resumen**")
                      st.write(item.get("resumen") or "(Vacío)")
                      if item.get("fecha_creacion"):
                          st.caption(f"Creado: {item['fecha_creacion'].replace('T',' ').replace('Z','')}")
                  else:
                      st.info("No existe un resumen para esta reunión.")

                  # Generación según tipo
                  tipo_val = str(fila.get("tipo") or "").lower()
                  if tipo_val in ["virtual", "mixta"]:
                      btn = st.button("📝 Generar resumen (IA)", key=f"gen_{key_prefix}")
                      if btn:
                          if not N8N_RESUMEN_VIRTUAL_URL:
                              st.error("Configura N8N_RESUMEN_VIRTUAL_WEBHOOK_URL en .env")
                          else:
                              try:
                                  inicio = time.time()
                                  with st.spinner("Generando resumen..."):
                                      resp = requests.post(N8N_RESUMEN_VIRTUAL_URL, json={"reunion_id": reunion_id}, timeout=120)
                                  
                                  # Calcular tiempo de respuesta
                                  tiempo_respuesta = time.time() - inicio
                                  tamano_respuesta = len(resp.content) if resp.content else 0
                                  
                                  # Registrar métrica
                                  registrar_metrica_n8n(
                                      endpoint="resumen_virtual",
                                      tiempo_respuesta=tiempo_respuesta,
                                      estado="éxito" if resp.status_code == 200 else "error",
                                      codigo_estado=resp.status_code,
                                      reunion_id=reunion_id,
                                      tamano_respuesta=tamano_respuesta
                                  )
                                  
                                  if resp.status_code == 200:
                                      data = resp.json()
                                      resumen_texto = data.get("resumen") or data.get("summary") or ""
                                      if resumen_texto:
                                          if save_resumen(reunion_id, resumen_texto):
                                              st.success("✅ Resumen generado y guardado")
                                              st.write(resumen_texto)
                                              if st.button("🔄 Actualizar", key=f"refresh_{key_prefix}"):
                                                  st.rerun()
                                          else:
                                              st.error("No se pudo guardar el resumen")
                                      else:
                                          st.error("El flujo no devolvió un resumen")
                                  else:
                                      st.error(f"Error n8n: {resp.status_code} - {resp.text}")
                              except Exception as e:
                                  # Registrar error en métricas
                                  registrar_metrica_n8n(
                                      endpoint="resumen_virtual",
                                      tiempo_respuesta=0,
                                      estado="error",
                                      detalles=f"Excepción: {str(e)}",
                                      reunion_id=reunion_id
                                  )
                                  st.error(f"Error solicitando resumen: {e}")
                  elif tipo_val == "presencial":
                      # Verificar si ya existe un resumen para esta reunión
                      resumen_existente = sb_select("resumenes", {"select": "id,resumen,fecha_creacion", "reunion_id": f"eq.{reunion_id}"})
                      
                      if resumen_existente and resumen_existente[0].get("resumen"):
                          # Mostrar el resumen existente
                          item = resumen_existente[0]
                          st.markdown("### 📄 Resumen existente")
                          st.write(item.get("resumen"))
                          if item.get("fecha_creacion"):
                              st.caption(f"Creado: {item['fecha_creacion'].replace('T',' ').replace('Z','')}")
                      else:
                          # Mostrar opción para subir PDF solo si no hay resumen
                          archivo_pdf = st.file_uploader("Sube el acta (PDF)", type=["pdf"], key=f"pdf_{key_prefix}")
                          if archivo_pdf is not None:
                              st.success(f"Archivo cargado: {archivo_pdf.name}")
                          btnp = st.button("🚀 Procesar PDF y generar resumen", key=f"genpdf_{key_prefix}")
                          if btnp:
                              if not N8N_RESUMEN_PRESENCIAL_URL:
                                  st.error("Configura N8N_RESUMEN_PRESENCIAL_WEBHOOK_URL en .env")
                              elif not archivo_pdf:
                                  st.warning("Primero sube un PDF")
                              else:
                                  try:
                                      inicio = time.time()
                                      with st.spinner("Procesando acta y esperando resumen..."):
                                          # Enviar PDF al flujo n8n
                                          files = {"file": (archivo_pdf.name, archivo_pdf.getvalue(), "application/pdf")}
                                          data_form = {"reunion_id": reunion_id, "nombre_archivo": archivo_pdf.name}
                                          
                                          # Realizar la petición y medir tiempo
                                          inicio_request = time.time()
                                          resp = requests.post(N8N_RESUMEN_PRESENCIAL_URL, files=files, data=data_form, timeout=180)
                                          tiempo_respuesta = time.time() - inicio_request
                                          
                                          # Registrar métrica básica
                                          registrar_metrica_n8n(
                                              endpoint="resumen_presencial",
                                              tiempo_respuesta=tiempo_respuesta,
                                              estado="en_proceso" if resp.status_code == 200 else "error",
                                              codigo_estado=resp.status_code,
                                              reunion_id=reunion_id
                                          )

                                          # Iniciar seguimiento del tiempo total de procesamiento
                                          inicio_procesamiento = time.time()
                                          encontrado = False
                                          deadline = time.time() + 120  # hasta 2 minutos de espera
                                          
                                          while time.time() < deadline and not encontrado:
                                              try:
                                                  poll = sb_select("resumenes", {
                                                      "select": "id,reunion_id,resumen,fecha_creacion", 
                                                      "reunion_id": f"eq.{reunion_id}"
                                                  })
                                                  if poll and (poll[0].get("resumen") or "").strip():
                                                      item = poll[0]
                                                      tiempo_total = time.time() - inicio
                                                      
                                                      # Actualizar métrica con resultado exitoso
                                                      registrar_metrica_n8n(
                                                          endpoint="resumen_presencial",
                                                          tiempo_respuesta=tiempo_total,
                                                          estado="éxito",
                                                          codigo_estado=200,
                                                          reunion_id=reunion_id,
                                                          detalles=f"Tiempo total de procesamiento: {tiempo_total:.2f}s"
                                                      )
                                                      
                                                      st.success("✅ Resumen generado y guardado")
                                                      st.markdown("**Resumen**")
                                                      st.write(item.get("resumen"))
                                                      if item.get("fecha_creacion"):
                                                          st.caption(f"Creado: {item['fecha_creacion'].replace('T',' ').replace('Z','')}")
                                                      encontrado = True
                                                      break
                                              except Exception as e:
                                                  print(f"Error al consultar resumen: {e}")
                                              time.sleep(3)

                                          if not encontrado:
                                              tiempo_total = time.time() - inicio
                                              registrar_metrica_n8n(
                                                  endpoint="resumen_presencial",
                                                  tiempo_respuesta=tiempo_total,
                                                  estado="timeout",
                                                  reunion_id=reunion_id,
                                                  detalles="Tiempo de espera agotado esperando el resumen"
                                              )
                                              st.warning("Aún no se genera el resumen. Por favor, espera unos segundos y vuelve a intentar actualizar.")
                                  
                                  except requests.exceptions.Timeout:
                                      tiempo_total = time.time() - inicio
                                      registrar_metrica_n8n(
                                          endpoint="resumen_presencial",
                                          tiempo_respuesta=tiempo_total,
                                          estado="timeout",
                                          reunion_id=reunion_id,
                                          detalles="Timeout en la petición a n8n"
                                      )
                                      st.error("⏱️ Tiempo de espera agotado")
                                  except Exception as e:
                                      tiempo_total = time.time() - inicio
                                      registrar_metrica_n8n(
                                          endpoint="resumen_presencial",
                                          tiempo_respuesta=tiempo_total,
                                          estado="error",
                                          reunion_id=reunion_id,
                                          detalles=f"Excepción: {str(e)}"
                                      )
                                      st.error(f"Error al procesar el PDF: {e}")

    df_v = df_total[df_total["tipo"] == "virtual"]
    df_p = df_total[df_total["tipo"] == "presencial"]
    df_m = df_total[df_total["tipo"] == "mixta"]

    render_columna(col_v, df_v, "Virtual", "virtual")
    render_columna(col_p, df_p, "Presencial", "presencial")
    render_columna(col_m, df_m, "Mixta", "mixta")

# -------- Participantes --------
def view_participantes():
    st.title("👥 Participantes de Reuniones")
    admin = is_admin()

    opciones = {}
    try:
        lista = sb_select("reuniones", {"select": "id,tema,fecha_inicio,tipo"})
        for r in lista:
            label = f"{r.get('tema','(Sin tema)')} — {str(r.get('fecha_inicio') or '').replace('T',' ').replace('Z','')} ({r.get('tipo','')}) (ID {r.get('id')})"
            opciones[label] = r.get("id")
    except Exception:
        lista = []

    opciones_list = ["— Selecciona —"] + list(opciones.keys())
    sel_val = st.selectbox("Escoge una reunión", opciones_list, key="sel_participantes")
    input_id = st.text_input("ID de reunión", placeholder="Ingresa el ID de una reunión", key="id_participantes")

    chosen_id = None
    if sel_val and sel_val != "— Selecciona —":
        chosen_id = opciones[sel_val]
    if input_id:
        chosen_id = input_id

    if not chosen_id:
        st.info("Selecciona una reunión o ingresa un ID para ver participantes.")
        return
    
    try:
        participantes = sb_select(
            "participantes",
            {"select":"id,usuario_id,correo,rol,estado_invitacion,fecha_creacion,reunion_id",
             "reunion_id": f"eq.{chosen_id}"}
        )
    except Exception as e:
        st.error(f"Error cargando participantes: {e}")
        return

    # Si no hay participantes
    if not participantes:
        st.warning("No hay participantes registrados en esta reunión aún.")
    else:
        # Convertir fecha
        for p in participantes:
            p["fecha_creacion"] = p["fecha_creacion"].replace("T"," ").replace("Z","")

        df = pd.DataFrame(participantes)

        st.subheader("Lista de Participantes")

        # Pequeño gráfico de estado de invitaciones (donut)
        try:
            cdata = df.groupby("estado_invitacion").size().reset_index(name="conteo")
            chart = alt.Chart(cdata).mark_arc(innerRadius=40).encode(
                theta=alt.Theta("conteo:Q", stack=True),
                color=alt.Color("estado_invitacion:N", scale=alt.Scale(scheme="pastel2")),
                tooltip=["estado_invitacion:N","conteo:Q"]
            ).properties(height=180)
            st.altair_chart(chart, use_container_width=True)
        except Exception:
            pass

        edited_df = st.data_editor(
            df,
            use_container_width=True,
            key="tabla_participantes",
            hide_index=True,
            column_config={
                "correo": st.column_config.TextColumn("Correo"),
                "rol": st.column_config.SelectboxColumn("Rol", options=["participante","organizador"]),
                "estado_invitacion": st.column_config.SelectboxColumn(
                    "Estado", 
                    options=["enviado","aceptado","rechazado"]
                ),
                "fecha_creacion": st.column_config.DatetimeColumn("Registrado")
            },
            disabled=[
                "id","reunion_id","usuario_id","fecha_creacion",
                *([] if admin else ["correo","rol","estado_invitacion"])
            ]
        )

        # Guardar cambios
        if admin and st.button("💾 Guardar cambios participante(s)"):
            for i, row in edited_df.iterrows():
                original = next(p for p in participantes if p["id"] == row["id"])
                if dict(row) != original:
                    try:
                        requests.patch(
                            f"{SUPABASE_URL}/rest/v1/participantes",
                            headers={**HEADERS,"Prefer":"return=representation"},
                            params={"id": f"eq.{row['id']}"},
                            data=json.dumps({
                                "correo": row["correo"],
                                "rol": row["rol"],
                                "estado_invitacion": row["estado_invitacion"]
                            })
                        )
                    except Exception as e:
                        st.error(f"Error actualizando {row['correo']}: {e}")
            st.success("✅ Cambios guardados")
            st.rerun()

        # Eliminar participante
        if admin:
            st.subheader("🗑 Eliminar participante")
            del_id = st.text_input("ID de participante a eliminar")

            if st.button("Eliminar participante"):
                try:
                    requests.delete(
                        f"{SUPABASE_URL}/rest/v1/participantes",
                        headers=HEADERS,
                        params={"id":f"eq.{del_id}"}
                    )
                    st.success("Participante eliminado ✅")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    st.divider()
    if admin:
        st.subheader("➕ Agregar nuevo participante")

        new_email = st.text_input("Correo del participante")
        new_rol = st.selectbox("Rol", ["participante","organizador"])

        if st.button("Agregar participante"):
            if not new_email:
                st.warning("Ingresa un email.")
                return
            try:
                sb_insert("participantes", [{
                    "reunion_id": chosen_id,
                    "correo": new_email,
                    "rol": new_rol,
                    "estado_invitacion": "enviado"
                }])
                st.success("✅ Participante agregado")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")


# -------- Tareas --------
def view_tareas():
    st.title("📋 Gestión de Tareas")
    admin = is_admin()
    
    # -------- Obtener tareas con información de reunión --------
    try:
        # Obtener tareas con información de reunión
        tareas = sb_select("tareas", {
            "select": "id,reunion_id,descripcion,asignado_a_correo,estado,fecha_vencimiento,fecha_creacion"
        })
        
        # Obtener información de reuniones
        if tareas:
            # Obtener IDs únicos de reuniones
            reuniones_ids = list(set(t['reunion_id'] for t in tareas))
            
            # Obtener información de reuniones en lotes si hay muchas
            reuniones_info = {}
            for i in range(0, len(reuniones_ids), 10):  # Procesar en lotes de 10
                batch = reuniones_ids[i:i+10]
                params = {
                    "select": "id,tema,fecha_inicio",
                    "id": f"in.({','.join(str(r) for r in batch)})"
                }
                reuniones_batch = sb_select("reuniones", params)
                reuniones_info.update({r['id']: f"{r['tema']} ({r['fecha_inicio'][:10]})" for r in reuniones_batch})
            
            # Agregar nombre de reunión a cada tarea
            for tarea in tareas:
                tarea['reunion_nombre'] = reuniones_info.get(tarea['reunion_id'], 'Reunión desconocida')
    except Exception as e:
        st.error(f"Error cargando tareas: {e}")
        return
    
    if not tareas:
        st.info("No hay tareas registradas. Ejecuta el script SQL para insertar datos de ejemplo.")
        if admin:
            st.divider()
            st.subheader("➕ Crear nueva tarea")
            with st.form("nueva_tarea"):
                try:
                    reuniones = sb_select("reuniones", {"select": "id,tema,fecha_inicio", "order": "fecha_inicio.desc", "limit": "50"})
                    opciones_reuniones = {f"{r['tema']} ({r['fecha_inicio'][:10]})": r['id'] for r in reuniones}
                    reunion_sel = st.selectbox("Reunión", list(opciones_reuniones.keys()))
                    descripcion = st.text_area("Descripción de la tarea")
                    asignado = st.text_input("Asignado a (correo)")
                    estado = st.selectbox("Estado", ["pendiente", "en_progreso", "completada"])
                    fecha_venc = st.date_input("Fecha de vencimiento")
                    submit = st.form_submit_button("Crear tarea")
                    
                    if submit:
                        if not descripcion:
                            st.warning("Ingresa una descripción")
                        else:
                            sb_insert("tareas", [{
                                "reunion_id": opciones_reuniones[reunion_sel],
                                "descripcion": descripcion,
                                "asignado_a_correo": asignado if asignado else None,
                                "estado": estado,
                                "fecha_vencimiento": fecha_venc.isoformat()
                            }])
                            st.success("✅ Tarea creada")
                            st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        return
    
    # Formatear fechas y asegurar que los valores no sean None
    from datetime import datetime
    for t in tareas:
        # Asegurar que todos los campos tengan un valor por defecto si son None
        t["descripcion"] = t.get("descripcion") or "Sin descripción"
        t["asignado_a_correo"] = t.get("asignado_a_correo") or "No asignado"
        t["estado"] = t.get("estado") or "pendiente"
        
        # Formatear fechas
        if t.get("fecha_vencimiento"):
            t["fecha_vencimiento"] = t["fecha_vencimiento"].replace("T", " ").split("+")[0].split("Z")[0][:10]
        else:
            t["fecha_vencimiento"] = "Sin fecha"
            
        if t.get("fecha_creacion"):
            t["fecha_creacion"] = t["fecha_creacion"].replace("T", " ").split("+")[0].split("Z")[0]
        else:
            t["fecha_creacion"] = "Desconocida"
    
    # Crear DataFrame asegurando que todos los campos necesarios existan
    df = pd.DataFrame(tareas)
    
    # Asegurarse de que las columnas necesarias existan
    columnas_necesarias = ["descripcion", "asignado_a_correo", "estado", "fecha_vencimiento", "fecha_creacion", "reunion_nombre"]
    for col in columnas_necesarias:
        if col not in df.columns:
            df[col] = ""  # O un valor por defecto apropiado
    
    # -------- PANEL DE MÉTRICAS --------
    st.subheader("📊 Métricas Generales")
    
    total_tareas = len(df)
    completadas = len(df[df["estado"] == "completada"])
    pendientes = len(df[df["estado"] == "pendiente"])
    en_progreso = len(df[df["estado"] == "en_progreso"])
    
    # Calcular atrasadas (fecha_vencimiento < hoy y estado != completada)
    hoy = datetime.now().date()
    df_copy = df.copy()
    df_copy["fecha_venc_dt"] = pd.to_datetime(df_copy["fecha_vencimiento"], errors="coerce")
    atrasadas = len(df_copy[
        (df_copy["fecha_venc_dt"].dt.date < hoy) & 
        (df_copy["estado"] != "completada")
    ])
    
    # Porcentaje de avance
    porcentaje_avance = (completadas / total_tareas * 100) if total_tareas > 0 else 0
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Total Tareas", total_tareas)
    col2.metric("Completadas", completadas, delta=f"{porcentaje_avance:.1f}%")
    col3.metric("Pendientes", pendientes)
    col4.metric("En Progreso", en_progreso)
    col5.metric("Atrasadas", atrasadas, delta="⚠️" if atrasadas > 0 else "✅")
    col6.metric("% Avance", f"{porcentaje_avance:.1f}%")
    
    st.divider()
    
    # -------- GRÁFICOS ESTADÍSTICOS --------
    st.subheader("📈 Análisis Estadístico")
    
    colg1, colg2, colg3 = st.columns(3)
    
    # Gráfico 1: Tareas por estado
    with colg1:
        st.caption("Tareas por Estado")
        try:
            estado_data = df.groupby("estado").size().reset_index(name="cantidad")
            chart = alt.Chart(estado_data).mark_bar().encode(
                x=alt.X("estado:N", title="Estado", sort="-y"),
                y=alt.Y("cantidad:Q", title="Cantidad"),
                color=alt.Color("estado:N", scale=alt.Scale(
                    domain=["pendiente", "en_progreso", "completada"],
                    range=["#ff6b6b", "#ffd93d", "#6bcf7f"]
                )),
                tooltip=["estado:N", "cantidad:Q"]
            ).properties(height=250)
            st.altair_chart(chart, use_container_width=True)
        except Exception:
            st.write("—")
    
    # Gráfico 2: Tareas por usuario asignado
    with colg2:
        st.caption("Tareas por Usuario Asignado")
        try:
            df_asignadas = df[df["asignado_a_correo"].notna()].copy()
            if not df_asignadas.empty:
                usuario_data = df_asignadas.groupby("asignado_a_correo").size().reset_index(name="cantidad")
                # Tomar top 10
                usuario_data = usuario_data.nlargest(10, "cantidad")
                chart = alt.Chart(usuario_data).mark_arc(innerRadius=50).encode(
                    theta=alt.Theta("cantidad:Q", stack=True),
                    color=alt.Color("asignado_a_correo:N", legend=None),
                    tooltip=["asignado_a_correo:N", "cantidad:Q"]
                ).properties(height=250)
                st.altair_chart(chart, use_container_width=True)
            else:
                st.write("Sin tareas asignadas")
        except Exception:
            st.write("—")
    
    # Gráfico 3: Creación de tareas por semana
    with colg3:
        st.caption("Creación de Tareas por Semana")
        try:
            df_fechas = df.copy()
            df_fechas["fecha_creacion_dt"] = pd.to_datetime(df_fechas["fecha_creacion"], errors="coerce")
            df_fechas = df_fechas.dropna(subset=["fecha_creacion_dt"])
            df_fechas["semana"] = df_fechas["fecha_creacion_dt"].dt.to_period("W").astype(str)
            semana_data = df_fechas.groupby("semana").size().reset_index(name="cantidad")
            
            chart = alt.Chart(semana_data).mark_line(point=True, color="#4a90e2").encode(
                x=alt.X("semana:N", title="Semana"),
                y=alt.Y("cantidad:Q", title="Tareas Creadas"),
                tooltip=["semana:N", "cantidad:Q"]
            ).properties(height=250)
            st.altair_chart(chart, use_container_width=True)
        except Exception:
            st.write("—")
    
    st.divider()
    
    # -------- FILTROS --------
    st.subheader("🔍 Filtros y Búsqueda")
    
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    
    with col_f1:
        filtro_busqueda = st.text_input("Buscar en tareas/reuniones", placeholder="Escribe para buscar...")
    
    with col_f2:
        filtro_estado = st.selectbox("Estado", ["Todos", "pendiente", "en_progreso", "completada"])
    
    with col_f3:
        # Obtener lista de correos únicos (quitando valores nulos)
        correos_unicos = [x for x in df["asignado_a_correo"].dropna().unique() if x]
        filtro_asignado = st.selectbox(
            "Asignado a",
            ["Todos"] + sorted(correos_unicos, key=str.lower)
        )
        
    with col_f4:
        # Obtener reuniones únicas para el filtro
        reuniones_unicas = ["Todas"] + sorted(df["reunion_nombre"].unique().tolist())
        filtro_reunion = st.selectbox(
            "Reunión",
            reuniones_unicas
        )
    
    # Obtener lista de reuniones únicas para el filtro
    reuniones_unicas = df['reunion_nombre'].unique()
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    # Filtro de búsqueda
    if filtro_busqueda:
        df_filtrado = df_filtrado[
            df_filtrado["descripcion"].str.contains(filtro_busqueda, case=False, na=False) |
            df_filtrado["reunion_nombre"].str.contains(filtro_busqueda, case=False, na=False)
        ]
    
    # Filtro de estado
    if filtro_estado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["estado"] == filtro_estado]
    
    # Filtro de asignado
    if filtro_asignado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["asignado_a_correo"] == filtro_asignado]
    
    # Convertir fechas a formato datetime
    df_filtrado['fecha_vencimiento'] = pd.to_datetime(df_filtrado['fecha_vencimiento'], errors='coerce').dt.date
    
    # Ordenar por fecha de vencimiento
    df_filtrado = df_filtrado.sort_values(by="fecha_vencimiento", ascending=True)
    
    st.caption(f"Mostrando {len(df_filtrado)} de {len(df)} tareas")
    
    # -------- TABLA DE TAREAS --------
    st.subheader("📋 Tabla de Tareas")
    
    # Configuración de columnas
    column_config = {
        "reunion_id": st.column_config.TextColumn("ID Reunión", width="medium"),
        "reunion_nombre": st.column_config.TextColumn("Reunión", width="large"),
        "descripcion": st.column_config.TextColumn("Tarea", width="xlarge"),
        "asignado_a_correo": st.column_config.TextColumn("Asignado a", width="medium"),
        "estado": st.column_config.SelectboxColumn(
            "Estado",
            options=["pendiente", "en_progreso", "completada"],
            width="small"
        ),
        "fecha_vencimiento": st.column_config.DateColumn("Vencimiento", format="DD/MM/YYYY", width="small"),
        "fecha_creacion": st.column_config.DatetimeColumn("Creación", format="DD/MM/YYYY HH:mm", width="medium"),
        "id": None  # Ocultar columna ID
    }
    
    # Ordenar columnas para mejor visualización
    column_order = [
        'reunion_id', 'reunion_nombre', 'descripcion', 'asignado_a_correo', 
        'estado', 'fecha_vencimiento', 'fecha_creacion'
    ]
    
    # Asegurarse de que todas las columnas existan en el DataFrame
    column_order = [col for col in column_order if col in df_filtrado.columns]
    
    # Aplicar filtro de reunión si se seleccionó una específica
    if 'filtro_reunion' in locals() and filtro_reunion != "Todas":
        df_filtrado = df_filtrado[df_filtrado['reunion_nombre'] == filtro_reunion]
    
    # Asegurarse de que no haya valores NaN en las columnas clave
    for col in ['descripcion', 'asignado_a_correo', 'estado', 'reunion_nombre']:
        if col in df_filtrado.columns:
            df_filtrado[col] = df_filtrado[col].fillna('' if col != 'estado' else 'pendiente')
    
    # Mostrar el editor de datos
    try:
        # Para admin: puede editar todo excepto reunion_nombre y fecha_creacion
        # Para usuario regular: solo puede editar estado
        if admin:
            disabled_cols = ["reunion_nombre", "fecha_creacion", "reunion_id"]
        else:
            # Usuario regular solo puede editar estado
            disabled_cols = [col for col in column_order if col != "estado"]
        
        edited_df = st.data_editor(
            df_filtrado[column_order],
            use_container_width=True,
            hide_index=True,
            column_config=column_config,
            disabled=disabled_cols,
            height=min(600, 100 + len(df_filtrado) * 35),  # Altura dinámica
            key=f"tareas_editor_{len(df_filtrado)}"  # Clave única para forzar actualización
        )
    except Exception as e:
        st.error(f"Error al mostrar la tabla de tareas: {str(e)}")
        # Mostrar los datos en formato de tabla simple como respaldo
        st.dataframe(df_filtrado[column_order], use_container_width=True)
    
    # -------- EXPORTAR PDF --------
    st.divider()
    col_exp1, col_exp2 = st.columns([1, 3])
    with col_exp1:
        if st.button("📄 Exportar a PDF"):
            try:
                # Preparar DataFrame para PDF (convertir fechas a string)
                df_pdf = df_filtrado.copy()
                if 'fecha_vencimiento' in df_pdf.columns:
                    df_pdf['fecha_vencimiento'] = df_pdf['fecha_vencimiento'].astype(str)
                
                pdf_bytes = tareas_to_pdf_bytes("Reporte de Tareas", df_pdf)
                st.session_state["tareas_pdf_bytes"] = pdf_bytes
                st.success("PDF generado")
            except Exception as e:
                st.error(f"Error generando PDF: {e}")
    with col_exp2:
        if "tareas_pdf_bytes" in st.session_state:
            st.download_button(
                label="⬇️ Descargar reporte PDF",
                data=st.session_state["tareas_pdf_bytes"],
                file_name=f"tareas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf"
            )
    
    # -------- GUARDAR CAMBIOS --------
    st.divider()
    
    # Crear un mapeo de índice a ID para encontrar las tareas originales
    id_map = {i: row['id'] for i, row in df_filtrado.reset_index(drop=True).iterrows()}
    
    if admin:
        # Admin puede guardar todos los cambios
        if st.button("💾 Guardar cambios", type="primary", use_container_width=True):
            cambios_realizados = 0
            for i, row in edited_df.iterrows():
                # Obtener el ID de la tarea desde el mapeo
                tarea_id = id_map.get(i)
                if not tarea_id:
                    continue
                    
                original = next((t for t in tareas if t["id"] == tarea_id), None)
                if not original:
                    continue
                    
                updates = {}
                
                # Verificar cambios en el estado
                if "estado" in row and row["estado"] != original.get("estado"):
                    updates["estado"] = row["estado"]
                    
                # Verificar cambios en el asignado
                if "asignado_a_correo" in row and row["asignado_a_correo"] != original.get("asignado_a_correo"):
                    updates["asignado_a_correo"] = row["asignado_a_correo"] if pd.notna(row["asignado_a_correo"]) else None
                    
                # Verificar cambios en la descripción
                if "descripcion" in row and row["descripcion"] != original.get("descripcion"):
                    updates["descripcion"] = row["descripcion"]
                
                # Verificar cambios en fecha de vencimiento
                if "fecha_vencimiento" in row:
                    fecha_nueva = str(row["fecha_vencimiento"]) if pd.notna(row["fecha_vencimiento"]) else None
                    fecha_original = original.get("fecha_vencimiento", "")[:10] if original.get("fecha_vencimiento") else None
                    if fecha_nueva != fecha_original:
                        updates["fecha_vencimiento"] = fecha_nueva
                
                # Si hay cambios, actualizar
                if updates:
                    try:
                        response = requests.patch(
                            f"{SUPABASE_URL}/rest/v1/tareas",
                            headers={
                                **HEADERS, 
                                "Prefer": "return=representation",
                                "Content-Type": "application/json"
                            },
                            params={"id": f"eq.{tarea_id}"},
                            data=json.dumps(updates)
                        )
                        response.raise_for_status()
                        cambios_realizados += 1
                    except Exception as e:
                        st.error(f"Error actualizando tarea {tarea_id}: {str(e)}")
                        continue
                        
            if cambios_realizados > 0:
                st.success(f"✅ {cambios_realizados} tarea(s) actualizada(s)")
                st.rerun()
            else:
                st.info("No hay cambios para guardar")
    else:
        # Usuario regular solo puede cambiar estado
        if st.button("✅ Guardar cambios de estado", type="primary", use_container_width=True):
            cambios_realizados = 0
            for i, row in edited_df.iterrows():
                # Obtener el ID de la tarea desde el mapeo
                tarea_id = id_map.get(i)
                if not tarea_id:
                    continue
                    
                original = next((t for t in tareas if t["id"] == tarea_id), None)
                if not original:
                    continue
                
                # Solo verificar cambios en el estado
                if "estado" in row and row["estado"] != original.get("estado"):
                    try:
                        response = requests.patch(
                            f"{SUPABASE_URL}/rest/v1/tareas",
                            headers={
                                **HEADERS, 
                                "Prefer": "return=representation",
                                "Content-Type": "application/json"
                            },
                            params={"id": f"eq.{tarea_id}"},
                            data=json.dumps({"estado": row["estado"]})
                        )
                        response.raise_for_status()
                        cambios_realizados += 1
                    except Exception as e:
                        st.error(f"Error actualizando tarea {tarea_id}: {str(e)}")
                        continue
            
            if cambios_realizados > 0:
                st.success(f"✅ {cambios_realizados} tarea(s) actualizada(s)")
                st.rerun()
            else:
                st.info("No hay cambios de estado para guardar")
    
    # -------- CREAR NUEVA TAREA --------
    if admin:
        st.divider()
        st.subheader("➕ Crear nueva tarea")
        
        with st.form("nueva_tarea"):
            try:
                reuniones = sb_select("reuniones", {
                    "select": "id,tema,fecha_inicio",
                    "order": "fecha_inicio.desc",
                    "limit": "50"
                })
                opciones_reuniones = {f"{r['tema']} ({r['fecha_inicio'][:10]})": r['id'] for r in reuniones}
                
                reunion_sel = st.selectbox("Reunión", list(opciones_reuniones.keys()))
                descripcion = st.text_area("Descripción de la tarea", height=100)
                
                col_a1, col_a2 = st.columns(2)
                with col_a1:
                    asignado = st.text_input("Asignado a (correo)")
                with col_a2:
                    estado = st.selectbox("Estado", ["pendiente", "en_progreso", "completada"])
                
                fecha_venc = st.date_input("Fecha de vencimiento")
                submit = st.form_submit_button("Crear tarea", use_container_width=True)
                
                if submit:
                    if not descripcion:
                        st.warning("Ingresa una descripción")
                    else:
                        sb_insert("tareas", [{
                            "reunion_id": opciones_reuniones[reunion_sel],
                            "descripcion": descripcion,
                            "asignado_a_correo": asignado if asignado else None,
                            "estado": estado,
                            "fecha_vencimiento": fecha_venc.isoformat()
                        }])
                        st.success("✅ Tarea creada")
                        st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")


# -------- Estadísticas --------
def view_estadisticas():
    st.title("📊 Estadísticas")

    # Reuniones base
    try:
        reuniones = sb_select("reuniones", {"select": "id,tema,fecha_inicio,tipo,estado,duracion_minutos,creador_id"})
    except Exception as e:
        st.error(f"Error cargando reuniones: {e}")
        reuniones = []

    df_r = pd.DataFrame(reuniones)
    if not df_r.empty:
        if "fecha_inicio" in df_r.columns:
            df_r["fecha_dt"] = pd.to_datetime(df_r["fecha_inicio"], errors="coerce")
        else:
            df_r["fecha_dt"] = pd.NaT
        df_r["tipo"] = df_r.get("tipo", pd.Series(dtype=str)).astype(str).str.lower()
        df_r["estado"] = df_r.get("estado", pd.Series(dtype=str)).astype(str).str.lower()

        # Filtros de fecha
        min_date = df_r["fecha_dt"].min()
        max_date = df_r["fecha_dt"].max()
        if pd.isna(min_date) or pd.isna(max_date):
            rango = st.date_input("Rango de fechas", value=None)
        else:
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                fi = st.date_input("Desde", value=min_date.date())
            with col_f2:
                ff = st.date_input("Hasta", value=max_date.date())
            mask = (df_r["fecha_dt"].dt.date >= fi) & (df_r["fecha_dt"].dt.date <= ff)
            df_r = df_r[mask]

        # Métricas rápidas
        total_reu = len(df_r)
        dur_total = int(df_r.get("duracion_minutos", pd.Series(dtype=int)).fillna(0).sum()) if not df_r.empty else 0
        dur_prom = int(df_r.get("duracion_minutos", pd.Series(dtype=int)).fillna(0).mean()) if total_reu > 0 else 0
        c1, c2, c3 = st.columns(3)
        c1.metric("Reuniones", f"{total_reu}")
        c2.metric("Duración total (min)", f"{dur_total}")
        c3.metric("Duración promedio (min)", f"{dur_prom}")

        # Reuniones por mes
        st.subheader("Reuniones por mes")
        if not df_r.empty:
            df_r["ym"] = df_r["fecha_dt"].dt.to_period("M").astype(str)
            by_month = df_r.groupby("ym").size().reset_index(name="reuniones")
            by_month = by_month.sort_values("ym")
            st.bar_chart(by_month.set_index("ym"))

        # Por tipo y por estado
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Reuniones por tipo")
            if not df_r.empty:
                by_tipo = df_r.groupby("tipo").size().reset_index(name="reuniones")
                st.bar_chart(by_tipo.set_index("tipo"))
        with col_b:
            st.subheader("Reuniones por estado")
            if not df_r.empty:
                by_estado = df_r.groupby("estado").size().reset_index(name="reuniones")
                st.bar_chart(by_estado.set_index("estado"))

        # Duración promedio por tipo
        st.subheader("Duración promedio por tipo (min)")
        if not df_r.empty and "duracion_minutos" in df_r.columns:
            dur_tipo = df_r.groupby("tipo")["duracion_minutos"].mean().reset_index()
            st.bar_chart(dur_tipo.set_index("tipo"))

    # Participantes por reunión y estado de invitaciones
    try:
        partes = sb_select("participantes", {"select":"id,reunion_id,estado_invitacion"})
    except Exception:
        partes = []
    df_p = pd.DataFrame(partes)
    if not df_p.empty:
        st.subheader("Top 10 reuniones por número de participantes")
        top = df_p.groupby("reunion_id").size().reset_index(name="participantes").sort_values("participantes", ascending=False).head(10)
        st.bar_chart(top.set_index("reunion_id"))

        st.subheader("Estado de invitaciones")
        by_inv = df_p.groupby("estado_invitacion").size().reset_index(name="conteo")
        st.bar_chart(by_inv.set_index("estado_invitacion"))

    # Resúmenes: cobertura
    try:
        res = sb_select("resumenes", {"select":"id,reunion_id,fecha_creacion"})
    except Exception:
        res = []
    df_s = pd.DataFrame(res)
    if not df_s.empty and not df_r.empty:
        st.subheader("Cobertura de resúmenes")
        reuniones_con_resumen = df_s["reunion_id"].nunique()
        total_reu_base = len(df_r)
        cobertura = (reuniones_con_resumen / total_reu_base * 100) if total_reu_base > 0 else 0
        cc1, cc2 = st.columns(2)
        cc1.metric("Reuniones con resumen", f"{reuniones_con_resumen}")
        cc2.metric("Cobertura (%)", f"{cobertura:.1f}%")

        # Cobertura por tipo
        m = df_r[["id","tipo"]].merge(df_s, left_on="id", right_on="reunion_id", how="left")
        has_res = m.groupby("tipo").apply(lambda g: g["reunion_id"].notna().mean()*100 if len(g)>0 else 0).reset_index(name="cobertura_%")
        st.bar_chart(has_res.set_index("tipo"))

# -------- Métricas y Análisis --------
def view_metricas():
    st.title("📊 Métricas y Estadísticas")
    st.markdown("---")
    
    try:
        # Obtener las métricas de la base de datos
        metricas = sb_select("metricas_n8n", {
            "select": "*",
            "order": "fecha.desc",
            "limit": "1000"  # Últimos 1000 registros
        })
        
        if not metricas:
            st.info("No hay métricas registradas aún. Realiza algunas acciones para ver las estadísticas.")
            return
            
        # Convertir a DataFrame para facilitar el análisis
        df = pd.DataFrame(metricas)
        df['fecha'] = pd.to_datetime(df['fecha'])
        
        # Mostrar filtros en la barra lateral
        st.sidebar.header("Filtros")
        
        # Filtro de fechas
        fecha_min = df['fecha'].min().date()
        fecha_max = df['fecha'].max().date()
        
        # Asegurar que la fecha de inicio predeterminada esté dentro del rango permitido
        fecha_inicio_predeterminada = fecha_max - timedelta(days=min(30, (fecha_max - fecha_min).days))
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            fecha_inicio = st.date_input(
                "Fecha de inicio",
                value=min(fecha_inicio_predeterminada, fecha_max),
                min_value=fecha_min,
                max_value=fecha_max
            )
        with col2:
            fecha_fin = st.date_input(
                "Fecha de fin",
                value=fecha_max,
                min_value=fecha_inicio,  # No permitir fechas anteriores a la fecha de inicio
                max_value=fecha_max
            )
        
        # Filtrar por rango de fechas
        df_filtrado = df[(df['fecha'].dt.date >= fecha_inicio) & 
                        (df['fecha'].dt.date <= fecha_fin)]
        
        if df_filtrado.empty:
            st.warning("No hay datos para el rango de fechas seleccionado.")
            return
            
        # Mostrar métricas generales
        st.subheader("📈 Resumen General")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total = len(df_filtrado)
            st.metric("Total de peticiones", total)
            
        with col2:
            exito = len(df_filtrado[df_filtrado['estado'] == 'éxito'])
            st.metric("Peticiones exitosas", f"{exito} ({exito/max(total,1)*100:.1f}%)")
            
        with col3:
            error = len(df_filtrado[df_filtrado['estado'] == 'error'])
            st.metric("Errores", f"{error} ({error/max(total,1)*100:.1f}%)")
        
        st.markdown("---")
        
        # Gráfico 1: Peticiones por día
        st.subheader("📅 Peticiones por día")
        df_diario = df_filtrado.set_index('fecha').resample('D').size().reset_index(name='count')
        if not df_diario.empty:
            fig1 = px.line(df_diario, x='fecha', y='count', 
                          title='Evolución de peticiones a n8n',
                          labels={'count': 'Número de peticiones', 'fecha': 'Fecha'})
            st.plotly_chart(fig1, use_container_width=True)
        
        # Gráfico 2: Distribución por endpoint
        st.subheader("🌐 Distribución por endpoint")
        df_endpoint = df_filtrado.groupby('endpoint').size().reset_index(name='count')
        if not df_endpoint.empty:
            fig2 = px.pie(df_endpoint, values='count', names='endpoint', 
                         title='Peticiones por tipo de endpoint',
                         hole=0.3)
            st.plotly_chart(fig2, use_container_width=True)
        
        # Gráfico 3: Tiempo de respuesta por endpoint
        st.subheader("⏱️ Tiempo de respuesta promedio")
        df_tiempo = df_filtrado.groupby('endpoint')['tiempo_respuesta'].agg(['mean', 'count']).reset_index()
        df_tiempo = df_tiempo.sort_values('mean', ascending=False)
        if not df_tiempo.empty:
            fig3 = px.bar(df_tiempo, x='endpoint', y='mean',
                         title='Tiempo de respuesta promedio por endpoint (segundos)',
                         labels={'mean': 'Tiempo (s)', 'endpoint': 'Endpoint', 'count': 'Número de peticiones'},
                         hover_data=['count'])
            st.plotly_chart(fig3, use_container_width=True)
        
        # Gráfico 4: Estado de las peticiones
        st.subheader("✅ Estado de las peticiones")
        df_estado = df_filtrado.groupby('estado').size().reset_index(name='count')
        if not df_estado.empty:
            fig4 = px.bar(df_estado, x='estado', y='count', color='estado',
                         title='Distribución por estado de las peticiones',
                         labels={'count': 'Número de peticiones', 'estado': 'Estado'})
            st.plotly_chart(fig4, use_container_width=True)
        
        # Tabla con los últimos registros
        st.subheader("📝 Registros recientes")
        st.dataframe(df_filtrado[['fecha', 'endpoint', 'estado', 'tiempo_respuesta', 'detalles']]
                    .sort_values('fecha', ascending=False)
                    .head(20), 
                    use_container_width=True,
                    column_config={
                        'fecha': 'Fecha y Hora',
                        'endpoint': 'Endpoint',
                        'estado': 'Estado',
                        'tiempo_respuesta': 'Tiempo (s)',
                        'detalles': 'Detalles'
                    })
        
    except Exception as e:
        st.error(f"Error al cargar las métricas: {str(e)}")
        st.exception(e)

# -------- Router --------
inject_custom_styles()
if st.session_state.session is None:
    render_public_sidebar()
    t1, t2 = st.tabs(["Iniciar sesión", "Registrarse"])
    with t1: view_login()
    with t2: view_register()
else:
    admin = is_admin()
    opciones_menu = ["Chat", "Reuniones", "Tareas", "Resumen de reuniones", "Participantes", "Métricas", "Cerrar sesión"]
    if admin:
        opciones_menu.insert(1, "Usuarios")
    page = render_sidebar(opciones_menu, admin)
    if page == "Chat":
        view_chat()
    elif page == "Usuarios":
        view_usuarios()
    elif page == "Reuniones":
        view_reuniones()
    elif page == "Tareas":
        view_tareas()
    elif page == "Resumen de reuniones":
        view_resumen_reuniones()
    elif page == "Participantes":
        view_participantes()
    elif page == "Métricas":
        view_metricas()
    elif page == "Cerrar sesión":
        st.session_state.clear()
        st.rerun()
