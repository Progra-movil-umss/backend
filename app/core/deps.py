# app/core/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from .db import get_db
from .firebase_auth import FirebaseAuthService
from .user_service import UserService
from app.models import TokenPayload, FirebaseInfo

# Esquema OAuth2 para tokens de Firebase
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # Ajusta según tu endpoint de login

# Dependencia para obtener el servicio de autenticación
def get_auth_service():
    return FirebaseAuthService()

# Dependencia para obtener el servicio de usuarios
def get_user_service(db: Session = Depends(get_db), auth_service: FirebaseAuthService = Depends(get_auth_service)):
    return UserService(db, auth_service)

# Dependencia para obtener el usuario actual autenticado
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: FirebaseAuthService = Depends(get_auth_service)
) -> TokenPayload:
    try:
        firebase_info = await auth_service.verify_token(token)
        return TokenPayload(sub=firebase_info.firebase_uid, email=firebase_info.email)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")