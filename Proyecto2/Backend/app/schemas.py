"""
Este archivo contiene los Modelos de Pydantic (Data Transfer Objects).
Su propósito es servir de "molde" estricto para los datos que entran
(ej: la configuración al momento de entrenar) y los que salen (JSON de respuesta).

Usar Pydantic nos permite:
1. Validar automáticamente los tipos de datos (si esperamos un int, rechazará un string no numérico).
2. Autogenerar la documentación Swagger en FastAPI.
3. Mantener tipado fuerte en el código Python.
"""

from pydantic import BaseModel

# Ejemplo de molde que se creará a futuro:
# class TrainConfig(BaseModel):
#     dataset: str
#     algoritmo: str
#     k: int = 3
