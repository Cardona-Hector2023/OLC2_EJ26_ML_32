from fastapi import APIRouter, UploadFile, File, HTTPException
import io
import pandas as pd
from app.core import data_processor

router = APIRouter() # Nos ayuda a poder enrutar las rutas.

# Esta es la ruta para cargar el csv ------------------------------------------------------------------------------------------------------------------
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
        
        # Pasar el dataframe a nuestra capa core para guardarlo
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




# CARDONA puedes empezar a programar aquí ----------------------------------------------------------------------------------
# Los próximos endpoints (limpieza, entrenamiento, predicción) irán aquí abajo...
