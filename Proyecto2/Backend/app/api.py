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
    EvaluacionRespuesta,
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

# Rutas para los DataFrames segmentados persistidos en disco.
# Esto permite recuperar el estado después de un reinicio del servidor
# sin necesidad de volver a entrenar (Problema 3 — severidad Alta).
RUTA_DF_FREELANCERS = os.path.join(MODELS_STORAGE_DIR, "freelancers_segmentado.pkl")
RUTA_DF_RESENAS = os.path.join(MODELS_STORAGE_DIR, "resenas_segmentado.pkl")

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


def _persistir_df_segmentado(df: pd.DataFrame, dataset: str) -> None:
    """
    Guarda el DataFrame segmentado en disco para sobrevivir reinicios del
    servidor (Problema 3 — severidad Alta).
    """
    ruta = RUTA_DF_FREELANCERS if dataset == "freelancers" else RUTA_DF_RESENAS
    try:
        df.to_pickle(ruta)
    except Exception as e:
        # No bloqueamos el flujo de entrenamiento si falla la persistencia,
        # pero sí lo registramos para que sea visible en los logs.
        import warnings
        warnings.warn(f"No se pudo persistir el DataFrame segmentado en '{ruta}': {e}")


def _recuperar_df_segmentado(dataset: str) -> pd.DataFrame | None:
    """
    Intenta recuperar el DataFrame segmentado desde disco cuando
    global_state está vacío (p. ej. tras un reinicio del servidor).
    Devuelve None si el archivo no existe.
    """
    ruta = RUTA_DF_FREELANCERS if dataset == "freelancers" else RUTA_DF_RESENAS
    if not os.path.exists(ruta):
        return None
    try:
        return pd.read_pickle(ruta)
    except Exception:
        return None


def _formatear_resumen_freelancers(df_segmentado: pd.DataFrame) -> dict:
    # reset_index para garantizar un RangeIndex 0..n antes de cualquier
    # operación posicional; los labels se extraen después del reset para
    # que la alineación label[i] → df.iloc[i] sea siempre explícita y
    # correcta (Problema 4 — alineación de índices frágil).
    df_segmentado = df_segmentado.reset_index(drop=True)
    labels = df_segmentado["segmento"].to_numpy()
    df_limpio = df_segmentado.drop(columns=["segmento"])

    artefactos = _cargar_artefactos_modelo("freelancers")
    scaler = artefactos["scaler"]
    X_escalado = scaler.transform(df_limpio[COLUMNAS_NUMERICAS])

    # Si el PCA fue persistido junto con el modelo durante el entrenamiento,
    # usamos .transform() sin re-ajustar (Problema 1 — PCA re-fit en cada GET).
    # Si no existe (modelos entrenados antes de esta mejora), caemos al
    # comportamiento anterior con fit_transform para mantener compatibilidad.
    pca = artefactos.get("pca")
    scatter = cl.reducir_dimensiones_numerico(X_escalado, labels, pca=pca)

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
    # Mismo patrón que freelancers: reset primero, labels después, para
    # garantizar alineación posicional explícita (Problema 4).
    df_segmentado = df_segmentado.reset_index(drop=True)
    labels = df_segmentado["segmento"].to_numpy()
    df_entrenamiento = df_segmentado.drop(columns=["segmento"])

    artefactos = _cargar_artefactos_modelo("resenas")
    vectorizador = artefactos["vectorizador"]

    textos_limpios = df_entrenamiento["texto_reseña"].astype(str).apply(cl.limpiar_texto)
    matriz = vectorizador.transform(textos_limpios)

    # Igual que con PCA: si el SVD fue persistido, lo reutilizamos sin
    # re-ajustar. Si no existe, reducir_dimensiones_texto hace fit_transform
    # internamente como antes (Problema 1 — SVD re-fit en cada GET).
    svd = artefactos.get("svd")
    scatter = cl.reducir_dimensiones_texto(matriz, labels, svd=svd)

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
                "id": str(df_entrenamiento.iloc[i]["reseña_id"]),
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
        # Recuperación desde disco si global_state se perdió por reinicio
        # del servidor (Problema 3 — severidad Alta).
        if global_state.df_freelancers_segmentado is None:
            global_state.df_freelancers_segmentado = _recuperar_df_segmentado("freelancers")
        if global_state.df_freelancers_segmentado is None:
            raise HTTPException(
                status_code=400,
                detail="No hay segmentos de freelancers disponibles. "
                       "Entrena el modelo primero.",
            )
        return _formatear_resumen_freelancers(global_state.df_freelancers_segmentado)

    # dataset == "resenas"
    if global_state.df_resenas_segmentado is None:
        global_state.df_resenas_segmentado = _recuperar_df_segmentado("resenas")
    if global_state.df_resenas_segmentado is None:
        raise HTTPException(
            status_code=400,
            detail="No hay segmentos de reseñas disponibles. "
                   "Entrena el modelo primero.",
        )
    return _formatear_resumen_resenas(global_state.df_resenas_segmentado)


@router.get("/segmentos/tabla-cruzada", tags=["Segmentos"])
async def obtener_tabla_cruzada():
    """Calcula la tabla cruzada entre segmentos de freelancers y reseñas."""
    # Intentamos recuperar desde disco si el servidor se reinició
    # (Problema 3 — aplica también a este endpoint).
    if global_state.df_freelancers_segmentado is None:
        global_state.df_freelancers_segmentado = _recuperar_df_segmentado("freelancers")
    if global_state.df_resenas_segmentado is None:
        global_state.df_resenas_segmentado = _recuperar_df_segmentado("resenas")

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


@router.get("/evaluacion", response_model=EvaluacionRespuesta, tags=["Evaluación"])
async def obtener_evaluacion(dataset: str):
    """Devuelve las métricas de evaluación del modelo ya entrenado."""
    if dataset not in {"freelancers", "resenas"}:
        raise HTTPException(status_code=400, detail="Dataset no válido.")

    if dataset == "freelancers":
        if global_state.df_freelancers_segmentado is None:
            global_state.df_freelancers_segmentado = _recuperar_df_segmentado("freelancers")
        df_segmentado = global_state.df_freelancers_segmentado
    else:
        if global_state.df_resenas_segmentado is None:
            global_state.df_resenas_segmentado = _recuperar_df_segmentado("resenas")
        df_segmentado = global_state.df_resenas_segmentado

    if df_segmentado is None:
        raise HTTPException(
            status_code=400,
            detail=f"No hay modelo entrenado para {dataset}. Entrena el modelo primero.",
        )
    
    df_segmentado = df_segmentado.reset_index(drop=True)
    labels = df_segmentado["segmento"].to_numpy()
    
    artefactos = _cargar_artefactos_modelo(dataset)
    if dataset == "freelancers":
        df_limpio = df_segmentado.drop(columns=["segmento"])
        scaler = artefactos["scaler"]
        X_eval = scaler.transform(df_limpio[COLUMNAS_NUMERICAS])
    else:
        df_entrenamiento = df_segmentado.drop(columns=["segmento"])
        vectorizador = artefactos["vectorizador"]
        textos_limpios = df_entrenamiento["texto_reseña"].astype(str).apply(cl.limpiar_texto)
        X_eval = vectorizador.transform(textos_limpios)
    
    metricas = ev.evaluar_modelo(X_eval, labels)
    interpretacion = ev.interpretar_metricas(metricas)
    curva = ev.calcular_curva_codo(X_eval, k_min=K_MIN_CODO, k_max=K_MAX_CODO)
    
    return EvaluacionRespuesta(
        dataset=dataset,
        silhouette=metricas["silhouette_score"],
        daviesBouldin=metricas["davies_bouldin_index"],
        calinskiHarabasz=metricas["calinski_harabasz_index"],
        interpretacion=interpretacion,
        curva=curva
    )


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

        # reducir_dimensiones_numerico devuelve también el PCA ajustado para
        # que podamos persistirlo y evitar re-fit en cada GET /segmentos
        # (Problema 1 — severidad Media). Ver nota en clustering.py.
        dispersion, pca_ajustado = cl.reducir_dimensiones_numerico(
            X_escalado, labels, retornar_reductor=True
        )
        perfiles = cl.perfilar_clusters_numerico(df_limpio, COLUMNAS_NUMERICAS, labels)

        os.makedirs(MODELS_STORAGE_DIR, exist_ok=True)
        # Persistimos scaler, modelo Y pca para evitar re-fit en GET /segmentos.
        cl.guardar_modelo_numerico(
            scaler, resultado_km["modelo"], RUTA_MODELO_FREELANCERS, pca=pca_ajustado
        )

        # Guardamos también el DataFrame con la columna de segmento asignado,
        # para que la Vista 3 (tabla cruzada) y la Vista 6 (exportación)
        # puedan usarlo sin volver a entrenar.
        df_segmentado = df_limpio.copy()
        df_segmentado["segmento"] = labels
        global_state.df_freelancers_segmentado = df_segmentado

        # Persistencia en disco para sobrevivir reinicios (Problema 3).
        _persistir_df_segmentado(df_segmentado, "freelancers")

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

        # Igual que con PCA: pedimos el SVD ajustado para persistirlo
        # (Problema 1 — severidad Media). Ver nota en clustering.py.
        dispersion, svd_ajustado = cl.reducir_dimensiones_texto(
            matriz, labels, retornar_reductor=True
        )
        perfiles = cl.perfilar_clusters_texto(matriz, vectorizador, labels)

        os.makedirs(MODELS_STORAGE_DIR, exist_ok=True)
        # Persistimos vectorizador, modelo Y svd para evitar re-fit en GET /segmentos.
        cl.guardar_modelo_texto(
            vectorizador, resultado_km["modelo"], RUTA_MODELO_RESENAS, svd=svd_ajustado
        )

        # Igual que con freelancers: guardamos el subset entrenado con su
        # columna de segmento, para la tabla cruzada y la exportación.
        df_segmentado = df_entrenamiento.copy()
        df_segmentado["segmento"] = labels
        global_state.df_resenas_segmentado = df_segmentado

        # Persistencia en disco para sobrevivir reinicios (Problema 3).
        _persistir_df_segmentado(df_segmentado, "resenas")

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