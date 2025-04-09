# app/core/firebase_auth.py
import firebase_admin
from firebase_admin import auth, credentials
from fastapi import HTTPException, status
from app.core.config import settings
from app.models import UserRegister, FirebaseInfo, FirebaseToken, TokenPayload
from app.core.messages import APIMessages
import requests
import json
import base64

class FirebaseAuthService:
    def __init__(self):
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        if not firebase_admin._apps:  # Evitar inicialización múltiple
            firebase_admin.initialize_app(cred)
        self.api_key = settings.FIREBASE_API_KEY
        self.project_id = settings.FIREBASE_PROJECT_ID

    def decode_token(self, token: str) -> dict:

        try:
            return auth.verify_id_token(token, check_revoked=False)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=APIMessages.INVALID_TOKEN
            )

    async def verify_token(self, token: str) -> FirebaseInfo:
        try:
            decoded_token = auth.verify_id_token(token)
            return FirebaseInfo(
                firebase_uid=decoded_token["uid"],
                email=decoded_token["email"]
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=APIMessages.INVALID_TOKEN
            )

    async def create_user(self, user_data: UserRegister) -> dict:
        try:
            firebase_user = auth.create_user(
                email=user_data.email,
                password=user_data.password,
                display_name=user_data.full_name
            )
            return {
                "firebase_uid": firebase_user.uid,
                "email": firebase_user.email,
                "display_name": firebase_user.display_name
            }
        except auth.EmailAlreadyExistsError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=APIMessages.EMAIL_EXISTS
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=APIMessages.USER_CREATE_ERROR
            )

    async def authenticate_user(self, email: str, password: str) -> FirebaseToken:
        try:
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.api_key}"
            data = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            
            response = requests.post(url, json=data)
            
            if response.status_code != 200:
                error_data = response.json()
                if "error" in error_data and error_data["error"]["message"] == "EMAIL_NOT_FOUND":
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=APIMessages.INVALID_CREDENTIALS
                    )
                elif "error" in error_data and error_data["error"]["message"] == "INVALID_PASSWORD":
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=APIMessages.INVALID_CREDENTIALS
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Error de autenticación: {error_data.get('error', {}).get('message', 'Error desconocido')}"
                    )
            
            token_data = response.json()
            return FirebaseToken(token=token_data["idToken"])
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al autenticar usuario: {str(e)}"
            )

    async def send_password_reset_email(self, email: str) -> None:
        try:
            link = auth.generate_password_reset_link(email)
            from email.message import EmailMessage
            import smtplib

            msg = EmailMessage()
            msg.set_content(f"Restablece tu contraseña aquí: {link}")
            msg["Subject"] = "Restablecimiento de Contraseña - Flora Find"
            msg["From"] = settings.EMAILS_FROM_EMAIL
            msg["To"] = email

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                if settings.SMTP_TLS:
                    server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        except auth.UserNotFoundError:
            pass
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=APIMessages.PASSWORD_RESET_ERROR
            )

    async def delete_user(self, firebase_uid: str) -> None:
        try:
            auth.delete_user(firebase_uid)
        except auth.UserNotFoundError:
            pass
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al eliminar usuario de Firebase: {str(e)}"
            )