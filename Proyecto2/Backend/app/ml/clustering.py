"""
Módulo de clustering para TalentMosaic.

Implementa dos pipelines independientes, siguiendo el flujo visto en los
notebooks de clase (Clase de KMeans/escalado/PCA y Clase de vectorización
de texto/TruncatedSVD/perfilado):

  1. Pipeline NUMÉRICO (freelancers.csv):
     StandardScaler -> KMeans -> PCA(2D) -> perfilado por groupby().mean()
     -> nombre corto por z-scores.

  2. Pipeline DE TEXTO (reseñas_clientes.csv):
     limpieza de texto -> CountVectorizer/TfidfVectorizer -> KMeans
     -> TruncatedSVD(2D) -> términos top por peso promedio en el cluster
     -> nombre corto por palabras dominantes.

Todas las funciones de salida devuelven estructuras simples (dict, list de
dict) ya serializables a JSON, pensadas para ser devueltas directo desde
endpoints de FastAPI sin transformación adicional.

Persistencia: cada pipeline guarda con joblib un único diccionario que
empaqueta el modelo KMeans junto con el transformador correspondiente
(StandardScaler para el pipeline numérico, el vectorizador para el de
texto), de forma que la Vista 5 (Clasificación de Nuevo Registro) pueda
aplicar `.transform()` con el mismo objeto ya ajustado antes de llamar a
`.predict()`.

Nota de responsabilidades: las métricas internas de validación
(Silhouette, Davies-Bouldin, Calinski-Harabasz) y la curva del método del
codo viven en evaluation.py, no en este módulo. Este archivo se limita a
entrenar e interpretar (perfilar, nombrar segmentos); evaluation.py se
limita a medir qué tan buena es la separación obtenida.
"""

import re

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.preprocessing import StandardScaler

SEED = 42

# Stopwords en español definidas a mano, siguiendo el mismo criterio usado
# en clase: scikit-learn no incluye una lista de stopwords en español por
# defecto (stop_words solo acepta 'english', una lista propia, o None).
STOPWORDS_ES = [
    "el", "la", "los", "las", "de", "del", "y", "en", "es", "un", "una",
    "unos", "unas", "que", "se", "con", "por", "para", "muy", "mas", "su",
    "sus", "lo", "al", "tiene", "tienen", "hay", "ha", "han", "esta",
    "este", "estas", "estos", "como", "pero", "tambien", "son", "ser",
    "fue", "le", "les", "o", "u", "e", "ni", "sin", "sobre", "ya", "cada",
    "entre", "hacia", "desde", "me", "mi", "te", "tu", "nos", "tan",
]


# =============================================================================
# PIPELINE DE TEXTO (reseñas_clientes.csv)
# =============================================================================


def limpiar_texto(texto: str) -> str:
    """
    Normaliza un texto antes de vectorizarlo: minúsculas, solo letras y
    espacios (se quita puntuación y dígitos), espacios colapsados.
    """
    texto = texto.lower()
    texto = re.sub(r"[^a-záéíóúñ\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def configurar_vectorizador(metodo: str, max_features: int = 1000):
    """
    Instancia un vectorizador de texto según el método elegido.

    Parameters
    ----------
    metodo : str
        "TF-IDF" o "Bag of Words".
    max_features : int
        Tamaño máximo del vocabulario a conservar.

    Returns
    -------
    Un CountVectorizer o TfidfVectorizer sin ajustar, listo para
    fit_transform.
    """
    metodo_normalizado = metodo.strip().lower()

    if metodo_normalizado in ("tf-idf", "tfidf"):
        return TfidfVectorizer(stop_words=STOPWORDS_ES, max_features=max_features)
    elif metodo_normalizado in ("bag of words", "bow", "bag-of-words"):
        return CountVectorizer(stop_words=STOPWORDS_ES, max_features=max_features)
    else:
        raise ValueError(
            f"Método de vectorización no reconocido: '{metodo}'. "
            "Use 'TF-IDF' o 'Bag of Words'."
        )


def vectorizar_textos(textos: pd.Series, metodo: str, max_features: int = 1000):
    """
    Limpia y vectoriza una serie de textos.

    Parameters
    ----------
    textos : pd.Series
        Textos ya filtrados (sin nulos). Ver
        nlp.obtener_textos_para_entrenamiento() para obtener este subset
        a partir del DataFrame de reseñas limpio.
    metodo : str
        "TF-IDF" o "Bag of Words".

    Returns
    -------
    tuple(matriz_dispersa, vectorizador_ajustado)
    """
    textos_limpios = textos.astype(str).apply(limpiar_texto)
    vectorizador = configurar_vectorizador(metodo, max_features=max_features)
    matriz = vectorizador.fit_transform(textos_limpios)
    return matriz, vectorizador


def entrenar_kmeans(X_vectorizado, n_clusters: int) -> dict:
    """
    Entrena KMeans sobre una matriz ya preparada (vectorizada o escalada,
    según el pipeline).

    Returns
    -------
    dict con:
        modelo     : el KMeans ya ajustado.
        labels     : np.ndarray con la etiqueta de cluster de cada fila.
        inercia    : float, modelo.inertia_.
    """
    modelo = KMeans(n_clusters=n_clusters, n_init=10, random_state=SEED)
    labels = modelo.fit_predict(X_vectorizado)
    return {
        "modelo": modelo,
        "labels": labels,
        "inercia": float(modelo.inertia_),
    }



def reducir_dimensiones_texto(
    X_vectorizado,
    labels,
    svd=None,
    retornar_reductor: bool = False,
):
    """
    Reduce la matriz dispersa de texto a 2D con TruncatedSVD (no PCA, ya
    que PCA no opera de forma eficiente sobre matrices dispersas como las
    que produce un vectorizador de texto).

    Parameters
    ----------
    X_vectorizado : matriz dispersa
        Salida del vectorizador ajustado.
    labels : array-like
        Etiquetas de cluster por documento.
    svd : TruncatedSVD | None
        Si se pasa un SVD ya ajustado (recuperado del .pkl), se usa
        directamente con .transform() sin re-ajustar. Si es None se crea
        uno nuevo y se ajusta con fit_transform (comportamiento original).
    retornar_reductor : bool
        Si True, devuelve una tupla (scatter, svd_ajustado) en lugar de
        solo scatter, para que el entrenamiento pueda persistir el SVD.

    Returns
    -------
    list[dict] con la forma [{"x": ..., "y": ..., "cluster": ...}, ...],
    o tuple(list[dict], TruncatedSVD) si retornar_reductor=True.
    """
    if svd is not None:
        # SVD ya ajustado: solo proyectamos, sin re-fit (Problema 1 — Media).
        coordenadas = svd.transform(X_vectorizado)
    else:
        svd = TruncatedSVD(n_components=2, random_state=SEED)
        coordenadas = svd.fit_transform(X_vectorizado)

    scatter = [
        {"x": float(coordenadas[i, 0]), "y": float(coordenadas[i, 1]), "cluster": int(labels[i])}
        for i in range(len(labels))
    ]
    return (scatter, svd) if retornar_reductor else scatter


def obtener_terminos_top(matriz_vectorizada, vectorizador, labels, n_terminos: int = 6) -> dict:
    """
    Para cada cluster, calcula el peso promedio de cada término ENTRE LOS
    DOCUMENTOS ASIGNADOS A ESE CLUSTER (no el centroide de KMeans), y
    devuelve los n_terminos con mayor peso promedio.

    Returns
    -------
    dict {cluster_id: [{"termino": str, "peso": float}, ...]}
    """
    vocabulario = vectorizador.get_feature_names_out()
    resultado = {}

    for cluster_id in sorted(set(labels)):
        filas_cluster = matriz_vectorizada[labels == cluster_id]
        peso_promedio = np.asarray(filas_cluster.mean(axis=0)).ravel()
        indices_top = peso_promedio.argsort()[::-1][:n_terminos]
        resultado[int(cluster_id)] = [
            {"termino": str(vocabulario[i]), "peso": float(peso_promedio[i])}
            for i in indices_top
        ]

    return resultado


def generar_nombres_cortos_texto(terminos_por_cluster: dict, n_terminos: int = 2) -> dict:
    """
    Genera un nombre corto por cluster de texto, tomando las n_terminos
    palabras de mayor peso y uniéndolas con " / ", siguiendo el mismo
    formato usado en clase (nombre_corto_texto).

    Parameters
    ----------
    terminos_por_cluster : dict
        Salida de obtener_terminos_top().

    Returns
    -------
    dict {cluster_id: "Palabra1 / Palabra2"}
    """
    nombres = {}
    for cluster_id, terminos in terminos_por_cluster.items():
        palabras = [t["termino"] for t in terminos[:n_terminos]]
        nombres[cluster_id] = " / ".join(p.capitalize() for p in palabras)
    return nombres


def perfilar_clusters_texto(
    matriz_vectorizada, vectorizador, labels, n_terminos_top: int = 6, n_terminos_nombre: int = 2
) -> dict:
    """
    Componente de interpretación del pipeline de texto: combina
    obtener_terminos_top() y generar_nombres_cortos_texto() en una sola
    respuesta lista para el frontend.

    Returns
    -------
    dict {cluster_id: {"nombre_corto": str, "terminos_top": [...], "cantidad_registros": int}}
    """
    terminos_por_cluster = obtener_terminos_top(
        matriz_vectorizada, vectorizador, labels, n_terminos=n_terminos_top
    )
    nombres_cortos = generar_nombres_cortos_texto(
        terminos_por_cluster, n_terminos=n_terminos_nombre
    )

    perfil = {}
    for cluster_id, terminos in terminos_por_cluster.items():
        cantidad = int(np.sum(labels == cluster_id))
        perfil[cluster_id] = {
            "nombre_corto": nombres_cortos[cluster_id],
            "terminos_top": terminos,
            "cantidad_registros": cantidad,
        }
    return perfil


def guardar_modelo_texto(vectorizador, modelo_kmeans, ruta: str, svd=None) -> None:
    """
    Empaqueta y guarda con joblib el vectorizador ajustado junto con el
    modelo KMeans, para que la Vista 5 pueda recuperarlos sin reentrenar.

    Parameters
    ----------
    svd : TruncatedSVD | None
        Si se pasa, se incluye en el paquete para que GET /segmentos pueda
        reutilizarlo con .transform() sin re-ajustar (Problema 1 — Media).
    """
    try:
        artefacto = {"vectorizador": vectorizador, "modelo": modelo_kmeans}
        if svd is not None:
            artefacto["svd"] = svd
        joblib.dump(artefacto, ruta)
    except Exception as e:
        raise RuntimeError(f"No se pudo guardar el modelo de texto en '{ruta}': {e}")


def predecir_nuevo_comentario(nuevo_texto: str, ruta_modelo: str) -> int:
    """
    Carga el vectorizador y el modelo KMeans guardados, transforma el
    texto nuevo con el MISMO vectorizador ya ajustado (nunca uno nuevo) y
    devuelve el cluster asignado.
    """
    try:
        artefactos = joblib.load(ruta_modelo)
    except Exception as e:
        raise RuntimeError(f"No se pudo cargar el modelo desde '{ruta_modelo}': {e}")

    vectorizador = artefactos["vectorizador"]
    modelo = artefactos["modelo"]

    texto_limpio = limpiar_texto(str(nuevo_texto))
    X_nuevo = vectorizador.transform([texto_limpio])
    cluster_asignado = modelo.predict(X_nuevo)[0]
    return int(cluster_asignado)


# =============================================================================
# PIPELINE NUMÉRICO (freelancers.csv)
# =============================================================================


def escalar_numericas(df: pd.DataFrame, columnas: list[str]):
    """
    Ajusta un StandardScaler sobre las columnas numéricas indicadas.

    Returns
    -------
    tuple(X_escalado, scaler_ajustado)
    """
    scaler = StandardScaler()
    X_escalado = scaler.fit_transform(df[columnas])
    return X_escalado, scaler


def reducir_dimensiones_numerico(
    X_escalado,
    labels,
    pca=None,
    retornar_reductor: bool = False,
):
    """
    Reduce las variables numéricas escaladas a 2D con PCA (no
    TruncatedSVD, ya que aquí la matriz es densa, no dispersa).

    Parameters
    ----------
    X_escalado : np.ndarray
        Salida del StandardScaler.
    labels : array-like
        Etiquetas de cluster por registro.
    pca : PCA | None
        Si se pasa un PCA ya ajustado (recuperado del .pkl), se usa
        directamente con .transform() sin re-ajustar. Si es None se crea
        uno nuevo y se ajusta con fit_transform (comportamiento original).
    retornar_reductor : bool
        Si True, devuelve una tupla (scatter, pca_ajustado) en lugar de
        solo scatter, para que el entrenamiento pueda persistir el PCA.

    Returns
    -------
    list[dict] con la forma [{"x": ..., "y": ..., "cluster": ...}, ...],
    o tuple(list[dict], PCA) si retornar_reductor=True.
    """
    if pca is not None:
        # PCA ya ajustado: solo proyectamos, sin re-fit (Problema 1 — Media).
        coordenadas = pca.transform(X_escalado)
    else:
        pca = PCA(n_components=2, random_state=SEED)
        coordenadas = pca.fit_transform(X_escalado)

    scatter = [
        {"x": float(coordenadas[i, 0]), "y": float(coordenadas[i, 1]), "cluster": int(labels[i])}
        for i in range(len(labels))
    ]
    return (scatter, pca) if retornar_reductor else scatter


def generar_nombre_corto_numerico(
    df: pd.DataFrame,
    columnas: list[str],
    labels,
    n_terminos: int = 2,
    umbral_z_minimo: float = 0.3,
) -> dict:
    """
    Genera un nombre corto por cluster a partir de qué tan lejos está el
    promedio de cada variable, dentro del cluster, respecto al promedio
    global (medido en desviaciones estándar / z-score).

    Si ningún z-score del cluster supera umbral_z_minimo, se asigna un
    nombre de respaldo ("Perfil mixto") en vez de forzar una etiqueta
    sobre un cluster sin rasgos claramente distintivos.

    Returns
    -------
    dict {cluster_id: "Alto ingresos totales / Bajo tiempo respuesta horas"}
    """
    promedio_global = df[columnas].mean()
    desviacion_global = df[columnas].std()
    # Alineación posicional explícita: convertimos labels a array numpy puro
    # para que el label[i] siempre caiga en df.index[i], incluso si el df
    # llegara con un índice no contiguo (Problema 4 — Baja).
    labels_array = labels.values if hasattr(labels, "values") else labels
    labels_serie = pd.Series(labels_array, index=df.index)

    nombres = {}
    for cluster_id in sorted(set(labels)):
        promedio_cluster = df.loc[labels_serie == cluster_id, columnas].mean()
        z_scores = (promedio_cluster - promedio_global) / desviacion_global
        top = z_scores.abs().sort_values(ascending=False).head(n_terminos)

        if top.iloc[0] < umbral_z_minimo:
            nombres[int(cluster_id)] = "Perfil mixto"
            continue

        partes = []
        for col in top.index:
            direccion = "Alto" if z_scores[col] > 0 else "Bajo"
            partes.append(f"{direccion} {col.replace('_', ' ')}")
        nombres[int(cluster_id)] = " / ".join(partes)

    return nombres


def perfilar_clusters_numerico(
    df: pd.DataFrame,
    columnas: list[str],
    labels,
    n_terminos_nombre: int = 2,
) -> dict:
    """
    Componente de interpretación del pipeline numérico: promedios de cada
    variable original por cluster, cantidad de registros, y nombre corto
    automático.

    Returns
    -------
    dict {cluster_id: {"nombre_corto": str, "promedios": {...}, "cantidad_registros": int}}
    """
    # Misma alineación posicional explícita que en generar_nombre_corto_numerico
    # (Problema 4 — Baja).
    labels_array = labels.values if hasattr(labels, "values") else labels
    labels_serie = pd.Series(labels_array, index=df.index)
    nombres_cortos = generar_nombre_corto_numerico(
        df, columnas, labels, n_terminos=n_terminos_nombre
    )

    perfil = {}
    for cluster_id in sorted(set(labels)):
        subset = df.loc[labels_serie == cluster_id, columnas]
        promedios = {col: float(subset[col].mean()) for col in columnas}
        perfil[int(cluster_id)] = {
            "nombre_corto": nombres_cortos[int(cluster_id)],
            "promedios": promedios,
            "cantidad_registros": int(len(subset)),
        }
    return perfil


def guardar_modelo_numerico(scaler, modelo_kmeans, ruta: str, pca=None) -> None:
    """
    Empaqueta y guarda con joblib el StandardScaler ajustado junto con el
    modelo KMeans, para que la Vista 5 pueda recuperarlos sin reentrenar.

    Parameters
    ----------
    pca : PCA | None
        Si se pasa, se incluye en el paquete para que GET /segmentos pueda
        reutilizarlo con .transform() sin re-ajustar (Problema 1 — Media).
    """
    try:
        artefacto = {"scaler": scaler, "modelo": modelo_kmeans}
        if pca is not None:
            artefacto["pca"] = pca
        joblib.dump(artefacto, ruta)
    except Exception as e:
        raise RuntimeError(f"No se pudo guardar el modelo numérico en '{ruta}': {e}")


def predecir_nuevo_freelancer(valores: dict, columnas: list[str], ruta_modelo: str) -> int:
    """
    Carga el StandardScaler y el modelo KMeans guardados, transforma un
    registro nuevo (dict con las mismas columnas usadas al entrenar) con
    el MISMO scaler ya ajustado, y devuelve el cluster asignado.

    Parameters
    ----------
    valores : dict
        Un valor numérico por cada columna en `columnas`.
    columnas : list[str]
        Mismo orden de columnas usado al entrenar (ver escalar_numericas).
    """
    try:
        artefactos = joblib.load(ruta_modelo)
    except Exception as e:
        raise RuntimeError(f"No se pudo cargar el modelo desde '{ruta_modelo}': {e}")

    scaler = artefactos["scaler"]
    modelo = artefactos["modelo"]

    fila = pd.DataFrame([{col: valores[col] for col in columnas}])
    X_nuevo = scaler.transform(fila[columnas])
    cluster_asignado = modelo.predict(X_nuevo)[0]
    return int(cluster_asignado)