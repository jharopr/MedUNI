from pydantic import BaseModel
from datetime import date, time

class CitaCrear(BaseModel):
    estudianteId: int
    medicoId: int
    especialidadId: int
    fecha: date
    hora: time
    estado: str # e.g., "reservada", "cancelada", "atendida", "no_asistio"

class CitaCreada(BaseModel):
    citaId: int
    estudianteId: int
    medicoNombre: str
    especialidadNombre: str
    fecha: date
    hora: time
    estado: str
