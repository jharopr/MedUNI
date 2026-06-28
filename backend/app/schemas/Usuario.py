from pydantic import BaseModel
from typing import Optional

class UserLogin(BaseModel):
    username: str
    password: str
    role: Optional[str] = "estudiante"  # "estudiante" o "administrador"

class AuthenticatedUser(BaseModel):
    id: int 
    nombres: str
    apellidos: str
    correo: str
    codEstudiante: Optional[str] = None
    username: Optional[str] = None
    role: str
