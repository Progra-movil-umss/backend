# app/core/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from .db import get_db
from .firebase_auth import FirebaseAuthService
from .user_service import UserService
from app.models import TokenPayload, FirebaseInfo

security = HTTPBearer(
    scheme_name="BearerAuth",
    description="Token de autenticación de Firebase",
    auto_error=True
)

# Dependencia para obtener el servicio de autenticación
def get_auth_service():
    return FirebaseAuthService()

def get_user_service(db: Session = Depends(get_db), auth_service: FirebaseAuthService = Depends(get_auth_service)):
    return UserService(db, auth_service)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: FirebaseAuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service)
) -> TokenPayload:
    try:
        firebase_info = await auth_service.verify_token(credentials.credentials)
        
        await user_service.get_current_user(firebase_info.firebase_uid)
            
        return TokenPayload(
            sub=firebase_info.firebase_uid,
            email=firebase_info.email
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido: {str(e)}"
        )