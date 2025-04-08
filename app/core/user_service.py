# app/core/user_service.py
from sqlmodel import Session, select
from fastapi import HTTPException, status
from app.models import User, UserRegister, UserUpdate, UserPublic
from .firebase_auth import FirebaseAuthService

class UserService:
    def __init__(self, db_session: Session, auth_service: FirebaseAuthService):
        self.db_session = db_session
        self.auth_service = auth_service

    async def create_user(self, user_data: UserRegister) -> UserPublic:
        try:
            firebase_user = await self.auth_service.create_user(user_data)
            user = User(
                email=user_data.email,
                firebase_uid=firebase_user["firebase_uid"],
                full_name=user_data.full_name
            )
            self.db_session.add(user)
            self.db_session.commit()
            self.db_session.refresh(user)
            return UserPublic.from_orm(user)
        except Exception as e:
            self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al crear usuario: {str(e)}"
            )

    async def get_current_user(self, firebase_uid: str) -> User:
        query = select(User).where(User.firebase_uid == firebase_uid)
        user = self.db_session.exec(query).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return user

    async def update_user(self, firebase_uid: str, user_update: UserUpdate) -> UserPublic:
        user = await self.get_current_user(firebase_uid)
        if user_update.email and user_update.email != user.email:
            await self.auth_service.update_user_email(firebase_uid, user_update.email)
            user.email = user_update.email
        if user_update.full_name is not None:
            user.full_name = user_update.full_name
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)
        return UserPublic.from_orm(user)