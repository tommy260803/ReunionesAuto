"""
Router de reportes.

Endpoints para exportación de datos en PDF, Word y Excel.
"""

from io import BytesIO
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from app.core.dependencies import get_current_admin, get_current_investigator
from app.core.supabase_client import SupabaseClient, get_supabase

try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
except ImportError:
    pass  # Dependencias opcionales

from app.reports.generator import (
    check_format_availability,
    generate_report,
    get_missing_dependency,
)

router = APIRouter(prefix="/reports", tags=["Reportes"])


@router.get("", summary="Listar reportes disponibles")
async def list_reports(
    user: dict = Depends(get_current_investigator),
) -> list[dict]:
    """Devuelve lista de reportes exportables (análisis y experimentos completados)."""
    sb = get_supabase()
    reports: list[dict] = []

    try:
        analyses = sb.select(
            "statistical_analyses",
            {"select": "id,nombre,estado,fecha_creacion", "creado_por": f"eq.{user['id']}", "order": "fecha_creacion.desc"},
        )
    except Exception:
        analyses = []

    for a in analyses:
        reports.append({
            "id": a["id"],
            "nombre": a["nombre"],
            "tipo": "ANALISIS",
            "formato": "PDF",
            "fecha_generacion": a.get("fecha_creacion", ""),
            "estado": a["estado"],
        })

    try:
        experiments = sb.select(
            "experiment_sessions",
            {"select": "id,nombre,estado,fecha_inicio", "investigador_id": f"eq.{user['id']}", "order": "fecha_inicio.desc"},
        )
    except Exception:
        experiments = []

    for e in experiments:
        reports.append({
            "id": e["id"],
            "nombre": e["nombre"],
            "tipo": "EXPERIMENTO",
            "formato": "PDF",
            "fecha_generacion": e.get("fecha_inicio", ""),
            "estado": e["estado"],
        })

    return reports


def build_pdf(title: str, headers: list[str], rows: list[list[str]], filename: str) -> Response:
    """Genera un reporte tabular simple, manteniendo el PDF en memoria."""
    try:
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
    except ImportError:
        raise HTTPException(status_code=500, detail="reportlab no está instalado. Ejecute pip install reportlab")

    buf = BytesIO()
    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]
    normal_style.fontSize = 8
    normal_style.leading = 10
    header_style = styles["Heading4"]
    header_style.fontSize = 8
    header_style.alignment = 1
    data = [[Paragraph(f"<b>{header}</b>", header_style) for header in headers]]
    data.extend([[Paragraph(str(value or ""), normal_style) for value in row] for row in rows])
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), leftMargin=25, rightMargin=25, topMargin=35, bottomMargin=25)
    table = Table(data, repeatRows=1)
    table.setStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 1), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
    ])
    doc.build([Paragraph(title, styles["Title"]), Spacer(1, 10), table])
    pdf_bytes = buf.getvalue()
    buf.close()
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

@router.get("/users/pdf", summary="Exportar lista de usuarios a PDF (solo admin)")
async def export_users_pdf(
    admin: dict = Depends(get_current_admin),
    sb: SupabaseClient = Depends(get_supabase)
):
    try:
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
    except ImportError:
        raise HTTPException(status_code=500, detail="reportlab no está instalado. Ejecute pip install reportlab")
        
    try:
        # Obtener datos
        rows = sb.select(
            "usuarios", 
            {"select": "id,nombre,correo,nivel_suscripcion,estado_suscripcion,fecha_creacion", "order": "fecha_creacion.desc"}
        )
        
        # Generar PDF en memoria
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
        normal_style = styles["Normal"]
        normal_style.fontSize = 8
        normal_style.leading = 10
        
        header_style = styles["Heading4"]
        header_style.fontSize = 9
        header_style.leading = 12
        header_style.alignment = 1
        
        title_style = styles["Title"]
        title_style.fontSize = 14
        
        story = []
        story.append(Paragraph("Reporte de Usuarios", title_style))
        story.append(Spacer(1, 10))
        
        cols = ["id", "nombre", "correo", "nivel_suscripcion", "estado_suscripcion", "fecha_creacion"]
        
        # Encabezados
        headers = []
        headers.append(Paragraph("<b>ID</b>", header_style))
        headers.append(Paragraph("<b>Nombre</b>", header_style))
        headers.append(Paragraph("<b>Correo</b>", header_style))
        headers.append(Paragraph("<b>Nivel</b>", header_style))
        headers.append(Paragraph("<b>Estado</b>", header_style))
        headers.append(Paragraph("<b>Fecha</b>", header_style))
        
        data = [headers]
        
        # Filas
        for row in rows:
            fila_pdf = []
            for col in cols:
                val = row.get(col, "")
                if col == "fecha_creacion" and val:
                    val = val.replace("T", " ").split(".")[0]
                fila_pdf.append(Paragraph(str(val), normal_style))
            data.append(fila_pdf)
            
        # Tabla y estilos
        table = Table(
            data,
            colWidths=[40, 100, 120, 60, 60, 80],
            repeatRows=1
        )
        
        table_style = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("FONTNAME", (0, 0), (-1, 0), 'Helvetica-Bold'),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 1), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
        ]
        
        # Filas alternas
        for i in range(1, len(data)):
            if i % 2 == 0:
                table_style.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#f8fafc")))
                
        table.setStyle(table_style)
        story.append(table)
        
        # Construir
        doc.build(story)
        pdf_bytes = buf.getvalue()
        buf.close()
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="reporte_usuarios.pdf"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/pdf", summary="Exportar lista de tareas a PDF")
async def export_tasks_pdf(
    admin: dict = Depends(get_current_admin),
    sb: SupabaseClient = Depends(get_supabase),
):
    try:
        tasks = sb.select(
            "tareas",
            {"select": "reunion_id,descripcion,asignado_a_correo,estado,fecha_vencimiento", "order": "fecha_creacion.desc"},
        )
        meeting_ids = ",".join(str(task["reunion_id"]) for task in tasks if task.get("reunion_id"))
        meetings = sb.select("reuniones", {"select": "id,tema", "id": f"in.({meeting_ids})"}) if meeting_ids else []
        meeting_names = {str(meeting["id"]): meeting.get("tema", "Sin reunión") for meeting in meetings}
        rows = []
        for task in tasks:
            due_date = (task.get("fecha_vencimiento") or "").replace("T", " ").split(".")[0]
            rows.append([
                meeting_names.get(str(task.get("reunion_id")), "Sin reunión"),
                task.get("descripcion", ""),
                task.get("asignado_a_correo", "Sin asignar"),
                task.get("estado", "").replace("_", " "),
                due_date,
            ])
        return build_pdf(
            "Reporte de Tareas",
            ["Reunión", "Descripción", "Asignado a", "Estado", "Vencimiento"],
            rows,
            "reporte_tareas.pdf",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/research/generate", summary="Generar reporte de investigación")
async def generate_research_report(
    report_type: str,
    format_type: str,
    data: dict[str, Any],
    title: str,
    user: dict = Depends(get_current_investigator),
) -> Response:
    """
    Genera un reporte de investigación en el formato solicitado.
    
    Args:
        report_type: Tipo de reporte (ANALISIS, EXPERIMENTO, EVALUACION)
        format_type: Formato (PDF, WORD, EXCEL)
        data: Datos del reporte
        title: Título del reporte
    """
    # Verificar disponibilidad del formato
    availability = check_format_availability(format_type)
    if not availability["available"]:
        raise HTTPException(
            status_code=500,
            detail=f"Formato {format_type} no disponible. Dependencia faltante: {availability['missing_dependency']}"
        )
    
    try:
        report_bytes = generate_report(report_type, format_type, data, title)
        
        # Determinar media type y extensión
        media_types = {
            "PDF": "application/pdf",
            "WORD": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "EXCEL": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }
        
        extensions = {
            "PDF": "pdf",
            "WORD": "docx",
            "EXCEL": "xlsx",
        }
        
        filename = f"{title.replace(' ', '_').lower()}.{extensions[format_type]}"
        
        return Response(
            content=report_bytes,
            media_type=media_types[format_type],
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando reporte: {str(e)}")


@router.get("/research/analyses/{analysis_id}/export", summary="Exportar análisis a PDF/Word/Excel")
async def export_analysis_report(
    analysis_id: UUID,
    format_type: str = "PDF",
    user: dict = Depends(get_current_investigator),
    sb: SupabaseClient = Depends(get_supabase),
) -> Response:
    """Exporta un análisis estadístico al formato solicitado."""
    # Obtener análisis
    analysis = sb.select("statistical_analyses", {"select": "*", "id": f"eq.{analysis_id}"})
    if not analysis:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")
    
    # Verificar permisos
    if analysis[0]["creado_por"] != user["id"] and user.get("rol") != "ADMIN":
        raise HTTPException(status_code=403, detail="No tienes permiso para exportar este análisis")
    
    # Obtener resultados
    results = sb.select("statistical_analysis_results", {"select": "*", "analysis_id": f"eq.{analysis_id}"})
    
    # Preparar datos
    data = {
        "nombre": analysis[0]["nombre"],
        "objetivo": analysis[0]["objetivo"],
        "variable_resultado": analysis[0]["variable_resultado"],
        "diseno": analysis[0]["diseno"],
        "prueba_ejecutada": analysis[0]["prueba_ejecutada"],
        "alpha": analysis[0]["alpha"],
        "correccion_multiple": analysis[0]["correccion_multiple"],
    }
    
    if results:
        data.update(results[0])
    
    return await generate_research_report(
        report_type="ANALISIS",
        format_type=format_type,
        data=data,
        title=analysis[0]["nombre"],
        user=user,
    )


@router.get("/research/experiments/{experiment_id}/export", summary="Exportar experimento a PDF/Word/Excel")
async def export_experiment_report(
    experiment_id: UUID,
    format_type: str = "PDF",
    user: dict = Depends(get_current_investigator),
    sb: SupabaseClient = Depends(get_supabase),
) -> Response:
    """Exporta una sesión experimental al formato solicitado."""
    # Obtener experimento
    experiment = sb.select("experiment_sessions", {"select": "*", "id": f"eq.{experiment_id}"})
    if not experiment:
        raise HTTPException(status_code=404, detail="Sesión experimental no encontrada")
    
    # Verificar permisos
    if experiment[0]["creado_por"] != user["id"] and user.get("rol") != "ADMIN":
        raise HTTPException(status_code=403, detail="No tienes permiso para exportar esta sesión")
    
    return await generate_research_report(
        report_type="EXPERIMENTO",
        format_type=format_type,
        data=experiment[0],
        title=experiment[0]["nombre"],
        user=user,
    )
