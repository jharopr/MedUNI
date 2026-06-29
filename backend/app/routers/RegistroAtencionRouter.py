from fastapi import APIRouter, Query, status

from app.schemas.RegistroAtencion import (
    RegistroAtencionActualizar,
    RegistroAtencionCrear,
    RegistroAtencionRespuesta,
)
from app.services.RegistroAtencionService import (
    actualizarRegistroAtencion,
    obtenerRegistroAtencion,
    registrarLlegada,
)

router = APIRouter(prefix="/registro-atencion", tags=["Registro Atencion"])


@router.post("/llegada", response_model=RegistroAtencionRespuesta, status_code=status.HTTP_201_CREATED)
def crear_llegada(
    data: RegistroAtencionCrear,
    usuario_id: int | None = Query(None),
    rol: str = Query("administrador"),
):
    return registrarLlegada(data, usuario_id, rol)


@router.patch("/{cita_id}", response_model=RegistroAtencionRespuesta)
def actualizar_registro(
    cita_id: int,
    data: RegistroAtencionActualizar,
    usuario_id: int | None = Query(None),
    rol: str = Query("administrador"),
):
    return actualizarRegistroAtencion(cita_id, data, usuario_id, rol)


@router.get("/{cita_id}", response_model=RegistroAtencionRespuesta | None)
def obtener_registro(cita_id: int):
    return obtenerRegistroAtencion(cita_id)
