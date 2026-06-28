from fastapi import APIRouter, HTTPException, status, Query
from app.schemas.Calificaciones import CalificacionCrear, CalificacionRespuesta
from app.services.CalificacionService import (
    crearCalificacion,
    obtenerCalificacionPorCita,
    obtenerCalificacionesPorEstudiante
)
from typing import Optional

router = APIRouter(prefix="/calificaciones", tags=["Calificaciones"])

@router.post("/", response_model=CalificacionRespuesta, status_code=status.HTTP_201_CREATED)
def crear_calificacion(
    calificacion: CalificacionCrear,
    estudiante_id: int = Query(..., description="ID del estudiante que realiza la calificación")
):
    """
    Crea una nueva calificación para una cita atendida.
    Solo se puede calificar una cita que:
    - Pertenezca al estudiante
    - Tenga hora_atencion registrada (ya fue atendida)
    - No tenga calificación previa
    """
    try:
        return crearCalificacion(calificacion, estudiante_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear calificación: {str(e)}"
        )

@router.get("/cita/{cita_id}", response_model=Optional[CalificacionRespuesta])
def obtener_calificacion_cita(cita_id: int):
    """
    Obtiene la calificación de una cita específica.
    Retorna None si la cita no tiene calificación.
    """
    try:
        calificacion = obtenerCalificacionPorCita(cita_id)
        if calificacion is None:
            return None
        return calificacion
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener calificación: {str(e)}"
        )

@router.get("/estudiante/{estudiante_id}", response_model=list[CalificacionRespuesta])
def obtener_calificaciones_estudiante(estudiante_id: int):
    """
    Obtiene todas las calificaciones realizadas por un estudiante.
    """
    try:
        return obtenerCalificacionesPorEstudiante(estudiante_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener calificaciones: {str(e)}"
        )

