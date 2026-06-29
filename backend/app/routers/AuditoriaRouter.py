from datetime import date
from typing import Optional

from fastapi import APIRouter, Query

from app.services.AuditoriaService import listarAuditoria

router = APIRouter(prefix="/auditoria", tags=["Auditoria"])


@router.get("/historial")
def historial_auditoria(
    rol: Optional[str] = Query(None),
    accion: Optional[str] = Query(None),
    fecha_desde: Optional[date] = Query(None),
    fecha_hasta: Optional[date] = Query(None),
    limit: int = Query(100, ge=1, le=300),
):
    return listarAuditoria(
        rol=rol,
        accion=accion,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        limit=limit,
    )
