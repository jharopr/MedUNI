from pydantic import BaseModel, Field
from typing import Optional

class CalificacionCrear(BaseModel):
    cita_id: int = Field(..., description="ID de la cita a calificar")
    calificacion: int = Field(..., ge=1, le=5, description="Calificación del 1 al 5")
    comentario: Optional[str] = Field(None, max_length=500, description="Comentario opcional sobre la atención")

class CalificacionRespuesta(BaseModel):
    id: int
    cita_id: int
    calificacion: int
    comentario: Optional[str]
    created_at: str

