# app/core/firebase_auth.py
import firebase_admin
from firebase_admin import auth, credentials
from fastapi import HTTPException, status
from app.core.config import settings
from app.models import UserRegister, FirebaseInfo

class FirebaseAuthService:
    def __init__(self):
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        if not firebase_admin._apps:  # Evitar inicialización múltiple
            firebase_admin.initialize_app(cred)

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
                detail=f"Token inválido: {str(e)}"
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
                detail="El correo ya está registrado"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al crear usuario: {str(e)}"
            )

    async def send_password_reset_email(self, email: str) -> None:
        try:
            link = auth.generate_password_reset_link(email)
            # Enviar correo usando SMTP
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
            pass  # Silenciar si el usuario no existe
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al enviar correo: {str(e)}"
            )