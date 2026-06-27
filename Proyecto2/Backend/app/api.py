from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
import io
 
from app.ml.preprocessor import limpiar_freelancers
from app.ml.nlp import agregar_longitud_resena, limpiar_resenas
from app.schemas import LimpiezaResultado, ResumenLimpiezaArchivo
from app.state import global_state

# Creamos el enrutador principal que contendrá todos nuestros endpoints
router = APIRouter()

def process_csv_preview(file: UploadFile) -> tuple[dict, pd.DataFrame]:
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
        
        return preview_data, df
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el CSV: {str(e)}")


@router.post("/datos/cargar/freelancers", tags=["Carga de Datos"])
async def upload_freelancers(file: UploadFile = File(...)):
    """
    Endpoint para recibir el archivo CSV de perfiles de freelancers.
    """
    preview_data, df = process_csv_preview(file)
 
    # Guardamos el DataFrame crudo en el estado global para que el
    # endpoint de limpieza pueda recuperarlo más adelante.
    global_state.df_freelancers = df
    # Si ya existía una limpieza previa (de una carga anterior), la
    # invalidamos: el usuario subió un archivo nuevo.
    global_state.df_freelancers_limpio = None
    return preview_data


@router.post("/datos/cargar/resenas", tags=["Carga de Datos"])
async def upload_resenas(file: UploadFile = File(...)):
    """
    Endpoint para recibir el archivo CSV de reseñas de clientes.
    """

    preview_data, df = process_csv_preview(file)
 
    # longitud_reseña debe calcularse a partir del texto original, antes
    # de cualquier limpieza, así que se agrega aquí mismo al guardar el
    # crudo en el estado (si el archivo no la trae incluida).
    if "longitud_reseña" not in df.columns:
        df = agregar_longitud_resena(df)
        # Reflejamos la columna nueva también en la vista previa, para que
        # el usuario la vea desde la tabla de carga.
        preview_data["columns"] = df.columns.tolist()
        preview_data["rows"] = df.head(5).to_dict(orient="records")
 
    global_state.df_resenas = df
    global_state.df_resenas_limpio = None

    return preview_data

def _resumir_limpieza_freelancers() -> ResumenLimpiezaArchivo:
    """
    Ejecuta limpiar_freelancers() sobre el DataFrame crudo guardado en el
    estado, guarda el resultado limpio, y construye el resumen de la
    operación (duplicados eliminados, nulos imputados, etc.).
    """
    df_crudo = global_state.df_freelancers
    registros_originales = len(df_crudo)
    nulos_antes = int(df_crudo.isna().sum().sum())
 
    df_limpio = limpiar_freelancers(df_crudo)
    global_state.df_freelancers_limpio = df_limpio
 
    duplicados_eliminados = registros_originales - len(df_limpio)
    # Nulos imputados = los que había originalmente, más los que se
    # generaron al limpiar texto sucio y rangos inválidos, menos los
    # nulos que pudieron irse junto con filas duplicadas eliminadas.
    nulos_en_filas_unicas = int(
        df_crudo.drop_duplicates().isna().sum().sum()
    )
    valores_nulos_imputados = nulos_en_filas_unicas
 
    return ResumenLimpiezaArchivo(
        registros_originales=registros_originales,
        registros_finales=len(df_limpio),
        duplicados_eliminados=duplicados_eliminados,
        valores_nulos_imputados=valores_nulos_imputados,
    )


def _resumir_limpieza_resenas() -> ResumenLimpiezaArchivo:
    """
    Ejecuta limpiar_resenas() sobre el DataFrame crudo guardado en el
    estado, guarda el resultado limpio, y construye el resumen de la
    operación.
 
    A diferencia de freelancers, aquí "valores_nulos_imputados" solo
    cuenta categoria_servicio, ya que es la única columna donde el nulo
    se reemplaza por un valor concreto ("Sin categoría"). texto_reseña y
    fecha_reseña se dejan intencionalmente como NaN y no se cuentan aquí.
    """
    df_crudo = global_state.df_resenas
    registros_originales = len(df_crudo)
 
    df_limpio = limpiar_resenas(df_crudo)
    global_state.df_resenas_limpio = df_limpio
 
    duplicados_eliminados = registros_originales - len(df_limpio)
 
    nulos_categoria_antes = int(
        df_crudo.drop_duplicates()["categoria_servicio"].isna().sum()
    )
 
    return ResumenLimpiezaArchivo(
        registros_originales=registros_originales,
        registros_finales=len(df_limpio),
        duplicados_eliminados=duplicados_eliminados,
        valores_nulos_imputados=nulos_categoria_antes,
    )

@router.post("/datos/limpiar", response_model=LimpiezaResultado, tags=["Carga de Datos"])
async def limpiar_datos():
    """
    Endpoint único de limpieza ("Limpiar Datos" en la Vista 1).
 
    Limpia cualquier dataset que esté actualmente cargado en el estado
    global: si solo se cargó freelancers.csv, limpia solo ese; si solo se
    cargó reseñas_clientes.csv, limpia solo ese; si se cargaron ambos,
    limpia los dos y devuelve un resumen de cada uno.
    """
    if not global_state.hay_datos_cargados():
        raise HTTPException(
            status_code=400,
            detail="No hay archivos cargados. Sube freelancers.csv y/o "
                   "reseñas_clientes.csv antes de limpiar.",
        )
 
    try:
        resumen_freelancers = None
        resumen_resenas = None
 
        if global_state.df_freelancers is not None:
            resumen_freelancers = _resumir_limpieza_freelancers()
 
        if global_state.df_resenas is not None:
            resumen_resenas = _resumir_limpieza_resenas()
 
        partes_mensaje = []
        if resumen_freelancers is not None:
            partes_mensaje.append(
                f"freelancers: {resumen_freelancers.registros_finales} "
                f"registros finales"
            )
        if resumen_resenas is not None:
            partes_mensaje.append(
                f"reseñas: {resumen_resenas.registros_finales} registros "
                f"finales"
            )
        mensaje = "Limpieza completada (" + ", ".join(partes_mensaje) + ")."
 
        return LimpiezaResultado(
            freelancers=resumen_freelancers,
            resenas=resumen_resenas,
            mensaje=mensaje,
        )
 
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error durante la limpieza de datos: {str(e)}"
        )