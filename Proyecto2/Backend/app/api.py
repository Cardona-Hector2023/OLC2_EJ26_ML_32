from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
import io
import os
import joblib

from app.ml.preprocessor import limpiar_freelancers, COLUMNAS_NUMERICAS
from app.ml.nlp import agregar_longitud_resena, limpiar_resenas, obtener_textos_para_entrenamiento
from app.ml import clustering as cl
from app.ml import evaluation as ev
from app.schemas import (
    ConfigEntrenamientoFreelancers,
    ConfigEntrenamientoResenas,
    EntrenamientoResultadoFreelancers,
    EntrenamientoResultadoResenas,
    LimpiezaResultado,
    ResumenLimpiezaArchivo,
)
from app.state import global_state

# Creamos el enrutador principal que contendrá todos nuestros endpoints
router = APIRouter()

# Carpeta donde se serializan los modelos entrenados y sus transformadores
# asociados (StandardScaler / vectorizador), para que la Vista 5 pueda
# reutilizarlos sin reentrenar. Coincide con models_storage/ en el árbol
# de carpetas del backend.
MODELS_STORAGE_DIR = "models_storage"
RUTA_MODELO_FREELANCERS = os.path.join(MODELS_STORAGE_DIR, "freelancers_kmeans.pkl")
RUTA_MODELO_RESENAS = os.path.join(MODELS_STORAGE_DIR, "resenas_kmeans.pkl")

# Rango de k explorado para la curva del método del codo. Se calcula
# siempre sobre este mismo rango, independientemente del k elegido por el
# usuario para el modelo final.
K_MIN_CODO = 2
K_MAX_CODO = 10


def _cargar_artefactos_modelo(dataset: str) -> dict:
    """Carga el artefacto persistido del dataset solicitado."""
    ruta = (
        RUTA_MODELO_FREELANCERS if dataset == "freelancers" else RUTA_MODELO_RESENAS
    )

    if not os.path.exists(ruta):
        raise HTTPException(
            status_code=400,
            detail="No existe un modelo entrenado para ese dataset.",
        )

    try:
        return joblib.load(ruta)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"No se pudo cargar el modelo desde '{ruta}': {e}",
        )


def _formatear_resumen_freelancers(df_segmentado: pd.DataFrame) -> dict:
    df_limpio = df_segmentado.drop(columns=["segmento"]).reset_index(drop=True)
    labels = df_segmentado["segmento"].to_numpy()

    artefactos = _cargar_artefactos_modelo("freelancers")
    scaler = artefactos["scaler"]
    X_escalado = scaler.transform(df_limpio[COLUMNAS_NUMERICAS])

    scatter = cl.reducir_dimensiones_numerico(X_escalado, labels)
    perfiles = cl.perfilar_clusters_numerico(df_limpio, COLUMNAS_NUMERICAS, labels)

    resumen = []
    for cluster_id, info in sorted(perfiles.items()):
        resumen.append(
            {
                "segmento": int(cluster_id),
                "registros": int(info["cantidad_registros"]),
                "caracteristicas": info["promedios"],
                "descripcion": info["nombre_corto"],
            }
        )

    scatter_con_id = []
    for i, punto in enumerate(scatter):
        scatter_con_id.append(
            {
                "x": punto["x"],
                "y": punto["y"],
                "segmento": punto["cluster"],
                "id": str(df_limpio.iloc[i]["freelancer_id"]),
            }
        )

    return {
        "dataset": "freelancers",
        "scatter": scatter_con_id,
        "resumen": resumen,
    }


def _formatear_resumen_resenas(df_segmentado: pd.DataFrame) -> dict:
    df_entrenamiento = df_segmentado.drop(columns=["segmento"]).reset_index(drop=True)
    labels = df_segmentado["segmento"].to_numpy()

    artefactos = _cargar_artefactos_modelo("resenas")
    vectorizador = artefactos["vectorizador"]

    textos_limpios = df_entrenamiento["texto_reseña"].astype(str).apply(cl.limpiar_texto)
    matriz = vectorizador.transform(textos_limpios)

    scatter = cl.reducir_dimensiones_texto(matriz, labels)
    perfiles = cl.perfilar_clusters_texto(matriz, vectorizador, labels)

    resumen = []
    for cluster_id, info in sorted(perfiles.items()):
        resumen.append(
            {
                "segmento": int(cluster_id),
                "registros": int(info["cantidad_registros"]),
                "caracteristicas": {
                    f"termino_{i + 1}": termino["termino"]
                    for i, termino in enumerate(info["terminos_top"][:2])
                },
                "descripcion": info["nombre_corto"],
                "terminos": info["terminos_top"],
            }
        )

    scatter_con_id = []
    for i, punto in enumerate(scatter):
        scatter_con_id.append(
            {
                "x": punto["x"],
                "y": punto["y"],
                "segmento": punto["cluster"],
                "id": str(df_entrenamiento.iloc[i]["resena_id"]),
            }
        )

    return {
        "dataset": "resenas",
        "scatter": scatter_con_id,
        "resumen": resumen,
    }


@router.get("/segmentos", tags=["Segmentos"])
async def obtener_segmentos(dataset: str):
    """Devuelve scatter y perfilado del dataset ya entrenado."""
    if dataset not in {"freelancers", "resenas"}:
        raise HTTPException(status_code=400, detail="Dataset no válido.")

    if dataset == "freelancers":
        if global_state.df_freelancers_segmentado is None:
            raise HTTPException(
                status_code=400,
                detail="No hay segmentos de freelancers disponibles.",
            )
        return _formatear_resumen_freelancers(global_state.df_freelancers_segmentado)

    if global_state.df_resenas_segmentado is None:
        raise HTTPException(
            status_code=400,
            detail="No hay segmentos de reseñas disponibles.",
        )
    return _formatear_resumen_resenas(global_state.df_resenas_segmentado)


@router.get("/segmentos/tabla-cruzada", tags=["Segmentos"])
async def obtener_tabla_cruzada():
    """Calcula la tabla cruzada entre segmentos de freelancers y reseñas."""
    if global_state.df_freelancers_segmentado is None or global_state.df_resenas_segmentado is None:
        raise HTTPException(
            status_code=400,
            detail="Debes entrenar ambos modelos para generar la tabla cruzada.",
        )

    freelancers = global_state.df_freelancers_segmentado[["freelancer_id", "segmento"]].drop_duplicates("freelancer_id")
    resenas = global_state.df_resenas_segmentado[["freelancer_id", "segmento"]].copy()

    cruce = resenas.merge(
        freelancers,
        on="freelancer_id",
        how="inner",
        suffixes=("_resena", "_freelancer"),
    )

    if cruce.empty:
        raise HTTPException(
            status_code=400,
            detail="No hay coincidencias entre freelancers y reseñas para cruzar.",
        )

    filas = sorted(freelancers["segmento"].dropna().astype(int).unique().tolist())
    columnas = sorted(resenas["segmento"].dropna().astype(int).unique().tolist())

    tabla = pd.crosstab(cruce["segmento_freelancer"], cruce["segmento_resena"])
    tabla = tabla.reindex(index=filas, columns=columnas, fill_value=0)

    celdas = []
    for fila in filas:
        total_fila = int(tabla.loc[fila].sum())
        fila_celdas = []
        for columna in columnas:
            cantidad = int(tabla.loc[fila, columna])
            porcentaje = round((cantidad / total_fila) * 100, 2) if total_fila else 0
            fila_celdas.append({"cantidad": cantidad, "porcentaje": porcentaje})
        celdas.append(fila_celdas)

    return {
        "filas": filas,
        "columnas": columnas,
        "celdas": celdas,
    }


def process_csv_preview(file: UploadFile) -> tuple[dict, pd.DataFrame]:
    """
    Función auxiliar genérica para leer un CSV subido por el usuario,
    validarlo y devolver tanto la vista previa (para el frontend) como el
    DataFrame completo (para guardarlo en el estado global).
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


@router.post(
    "/entrenar/freelancers",
    response_model=EntrenamientoResultadoFreelancers,
    tags=["Configuración y Entrenamiento"],
)
async def entrenar_freelancers(config: ConfigEntrenamientoFreelancers):
    """
    Entrena KMeans sobre el dataset de freelancers ya limpio (Vista 2).

    Requiere haber ejecutado POST /datos/limpiar previamente: este
    endpoint consume global_state.df_freelancers_limpio, nunca el
    DataFrame crudo.

    En una sola llamada: escala las variables, entrena el modelo con el
    k indicado, calcula métricas de validación, la curva del método del
    codo, la proyección 2D para el scatter plot, el perfil de cada
    segmento con su nombre corto automático, y persiste el modelo en
    disco para que la Vista 5 pueda reutilizarlo.
    """
    df_limpio = global_state.df_freelancers_limpio
    if df_limpio is None:
        raise HTTPException(
            status_code=400,
            detail="No hay datos de freelancers limpios. Carga el CSV y "
                   "ejecuta /datos/limpiar antes de entrenar.",
        )

    try:
        X_escalado, scaler = cl.escalar_numericas(df_limpio, COLUMNAS_NUMERICAS)

        resultado_km = cl.entrenar_kmeans(X_escalado, n_clusters=config.k)
        labels = resultado_km["labels"]

        metricas = ev.evaluar_modelo(X_escalado, labels)
        interpretacion = ev.interpretar_metricas(metricas)
        curva_codo = ev.calcular_curva_codo(X_escalado, k_min=K_MIN_CODO, k_max=K_MAX_CODO)
        dispersion = cl.reducir_dimensiones_numerico(X_escalado, labels)
        perfiles = cl.perfilar_clusters_numerico(df_limpio, COLUMNAS_NUMERICAS, labels)

        os.makedirs(MODELS_STORAGE_DIR, exist_ok=True)
        cl.guardar_modelo_numerico(scaler, resultado_km["modelo"], RUTA_MODELO_FREELANCERS)

        # Guardamos también el DataFrame con la columna de segmento asignado,
        # para que la Vista 3 (tabla cruzada) y la Vista 6 (exportación)
        # puedan usarlo sin volver a entrenar.
        df_segmentado = df_limpio.copy()
        df_segmentado["segmento"] = labels
        global_state.df_freelancers_segmentado = df_segmentado

        resumen_por_segmento = ", ".join(
            f"Segmento {cid}: {info['cantidad_registros']} registros"
            for cid, info in sorted(perfiles.items())
        )

        return EntrenamientoResultadoFreelancers(
            k=config.k,
            inercia=resultado_km["inercia"],
            metricas=metricas,
            interpretacion=interpretacion,
            curva_codo=curva_codo,
            dispersion=dispersion,
            perfiles=perfiles,
            mensaje=f"Modelo entrenado. Segmentos generados: {config.k} ({resumen_por_segmento}).",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error durante el entrenamiento: {str(e)}"
        )


@router.post(
    "/entrenar/resenas",
    response_model=EntrenamientoResultadoResenas,
    tags=["Configuración y Entrenamiento"],
)
async def entrenar_resenas(config: ConfigEntrenamientoResenas):
    """
    Entrena KMeans sobre el dataset de reseñas ya limpio (Vista 2).

    Requiere haber ejecutado POST /datos/limpiar previamente: este
    endpoint consume global_state.df_resenas_limpio, nunca el DataFrame
    crudo.

    Solo las reseñas con texto_reseña no nulo participan del
    entrenamiento (ver nlp.obtener_textos_para_entrenamiento); las que
    tienen texto faltante se mantienen en el dataset general pero no
    reciben un segmento de texto.
    """
    df_limpio = global_state.df_resenas_limpio
    if df_limpio is None:
        raise HTTPException(
            status_code=400,
            detail="No hay datos de reseñas limpios. Carga el CSV y "
                   "ejecuta /datos/limpiar antes de entrenar.",
        )

    try:
        df_entrenamiento = obtener_textos_para_entrenamiento(df_limpio)
        if len(df_entrenamiento) == 0:
            raise HTTPException(
                status_code=400,
                detail="No hay reseñas con texto válido para entrenar el modelo.",
            )

        matriz, vectorizador = cl.vectorizar_textos(
            df_entrenamiento["texto_reseña"], metodo=config.metodo_vectorizacion
        )

        resultado_km = cl.entrenar_kmeans(matriz, n_clusters=config.k)
        labels = resultado_km["labels"]

        metricas = ev.evaluar_modelo(matriz, labels)
        interpretacion = ev.interpretar_metricas(metricas)
        curva_codo = ev.calcular_curva_codo(matriz, k_min=K_MIN_CODO, k_max=K_MAX_CODO)
        dispersion = cl.reducir_dimensiones_texto(matriz, labels)
        perfiles = cl.perfilar_clusters_texto(matriz, vectorizador, labels)

        os.makedirs(MODELS_STORAGE_DIR, exist_ok=True)
        cl.guardar_modelo_texto(vectorizador, resultado_km["modelo"], RUTA_MODELO_RESENAS)

        # Igual que con freelancers: guardamos el subset entrenado con su
        # columna de segmento, para la tabla cruzada y la exportación.
        df_segmentado = df_entrenamiento.copy()
        df_segmentado["segmento"] = labels
        global_state.df_resenas_segmentado = df_segmentado

        resumen_por_segmento = ", ".join(
            f"Segmento {cid}: {info['cantidad_registros']} registros"
            for cid, info in sorted(perfiles.items())
        )

        return EntrenamientoResultadoResenas(
            k=config.k,
            metodo_vectorizacion=config.metodo_vectorizacion,
            inercia=resultado_km["inercia"],
            metricas=metricas,
            interpretacion=interpretacion,
            curva_codo=curva_codo,
            dispersion=dispersion,
            perfiles=perfiles,
            mensaje=f"Modelo entrenado. Segmentos generados: {config.k} ({resumen_por_segmento}).",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error durante el entrenamiento: {str(e)}"
        )