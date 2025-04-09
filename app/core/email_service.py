import os
from pathlib import Path
from fastapi import HTTPException, status
from app.core.config import settings
from app.core.messages import APIMessages
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
import asyncio
from functools import partial

class EmailService:
    def __init__(self):
        self.emails_enabled = settings.emails_enabled
        if not self.emails_enabled:
            print("⚠️ Emails no están configurados. Los emails no se enviarán.")
            return

        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_tls = settings.SMTP_TLS
        self.smtp_ssl = settings.SMTP_SSL
        self.from_email = settings.EMAILS_FROM_EMAIL
        self.from_name = settings.EMAILS_FROM_NAME
        self.project_name = settings.PROJECT_NAME
        
        template_dir = Path(__file__).parent.parent / "email-templates" / "build"
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))

    async def _send_email(self, to_email: str, subject: str, html_content: str) -> None:
        if not self.emails_enabled:
            print(f"⚠️ Email no enviado (emails deshabilitados): {subject} a {to_email}")
            return

        try:
            msg = MIMEMultipart()
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email
            msg["Subject"] = subject

            msg.attach(MIMEText(html_content, "html"))

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                partial(self._send_email_sync, msg)
            )
            print(f"✅ Email enviado: {subject} a {to_email}")
        except Exception as e:
            print(f"❌ Error al enviar email: {str(e)}")
            pass

    def _send_email_sync(self, msg: MIMEMultipart) -> None:
        if self.smtp_ssl:
            server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
        else:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            if self.smtp_tls:
                server.starttls()
        
        server.login(self.smtp_user, self.smtp_password)
        server.send_message(msg)
        server.quit()

    async def send_new_account_email(self, to_email: str, username: str, password: str) -> None:
        if not self.emails_enabled:
            print(f"⚠️ Email de bienvenida no enviado (emails deshabilitados): {to_email}")
            return
            
        try:
            template = self.env.get_template("new_account.html")
            html_content = template.render(
                project_name=self.project_name,
                username=username,
                password=password,
                link=f"{settings.FRONTEND_HOST}/login"
            )
            
            await self._send_email(
                to_email=to_email,
                subject=f"Bienvenido a {self.project_name} - Tu nueva cuenta",
                html_content=html_content
            )
        except Exception as e:
            print(f"❌ Error al preparar email de bienvenida: {str(e)}")
            pass

    async def send_password_reset_email(self, to_email: str, reset_link: str) -> None:
        """Envía email para restablecer contraseña."""
        if not self.emails_enabled:
            print(f"⚠️ Email de restablecimiento no enviado (emails deshabilitados): {to_email}")
            return
            
        try:
            template = self.env.get_template("reset_password.html")
            html_content = template.render(
                project_name=self.project_name,
                reset_link=reset_link
            )
            
            await self._send_email(
                to_email=to_email,
                subject=f"{self.project_name} - Restablecer contraseña",
                html_content=html_content
            )
        except Exception as e:
            print(f"❌ Error al preparar email de restablecimiento: {str(e)}")
            pass