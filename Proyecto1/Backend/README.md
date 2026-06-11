# Backend de CreditGuard

Este proyecto provee la API para el entrenamiento y predicción de riesgo crediticio usando FastAPI.

## Estructura
- `app/main.py`: Punto de entrada de la aplicación.
- `app/api/endpoints.py`: Rutas de la API.
- `app/core/`: Lógica de procesamiento de datos y modelos.
- `app/schemas/`: Modelos de datos para validación (Pydantic).
- `app/storage/`: Archivos locales persistentes (CSV y modelos).

## Cómo ejecutar
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
