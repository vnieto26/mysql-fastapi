import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, Query
from typing import Annotated
from sqlmodel import Field, Session, create_engine, select, SQLModel, table

load_dotenv()
db_username = os.getenv("USER_DB")
db_password = os.getenv("PASSWORD_DB")
db_host = os.getenv("HOST_DB")
db_port = os.getenv("PORT_DB")
db_name = os.getenv("NAME_DB")
DATABASE_URL = f"mysql+pymysql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"
engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

session_dep = Annotated[Session, Depends(get_session)]

# Modelo
class HeroBase(SQLModel):
    name: str=Field(index=True)
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

# API rutas
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

## Creacion de heroes
@app.post("/heroes/", response_model=HeroPublic)
def create_hero(hero: HeroCreate, session: session_dep):
    db_hero = Hero.model_validate(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero

## Listado de heroes
@app.get("/heroes/", response_model=list[HeroPublic])
def read_heroes(session: session_dep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100):
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes

## Busqueda de heroes
@app.get("/heroes/{hero_id}", response_model=HeroPublic)
def read_hero(hero_id: int, session: session_dep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Heroe no encontrado")
    return hero

## Actualizacion de heroes
@app.patch("/heroes/{hero_id}", response_model=HeroPublic)
def update_hero(hero_id: int, hero: HeroUpdate, session: session_dep):
    db_hero = session.get(Hero, hero_id)
    if not db_hero:
        raise HTTPException(status_code=404, detail="Heroe no encontrado")
    hero_data = hero.model_dump(exclude_unset=True)
    db_hero.sqlmodel_update(hero_data)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero

## Eliminacion de heroes
@app.delete("/heroes/{hero_id}")
def delete_hero(hero_id: int, session: session_dep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Heroe no encontrado")
    session.delete(hero)
    session.commit()
    return {"message": "Heroe eliminado"}
