from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from sqlmodel import SQLModel, Field

# Modelo base para usuario
class UserBase(SQLModel):
    username: str = Field(index=True, unique=True, max_length=50)
    email: EmailStr = Field(unique=True, index=True)
    full_name: Optional[str] = None
    disabled: bool = False

# Modelo para crear usuario (hereda de UserBase)
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)

# Modelo para actualizar usuario
class UserUpdate(SQLModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

# Modelo de base de datos para usuario
class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Modelo para respuesta de API (sin contraseña)
class UserPublic(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

# Modelo para autenticación
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
