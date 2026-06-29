from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RegistroAtencionCrear(BaseModel):
    cita_id: int
    observacion: Optional[str] = None


class RegistroAtencionActualizar(BaseModel):
    hora_llegada: Optional[datetime] = None
    hora_triaje: Optional[datetime] = None
    hora_inicio: Optional[datetime] = None
    hora_fin: Optional[datetime] = None
    estado_atencion: Optional[str] = Field(
        None,
        pattern="^(en_espera|en_triaje|en_atencion|finalizada|no_asistio)$",
    )
    observacion: Optional[str] = None


class RegistroAtencionRespuesta(BaseModel):
    id: int
    cita_id: int
    hora_llegada: Optional[datetime]
    hora_triaje: Optional[datetime]
    hora_inicio: Optional[datetime]
    hora_fin: Optional[datetime]
    estado_atencion: str
    observacion: Optional[str]
    created_at: datetime
    updated_at: datetime
