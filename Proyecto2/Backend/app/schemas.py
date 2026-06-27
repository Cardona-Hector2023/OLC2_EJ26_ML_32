"""
Este archivo contiene los Modelos de Pydantic (Data Transfer Objects).
Su propósito es servir de "molde" estricto para los datos que entran
(ej: la configuración al momento de entrenar) y los que salen (JSON de respuesta).

Usar Pydantic nos permite:
1. Validar automáticamente los tipos de datos (si esperamos un int, rechazará un string no numérico).
2. Autogenerar la documentación Swagger en FastAPI.
3. Mantener tipado fuerte en el código Python.
"""


from typing import Optional
 
from pydantic import BaseModel

class ResumenLimpiezaArchivo(BaseModel):
    """
    Resumen de lo que ocurrió al limpiar un único archivo (freelancers o
    reseñas). Se usa para construir el mensaje de resultado que pide el
    enunciado en la Vista 1 ("Registros cargados: 1,250 | Valores nulos
    imputados: 38 | Duplicados eliminados: 14 | Registros corregidos: 9").
    """
 
    registros_originales: int
    registros_finales: int
    duplicados_eliminados: int
    valores_nulos_imputados: int
 
 
class LimpiezaResultado(BaseModel):
    """
    Respuesta del endpoint POST /datos/limpiar.
 
    Cada campo es opcional porque el usuario pudo haber cargado solo uno
    de los dos archivos (freelancers o reseñas) antes de presionar
    "Limpiar Datos".
    """
 
    freelancers: Optional[ResumenLimpiezaArchivo] = None
    resenas: Optional[ResumenLimpiezaArchivo] = None
    mensaje: str
 

# Ejemplo de molde que se creará a futuro:
# class TrainConfig(BaseModel):
#     dataset: str
#     algoritmo: str
#     k: int = 3
