from fastapi import APIRouter
from app.services.KPIService import (
    getTiempoEsperaPromedio,
    getTasaAusentismo,
    getTasaOcupacionMedica,
    getNivelSatisfaccion,
    getTiempoCicloAdmision,
    getAllKPIs
)

router = APIRouter(prefix="/kpis", tags=["KPIs"])

@router.get("/tiempo-espera-promedio")
def tiempo_espera_promedio():
    return getTiempoEsperaPromedio()

@router.get("/tasa-ausentismo")
def tasa_ausentismo():
    return getTasaAusentismo()

@router.get("/tasa-ocupacion-medica")
def tasa_ocupacion_medica():
    return getTasaOcupacionMedica()

@router.get("/nivel-satisfaccion")
def nivel_satisfaccion():
    return getNivelSatisfaccion()

@router.get("/tiempo-ciclo-admision")
def tiempo_ciclo_admision():
    return getTiempoCicloAdmision()

@router.get("/all")
def all_kpis():
    return getAllKPIs()

