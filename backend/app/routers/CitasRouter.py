from datetime import date
from typing import List

from fastapi import APIRouter, HTTPException, status

from app.schemas.Citas import CitaCreada, CitaCrear
from app.services.CitasService import (
    buscarCitaReservadaPorCodigo,
    cancelarCita,
    getCitasReservadas,
    getCitasReservadasPorEspecialidad,
    getHistorialCitasPorEspecialidad,
    getResumenCitasTopico,
    reservarCita,
)

router = APIRouter(prefix="/citas", tags=["Citas"])


@router.post("/reservar", response_model=CitaCrear)
def reservar(data: CitaCrear):
    citaReservada = reservarCita(data)

    if citaReservada:
        return {
            "estudianteId": data.estudianteId,
            "medicoId": data.medicoId,
            "especialidadId": data.especialidadId,
            "fecha": data.fecha,
            "hora": data.hora.strftime("%H:%M"),
            "estado": data.estado,
        }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales invalidas",
    )


@router.get("/citas_reservadas/{estudianteId}", response_model=List[CitaCreada])
def mostrarCitas(estudianteId: int):
    data = getCitasReservadas(estudianteId)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay citas reservadas",
        )

    return data


@router.delete("/cancelar_cita/{citaId}", response_model=dict)
async def eliminarCita(citaId: int):
    try:
        return cancelarCita(citaId)
    except HTTPException as e:
        raise e


@router.get("/historial/{estudianteId}")
def historialCitasPorEspecialidad(estudianteId: int):
    data = getHistorialCitasPorEspecialidad(estudianteId)
    return data if data else []


@router.get("/topico/especialidad/{especialidadId}")
def citasReservadasParaTopico(especialidadId: int, fecha: date | None = None):
    return getCitasReservadasPorEspecialidad(especialidadId, fecha)


@router.get("/topico/resumen")
def resumenCitasParaTopico(fecha: date | None = None):
    return getResumenCitasTopico(fecha)


@router.get("/topico/buscar")
def buscarCitaParaTopico(codigo: str, fecha: date | None = None):
    return buscarCitaReservadaPorCodigo(codigo, fecha)
