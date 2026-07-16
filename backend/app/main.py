"""
Punto de entrada de la aplicación FastAPI.

Configura middlewares (CORS), incluye routers, registra manejadores
de errores globales y expone un endpoint /health para verificar que
el servicio está activo.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.meetings.router import router as meetings_router
from app.participants.router import router as participants_router
from app.tasks.router import router as tasks_router
from app.automation.router import router as automation_router
from app.summaries.router import router as summaries_router
from app.metrics.router import router as metrics_router
from app.reports.router import router as reports_router

# ------------------------------------------------------------------
# Instancia de FastAPI
# ------------------------------------------------------------------

app = FastAPI(
    title="ReunionesAuto API",
    description="Backend para la gestión automática de reuniones Zoom.",
    version="1.0.0",
)

# ------------------------------------------------------------------
# CORS
# ------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# Routers
# ------------------------------------------------------------------

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(meetings_router)
app.include_router(participants_router)
app.include_router(tasks_router)
app.include_router(automation_router)
app.include_router(summaries_router)
app.include_router(metrics_router)
app.include_router(reports_router)

# ------------------------------------------------------------------
# Manejadores de errores globales
# ------------------------------------------------------------------


@app.exception_handler(Exception)
async def global_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Captura cualquier excepción no controlada y devuelve un JSON limpio."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Error interno del servidor.",
            "error": str(exc),
        },
    )


# ------------------------------------------------------------------
# Health check
# ------------------------------------------------------------------


@app.get("/health", tags=["Sistema"], summary="Verificar estado del servicio")
async def health() -> dict:
    """Retorna un indicador simple de que el servicio está activo."""
    return {"status": "ok"}
