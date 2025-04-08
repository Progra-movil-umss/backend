from abc import ABC, abstractmethod
from typing import Dict, Any
from app.models import UserRegister, FirebaseInfo

class AuthService(ABC):
    @abstractmethod
    async def verify_token(self, token: str) -> FirebaseInfo:
        pass

    @abstractmethod
    async def create_user(self, user_data: UserRegister) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def update_user_email(self, firebase_uid: str, new_email: str) -> None:
        pass

    @abstractmethod
    async def update_user_password(self, firebase_uid: str, new_password: str) -> None:
        pass

    @abstractmethod
    async def delete_user(self, firebase_uid: str) -> None:
        pass

    @abstractmethod
    async def send_password_reset_email(self, email: str) -> str:
        pass