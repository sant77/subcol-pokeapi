# 📘 Subcol Pokémon Counter API 

API que determina cuál es el mejor Pokémon para enfrentar a un rival usando lógica de tipos (PokeAPI) y arquitectura hexagonal.
Incluye CI/CD con GitHub Actions y despliegue automático a un servidor Contabo usando Docker Compose.

## 🧱 Arquitectura del Proyecto

Este proyecto sigue una arquitectura hexagonal (Ports & Adapters):

```bash
    app/
    ├── domain/                → Lógica de negocio pura
    │   └── pokemon_service.py
    │
    ├── application/           → Orquestación, casos de uso
    │   └── best_counter_usecase.py
    │
    ├── infrastructure/        → Conexiones externas
    │   ├── pokeapi_repository.py
    │   ├── logger_config.py
    │   └── api/
    │       └──pokemon_controller.py
    │         
    │
    └── main.py                → Entrada de FastAPI

```

## ⚙️ Instalación y Ejecución Local

```bash
git clone https://github.com/sant77/subcol-pokeapi.git
cd subcol-pokeapi
```

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```
```bash
pip install -r requirements.txt
```
```bash
uvicorn main:app --reload --port 8000
```

## 🐳Docker Compose en Producción 

En tu servidor o en local:

```bash
docker compose up -d
```

## 🔄 CI/CD — GitHub Actions

Este proyecto cuenta con un pipeline completo:

Construye la imagen Docker

La sube a Docker Hub:
sant77/subcol-pokeapi:latest

Se conecta al servidor Contabo mediante SSH (con contraseña)

Ejecuta:

- docker-compose pull

- docker-compose down

- docker-compose up -d

- Limpia imágenes antiguas

## 🎯 Roadmap

 Agregar caché Redis para acelerar respuestas

 Hacer tests unitarios del dominio

 Agregar versionado de imágenes Docker

 Agregar métricas Prometheus

## ❤️ Contribuciones

Pull requests y mejoras son bienvenidas.

## 📄 Licencia

MIT License.