from sqlmodel import Session, select
from fastapi import HTTPException, status
from app.models import User, UserRegister, UserUpdate, UserPublic
from .firebase_auth import FirebaseAuthService
from .email_service import EmailService
from .messages import APIMessages
import re

class UserService:
    def __init__(self, db_session: Session, auth_service: FirebaseAuthService):
        self.db_session = db_session
        self.auth_service = auth_service
        self.email_service = EmailService()

    async def create_user(self, user_data: UserRegister) -> UserPublic:
        try:
            existing_user = self.db_session.exec(
                select(User).where(User.email == user_data.email)
            ).first()
            
            if existing_user:
                try:
                    await self.delete_user(existing_user.firebase_uid)
                except Exception as e:
                    print(f"Error al eliminar usuario existente: {str(e)}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Ya existe un usuario con el email {user_data.email}. Por favor, use otro email o contacte al administrador."
                    )
            
            firebase_user = await self.auth_service.create_user(user_data)
            
            user = User(
                email=user_data.email,
                firebase_uid=firebase_user["firebase_uid"],
                full_name=user_data.full_name
            )
            self.db_session.add(user)
            self.db_session.commit()
            self.db_session.refresh(user)
            
            try:
                await self.email_service.send_new_account_email(
                    to_email=user_data.email,
                    username=user_data.email,
                    password=user_data.password
                )
            except Exception as e:
                print(f"Error al enviar email de bienvenida: {str(e)}")
            
            return UserPublic.from_orm(user)
        except Exception as e:
            self.db_session.rollback()
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    async def delete_user(self, firebase_uid: str) -> None:
        try:
            await self.auth_service.delete_user(firebase_uid)
            
            user = await self.get_current_user(firebase_uid)
            self.db_session.delete(user)
            self.db_session.commit()
            
            return None
        except Exception as e:
            self.db_session.rollback()
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al eliminar usuario: {str(e)}"
            )

    async def get_current_user(self, firebase_uid: str) -> User:
        query = select(User).where(User.firebase_uid == firebase_uid)
        user = self.db_session.exec(query).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=APIMessages.USER_NOT_FOUND
            )
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

    async def delete_user_from_db(self, firebase_uid: str, db: Session) -> None:
        try:
            user = db.exec(
                select(User).where(User.firebase_uid == firebase_uid)
            ).first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado en la base de datos"
                )
            
            db.delete(user)
            db.commit()
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al eliminar usuario de la base de datos: {str(e)}"
            )