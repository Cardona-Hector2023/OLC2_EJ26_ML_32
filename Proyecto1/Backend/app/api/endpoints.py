from fastapi.middleware import asyncexitstack
from fastapi import APIRouter, UploadFile, File, HTTPException
import io
import pandas as pd
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
@router.post("/limpieza")
async def limpiar_datos_api():
    return 0 # podes borrar esto xd
    #Demás código...

@router.post("/entrenamiento")
async def entrenar_modelo_api():
    return 0 # podes borrar esto xd
    #Demás código...

@router.post("/reentrenamiento")  #Esto es para lo de Hiperparametros para reentrenar el modelo, por eso lo llame así
async def ajustar_hiperparametros_api():
    return 0 # podes borrar esto xd
    #Demás código...






#ESTO LO HACE PABLO (OSEA YO XD)---------------------------------------------------------------------------------------------------
@router.get("/metricas")
async def metricas_modelo_api():
    return 0 

@router.post("/prediccion-individual")
async def predecir_riesgo_individual_api():
    return 0  
#----------------------------------------------------------------------------------------------------------------------------------
