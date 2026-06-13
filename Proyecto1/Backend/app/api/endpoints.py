from fastapi.middleware import asyncexitstack
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import io
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from app.core import data_processor

router = APIRouter() # Nos ayuda a poder enrutar las rutas.

#Esta es la ruta para cargar el csv ------------------------------------------------------------------------------------------------------------------
@router.post("/carga")
async def cargar_csv(archivo: UploadFile = File(...)): 
    """
    Recibe un archivo CSV desde el frontend y lo carga en memoria.
    """
    if not archivo.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="El archivo debe ser un .csv")
        
    try:
        contents = await archivo.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        #Validar que el CSV contenga las columnas obligatorias del proyecto, asi evitamos errores. 
        columnas_esperadas = [
            "ingresos_mensuales", "deuda_activa", "historial_pagos",
            "antiguedad_laboral", "creditos_activos", "monto_solicitado",
            "atrasos_previos", "dependientes_economicos", "utilizacion_credito",
            "en_riesgo"
        ]

        #Nos ayuda a poder validar que el CSV contenga las columnas obligatorias del proyecto.
        columnas_faltantes = [col for col in columnas_esperadas if col not in df.columns]
        if columnas_faltantes:
            raise HTTPException(
                status_code=400, 
                detail=f"El CSV no tiene el formato correcto. Faltan las siguientes columnas: {', '.join(columnas_faltantes)}"
            )
        
        #Pasar el dataframe a nuestra capa core para guardarlo
        data_processor.set_original_data(df)
        data_processor.save_original_csv(df)

        # depuracion 
        """
        print(f"\n Dimensiones: {df.shape[0]} filas × {df.shape[1]} columnas \n")
        print(df.head()) #primeros 5 filas
        print("")
        print(df.info()) #para detectar columnas con nulos 
        print("")
        print(df.describe()) #informacion estadistica de las columnas numericas
        """

        return {
            "filas": int(df.shape[0]),
            "columnas": int(df.shape[1]),
            "nombre_archivo": archivo.filename,
            "mensaje": "Archivo cargado exitosamente"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo: {str(e)}")





# CARDONA podes empezar a programar aquí ----------------------------------------------------------------------------------
# Los próximos endpoints (limpieza, entrenamiento, predicción) irán aquí abajo...

# ── Limpieza de datos ──────────────────────────────────────────────────────────
@router.post("/limpieza")
async def limpiar_datos_api():
    """
    Ejecuta el pipeline de limpieza sobre los datos cargados y devuelve
    un reporte con los cambios realizados.
    """
    try:
        reporte = data_processor.limpiar_datos()
        return reporte
    except ValueError as e:
        # Sin datos cargados previamente
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la limpieza: {str(e)}")

# ── Entrenamiento ──────────────────────────────────────────────────────────────
@router.post("/entrenamiento")
async def entrenar_modelo_api():
    """
    Entrena el Random Forest con los hiperparámetros por defecto y
    devuelve métricas + detalles del split. Responde con EntrenamientoResult.
    """
    try:
        resultado = data_processor.entrenar_modelo()
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante el entrenamiento: {str(e)}")





# NOTA: Modelo para recibir hiperparámetros, agregado por Pablo para que funcione :D -----------------------------------------------------------------
class HiperparametrosIn(BaseModel):
    n_arboles: int
    profundidad_maxima: int
    hojas_maximas: int

# NOTA: Modelo para recibir los datos de un solicitante individual -----------------------------------------------------------------
class SolicitanteInput(BaseModel):
    ingresos_mensuales: float
    deuda_activa: float
    historial_pagos: float
    antiguedad_laboral: float
    creditos_activos: float
    monto_solicitado: float
    atrasos_previos: float
    dependientes_economicos: float
    utilizacion_credito: float

@router.post("/reentrenamiento")  
async def ajustar_hiperparametros_api(hiperparametros: HiperparametrosIn):
    try:
        resultado = data_processor.entrenar_modelo(hiperparametros.model_dump())
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante el reentrenamiento: {str(e)}")
# ----------------------------------------------------------------------------------------------------------------------------------------------------



#ESTO LO HACE PABLO (OSEA YO XD)---------------------------------------------------------------------------------------------------
@router.get("/metricas")
async def metricas_modelo_api():
    return 0 

@router.post("/prediccion")
async def predecir_riesgo_individual_api(solicitante: SolicitanteInput):
    try:
        resultado = data_processor.predecir_individual(solicitante.model_dump())
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al realizar la predicción: {str(e)}")
#----------------------------------------------------------------------------------------------------------------------------------
