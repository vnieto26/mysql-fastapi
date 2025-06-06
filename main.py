from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated, List
from datetime import timedelta
from sqlmodel import Session, select

from models import User, UserCreate, UserPublic, UserUpdate
from auth import (
    get_current_active_user,
    create_access_token,
    get_password_hash,
    authenticate_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from database import get_db, create_db_and_tables
from sqlmodel import SQLModel, Field

# Importar modelos de autenticación
from models import Token

# Importar modelos de héroes
class HeroBase(SQLModel):
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)

class Hero(HeroBase, table=True):
    id: int = Field(default=None, primary_key=True)
    secret_name: str

class HeroPublic(HeroBase):
    id: int

class HeroCreate(HeroBase):
    secret_name: str

class HeroUpdate(HeroBase):
    name: str | None = None
    age: int | None = None
    secret_name: str | None = None

# Inicializar la aplicación FastAPI
app = FastAPI(title="API de Héroes con Autenticación")

# Evento de inicio para crear tablas
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Rutas de autenticación
@app.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Rutas de usuarios
@app.post("/users/", response_model=UserPublic)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.exec(select(User).where(User.username == user.username)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        disabled=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/me/", response_model=UserPublic)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

# Rutas de héroes (protegidas)
@app.post("/heroes/", response_model=HeroPublic)
def create_hero(
    hero: HeroCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_hero = Hero.model_validate(hero)
    db.add(db_hero)
    db.commit()
    db.refresh(db_hero)
    return db_hero

@app.get("/heroes/", response_model=List[HeroPublic])
def read_heroes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    heroes = db.exec(select(Hero).offset(skip).limit(limit)).all()
    return heroes

@app.get("/heroes/{hero_id}", response_model=HeroPublic)
def read_hero(
    hero_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    hero = db.get(Hero, hero_id)
    if hero is None:
        raise HTTPException(status_code=404, detail="Héroe no encontrado")
    return hero

@app.patch("/heroes/{hero_id}", response_model=HeroPublic)
def update_hero(
    hero_id: int,
    hero: HeroUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_hero = db.get(Hero, hero_id)
    if db_hero is None:
        raise HTTPException(status_code=404, detail="Héroe no encontrado")
    
    hero_data = hero.dict(exclude_unset=True)
    for key, value in hero_data.items():
        setattr(db_hero, key, value)
    
    db.add(db_hero)
    db.commit()
    db.refresh(db_hero)
    return db_hero

@app.delete("/heroes/{hero_id}")
def delete_hero(
    hero_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    hero = db.get(Hero, hero_id)
    if hero is None:
        raise HTTPException(status_code=404, detail="Héroe no encontrado")
    db.delete(hero)
    db.commit()
    return {"message": "Héroe eliminado correctamente"}
