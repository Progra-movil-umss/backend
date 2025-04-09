# app/api/routes/users.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.models import UserRegister, UserUpdate, UserPublic, FirebaseToken, Message
from app.core.deps import get_user_service
from app.core.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # Ajusta según tu endpoint de login

@router.post("/", response_model=UserPublic)
async def create_user(user_data: UserRegister, user_service: UserService = Depends(get_user_service)):
    return await user_service.create_user(user_data)

@router.get("/me", response_model=UserPublic)
async def read_users_me(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
):
    firebase_info = await user_service.auth_service.verify_token(token)
    user = await user_service.get_current_user(firebase_info.firebase_uid)
    return UserPublic.from_orm(user)

@router.put("/me", response_model=UserPublic)
async def update_user_me(
    user_update: UserUpdate,
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
):
    firebase_info = await user_service.auth_service.verify_token(token)
    return await user_service.update_user(firebase_info.firebase_uid, user_update)

@router.post("/reset-password", response_model=Message)
async def reset_password(
    reset_data: FirebaseToken,
    user_service: UserService = Depends(get_user_service)
):
    firebase_info = await user_service.auth_service.verify_token(reset_data.token)
    await user_service.auth_service.send_password_reset_email(firebase_info.email)
    return Message(message="Correo de restablecimiento enviado")