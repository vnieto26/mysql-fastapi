# MySQL FastAPI

Este proyecto es una API construida con [FastAPI](https://fastapi.tiangolo.com/) y utiliza una base de datos MySQL para el almacenamiento de datos.

## Características

- API RESTful con FastAPI
- Integración con base de datos MySQL
- Estructura modular para autenticación y modelos

## Requisitos

- Python 3.8+
- MySQL

## Instalación

1. Clona el repositorio:
   ```bash
   git clone <URL-del-repositorio>
   cd mysql-fastapi
   ```
2. Crea un entorno virtual e instala las dependencias:
   ```bash
   python -m venv env
   source env/bin/activate  # En Windows: env\Scripts\activate
   pip install -r requirements.txt
   ```
3. Configura la conexión a la base de datos en `database.py` según tus credenciales de MySQL.

## Uso

1. Inicia el servidor de desarrollo:
   ```bash
   uvicorn main:app --reload
   ```
2. Accede a la documentación interactiva en [http://localhost:8000/docs](http://localhost:8000/docs)

## Estructura del proyecto

```
mysql-fastapi/
├── auth.py         # Lógica de autenticación
├── database.py     # Configuración de la base de datos
├── main.py         # Punto de entrada de la aplicación FastAPI
├── models.py       # Definición de modelos de datos
├── requirements.txt# Dependencias del proyecto
└── README.md       # Este archivo
```

## Licencia

[MIT](LICENSE)
