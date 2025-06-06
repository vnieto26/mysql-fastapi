from sqlmodel import create_engine, SQLModel, Session
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de la base de datos
db_username = os.getenv("USER_DB")
db_password = os.getenv("PASSWORD_DB")
db_host = os.getenv("HOST_DB")
db_port = os.getenv("PORT_DB")
db_name = os.getenv("NAME_DB")

DATABASE_URL = f"mysql+pymysql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"

# Crear el motor de la base de datos
engine = create_engine(DATABASE_URL, echo=True)

# Dependencia para obtener la sesión de la base de datos
def get_db():
    with Session(engine) as session:
        yield session

# Crear tablas al iniciar la aplicación
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
