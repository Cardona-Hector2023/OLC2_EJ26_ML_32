from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
import io

# Creamos el enrutador principal que contendrá todos nuestros endpoints
router = APIRouter()

def process_csv_preview(file: UploadFile) -> dict:
    """
    Función auxiliar genérica para leer un CSV subido por el usuario,
    validarlo y devolver la estructura de vista previa (CsvPreview) que espera el frontend.
    """
    # 1. Validación básica de extensión
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="El archivo debe tener extensión .csv")
    
    try:
        # Leemos el contenido del archivo a la memoria
        content = file.file.read()
        
        # 2. Tolerancia de codificación:
        # Intentamos leer con utf-8. Si el CSV viene de Excel en Windows,
        # puede tener caracteres especiales (tildes, ñ) que causan un error,
        # en ese caso usamos latin1.
        try:
            df = pd.read_csv(io.BytesIO(content), encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(io.BytesIO(content), encoding='latin1')
            
        # 3. Vista previa:
        # Tomamos solo las primeras 5 filas para enviarlas al frontend.
        # Enviar todo el dataset podría congelar la interfaz web.
        preview_df = df.head(5)
        
        # 4. Formateamos la respuesta para que coincida con la interfaz CsvPreview de Typescript
        preview_data = {
            "columns": df.columns.tolist(),
            "rows": preview_df.to_dict(orient="records"),
            "totalRows": len(df)
        }
        
        # TODO (Próximo paso): Guardar el DataFrame completo (df) en el estado global (state.py)
        # para que esté disponible cuando el usuario haga clic en "Limpiar Datos".
        
        return preview_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el CSV: {str(e)}")


@router.post("/datos/cargar/freelancers", tags=["Carga de Datos"])
async def upload_freelancers(file: UploadFile = File(...)):
    """
    Endpoint para recibir el archivo CSV de perfiles de freelancers.
    """
    return process_csv_preview(file)


@router.post("/datos/cargar/resenas", tags=["Carga de Datos"])
async def upload_resenas(file: UploadFile = File(...)):
    """
    Endpoint para recibir el archivo CSV de reseñas de clientes.
    """
    return process_csv_preview(file)
