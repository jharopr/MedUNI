from datetime import date

from fastapi import APIRouter, Query

from app.services.DoctorService import finalizarCitaMedico, iniciarCitaMedico, listarCitasMedico

router = APIRouter(prefix="/doctor", tags=["Doctor"])


@router.get("/{medico_id}/citas")
def citas_del_medico(medico_id: int, fecha: date = Query(...)):
    return listarCitasMedico(medico_id, fecha)


@router.post("/{medico_id}/citas/{cita_id}/iniciar")
def iniciar_cita(medico_id: int, cita_id: int):
    return iniciarCitaMedico(cita_id, medico_id)


@router.post("/{medico_id}/citas/{cita_id}/finalizar")
def finalizar_cita(medico_id: int, cita_id: int):
    return finalizarCitaMedico(cita_id, medico_id)
