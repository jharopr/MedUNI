from fastapi import APIRouter, HTTPException, status
from app.schemas.Usuario import UserLogin, AuthenticatedUser
from app.services.UserService import (
    getAdministrador,
    getPersonalTopico,
    getUsuario,
    loginAdministrador,
    loginPersonalTopico,
    loginUsuario,
)
import secrets, time

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(data: UserLogin):
    role = data.role or "estudiante"
    
    if role == "administrador":
        ok = loginAdministrador(data.username, data.password)
        if ok:
            admin_data = getAdministrador(data.username)
            fake_token = secrets.token_hex(16) + ":" + str(int(time.time()))
            return {
                "message": "✅ Login exitoso",
                "user": data.username,
                "token": fake_token,
                "role": "administrador",
                "userData": admin_data
            }
    elif role == "topico":
        ok = loginPersonalTopico(data.username, data.password)
        if ok:
            topico_data = getPersonalTopico(data.username)
            fake_token = secrets.token_hex(16) + ":" + str(int(time.time()))
            return {
                "message": "Login exitoso",
                "user": data.username,
                "token": fake_token,
                "role": "topico",
                "userData": topico_data
            }
    else:
        ok = loginUsuario(data.username, data.password)
        if ok:
            fake_token = secrets.token_hex(16) + ":" + str(int(time.time()))
            return {
                "message": "✅ Login exitoso",
                "user": data.username,
                "token": fake_token,
                "role": "estudiante"
            }
    
    raise HTTPException(status_code=401, detail="Credenciales inválidas")


#INTEGRAR
@router.get("/me", response_model = AuthenticatedUser)
def me(username: str, role: str = "estudiante"):
    if role == "administrador":
        user_data = getAdministrador(username)
    elif role == "topico":
        user_data = getPersonalTopico(username)
    else:
        user_data = getUsuario(username)
    
    if user_data:
        return {
            "id": user_data["id"],
            "nombres": user_data["nombres"],
            "apellidos": user_data["apellidos"],
            "correo": user_data["correo"],
            "codEstudiante": user_data.get("codEstudiante"),
            "username": user_data.get("username"),
            "role": user_data.get("role", role)
        }
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="❌ Credenciales inválidas"
    )
