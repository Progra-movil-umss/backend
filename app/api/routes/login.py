from fastapi import APIRouter, Depends, HTTPException, status
from app.models import UserLogin, FirebaseToken, UserRegister
from app.core.deps import get_auth_service, get_current_user
from app.core.messages import APIMessages
from app.core.firebase_auth import FirebaseAuthService
import firebase_admin
from firebase_admin import auth
from app.core.user_service import UserService
from app.core.db import get_db
from sqlalchemy.orm import Session

router = APIRouter(tags=["auth"])
firebase_service = FirebaseAuthService()

@router.post("/login", response_model=FirebaseToken)
async def login(
    user_data: UserLogin,
    auth_service: FirebaseAuthService = Depends(get_auth_service)
):
    """
    Endpoint para autenticar usuarios con email y contraseña.
    
    Este endpoint autentica al usuario directamente con Firebase y devuelve
    un token de ID que puede usarse para autenticar peticiones.
    """
    try:
        # Autenticar al usuario y obtener el token
        token = await auth_service.authenticate_user(user_data.email, user_data.password)
        return token
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al autenticar usuario: {str(e)}"
        )

@router.post("/register")
async def register(
    user: UserRegister, 
    db: Session = Depends(get_db),
    auth_service: FirebaseAuthService = Depends(get_auth_service)
):
    user_service = UserService(db, auth_service)
    return await user_service.create_user(user)

@router.delete("/delete-user")
async def delete_user(
    db: Session = Depends(get_db),
    auth_service: FirebaseAuthService = Depends(get_auth_service),
    current_user = Depends(get_current_user)
):
    """Elimina un usuario completamente de Firebase y la base de datos."""
    try:
        # Obtener el ID del usuario actual (sub es el firebase_uid en el token)
        user_id = current_user.sub
            
        # Eliminar usuario de Firebase y la base de datos
        user_service = UserService(db, auth_service)
        await user_service.delete_user(user_id)
        
        return {"message": "Usuario eliminado exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
