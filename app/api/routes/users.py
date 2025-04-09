# app/api/routes/users.py
from fastapi import APIRouter, Depends, HTTPException
from app.models import UserRegister, UserUpdate, UserPublic, FirebaseToken, Message
from app.core.deps import get_user_service, get_current_user
from app.core.user_service import UserService
from app.models import TokenPayload

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserPublic)
async def create_user(user_data: UserRegister, user_service: UserService = Depends(get_user_service)):
    return await user_service.create_user(user_data)

@router.get("/me", response_model=UserPublic)
async def read_users_me(
    current_user: TokenPayload = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    user = await user_service.get_current_user(current_user.sub)
    return UserPublic.from_orm(user)

@router.put("/me", response_model=UserPublic)
async def update_user_me(
    user_update: UserUpdate,
    current_user: TokenPayload = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    return await user_service.update_user(current_user.sub, user_update)

@router.post("/reset-password", response_model=Message)
async def reset_password(
    reset_data: FirebaseToken,
    user_service: UserService = Depends(get_user_service)
):
    firebase_info = await user_service.auth_service.verify_token(reset_data.token)
    await user_service.auth_service.send_password_reset_email(firebase_info.email)
    return Message(message="Correo de restablecimiento enviado")