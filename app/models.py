import uuid
from pydantic import EmailStr, validator
from sqlmodel import Field, SQLModel
from typing import Optional, List

class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    full_name: Optional[str] = Field(default=None, max_length=255)
    firebase_uid: str = Field(unique=True, index=True)

class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: Optional[str] = Field(default=None, max_length=255)

    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("La contraseña debe contener al menos una letra mayúscula")
        if not any(c.islower() for c in v):
            raise ValueError("La contraseña debe contener al menos una letra minúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("La contraseña debe contener al menos un número")
        if not any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?/" for c in v):
            raise ValueError("La contraseña debe contener al menos un carácter especial")
        return v

class UserUpdate(SQLModel):
    full_name: Optional[str] = Field(default=None, max_length=255)
    email: Optional[EmailStr] = Field(default=None, max_length=255)

class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)

    @validator('new_password')
    def validate_new_password(cls, v, values):
        if 'current_password' in values and v == values['current_password']:
            raise ValueError("La nueva contraseña debe ser diferente a la actual")
        if not any(c.isupper() for c in v):
            raise ValueError("La contraseña debe contener al menos una letra mayúscula")
        if not any(c.islower() for c in v):
            raise ValueError("La contraseña debe contener al menos una letra minúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("La contraseña debe contener al menos un número")
        if not any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?/" for c in v):
            raise ValueError("La contraseña debe contener al menos un carácter especial")
        return v

class ResetPassword(SQLModel):
    email: EmailStr = Field(max_length=255)

class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)

    @validator('new_password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("La contraseña debe contener al menos una letra mayúscula")
        if not any(c.islower() for c in v):
            raise ValueError("La contraseña debe contener al menos una letra minúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("La contraseña debe contener al menos un número")
        if not any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?/" for c in v):
            raise ValueError("La contraseña debe contener al menos un carácter especial")
        return v

class User(UserBase, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

class UserPublic(SQLModel):
    id: uuid.UUID
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool

class UsersPublic(SQLModel):
    data: List[UserPublic]
    count: int

class Message(SQLModel):
    message: str

class FirebaseInfo(SQLModel):
    firebase_uid: str
    email: EmailStr

class FirebaseToken(SQLModel):
    token: str
    """
    Token de ID de Firebase obtenido al autenticar al usuario.
    Este token debe incluirse en el header Authorization para peticiones autenticadas.
    """

class TokenPayload(SQLModel):
    sub: str
    email: EmailStr

class UserLogin(SQLModel):
    email: EmailStr
    password: str