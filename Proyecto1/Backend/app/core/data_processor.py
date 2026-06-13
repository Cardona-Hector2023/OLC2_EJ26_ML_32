import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import os
import pickle

STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage") # Nos ayuda a poder encontrar la carpeta storage donde estara el dataset.

COLUMNAS_FEATURES = [
    "ingresos_mensuales", "deuda_activa", "historial_pagos",
    "antiguedad_laboral", "creditos_activos", "monto_solicitado",
    "atrasos_previos", "dependientes_economicos", "utilizacion_credito"
]
 
# Hiperparámetros por defecto del Random Forest
HIPERPARAMETROS_DEFAULT = {
    "n_arboles":         100,
    "profundidad_maxima": 10,
    "hojas_maximas":      50,
}

# Esta sección es para guardar el dataframe original. desde set_original_data hasta save_clean_csv ---------------------------------------------------------

# Variables en memoria para evitar recargar desde disco continuamente
_original_df = None
_clean_df = None
_scaler = None  # StandardScaler ajustado durante la limpieza, se reutiliza en predicción
_modelo      = None   # RandomForestClassifier entrenado
_metricas    = None   # Métricas del último entrenamiento
_hiperparams = None   # Hiperparámetros usados en el último entrenamiento


# Nos ayuda a poder guardar el dataframe original en memoria.
def set_original_data(df: pd.DataFrame):
    """Guarda el dataframe original en memoria en el directorio storage."""
    global _original_df
    _original_df = df

# Nos ayuda a poder obtener el dataframe original de la memoria.
def get_original_data() -> pd.DataFrame:
    """Devuelve el dataframe original de la memoria."""
    return _original_df

# Nos ayuda a poder guardar un respaldo del CSV original en storage/.
def save_original_csv(df: pd.DataFrame):
    """Guarda un respaldo del CSV original en storage/."""
    os.makedirs(STORAGE_DIR, exist_ok=True)
    filepath = os.path.join(STORAGE_DIR, "dataset_original.csv")
    df.to_csv(filepath, index=False)

# Nos ayuda a poder obtener el dataframe limpio de la memoria.
def get_clean_data() -> pd.DataFrame:
    """Devuelve el dataframe limpio."""
    return _clean_df
# Nos ayuda a poder guardar el dataframe limpio en memoria y en storage/.
def save_clean_csv(df: pd.DataFrame):
    """Guarda un respaldo del CSV limpio y actualiza memoria."""
    global _clean_df
    _clean_df = df
    os.makedirs(STORAGE_DIR, exist_ok=True)
    filepath = os.path.join(STORAGE_DIR, "dataset_clean.csv")
    df.to_csv(filepath, index=False)


def get_scaler() -> StandardScaler:
    """Devuelve el scaler ajustado durante la limpieza."""
    return _scaler
 
def get_modelo() -> RandomForestClassifier:
    """Devuelve el modelo entrenado o None si aún no se ha entrenado."""
    return _modelo
 
def get_metricas() -> dict:
    """Devuelve las métricas del último entrenamiento."""
    return _metricas
 
def get_hiperparametros() -> dict:
    """Devuelve los hiperparámetros usados en el último entrenamiento."""
    return _hiperparams


# CARDONA puedes empezar a programar aquí ----------------------------------------------------------------------------------
# Aquí agregaremos después las funciones puras de limpieza...  Aqui puedes empezar a programar el manejo de tu archivo CSV  -----------------------------

# Ejemplo (podes eliminarlo o dejarlo)
def limpiar_datos() -> dict:
    """
    Ejecuta el pipeline completo de limpieza sobre el dataset original.
 
    Pasos (en orden):
      1. Eliminar duplicados exactos.
      2. Eliminar registros "basura" (todas las columnas de features en cero).
      3. Convertir inconsistencias / valores fuera de rango a NaN.
      4. Imputar valores faltantes (mediana para continuos, moda para discretos).
      5. Escalar features con StandardScaler (excluye en_riesgo).
 
    Returns:
        dict con contadores de cada paso y el mensaje de resumen.
 
    Raises:
        ValueError si no hay datos cargados previamente.
    """
    global _scaler
 
    df = get_original_data()
    if df is None:
        raise ValueError("No hay datos cargados. Primero realiza la carga del CSV.")
 
    df = df.copy()
    reporte = {}
 
    # ── PASO 1: Eliminar duplicados ────────────────────────────────────────────
    n_antes = len(df)
    df = df.drop_duplicates()
    reporte["duplicados_eliminados"] = n_antes - len(df)
 
    # ── PASO 2: Eliminar registros basura (todas las features en 0) ────────────
    # Solo miramos las columnas de features, no la etiqueta en_riesgo
    columnas_features = [
        "ingresos_mensuales", "deuda_activa", "historial_pagos",
        "antiguedad_laboral", "creditos_activos", "monto_solicitado",
        "atrasos_previos", "dependientes_economicos", "utilizacion_credito"
    ]
    mascara_basura = (df[columnas_features] == 0).all(axis=1)
    n_antes = len(df)
    df = df[~mascara_basura]
    reporte["registros_basura_eliminados"] = n_antes - len(df)
 
    # ── PASO 3: Convertir inconsistencias a NaN ────────────────────────────────
    n_inconsistencias = 0
 
    # ingresos_mensuales: negativos o cero → NaN
    mascara = df["ingresos_mensuales"] <= 0
    n_inconsistencias += mascara.sum()
    df.loc[mascara, "ingresos_mensuales"] = np.nan
 
    # monto_solicitado: igual a cero → NaN
    mascara = df["monto_solicitado"] == 0
    n_inconsistencias += mascara.sum()
    df.loc[mascara, "monto_solicitado"] = np.nan
 
    # historial_pagos: fuera de [0, 100] → NaN
    mascara = (df["historial_pagos"] < 0) | (df["historial_pagos"] > 100)
    n_inconsistencias += mascara.sum()
    df.loc[mascara, "historial_pagos"] = np.nan
 
    # utilizacion_credito: fuera de [0, 100] → NaN
    mascara = (df["utilizacion_credito"] < 0) | (df["utilizacion_credito"] > 100)
    n_inconsistencias += mascara.sum()
    df.loc[mascara, "utilizacion_credito"] = np.nan
 
    # antiguedad_laboral: negativa → NaN
    mascara = df["antiguedad_laboral"] < 0
    n_inconsistencias += mascara.sum()
    df.loc[mascara, "antiguedad_laboral"] = np.nan
 
    # deuda_activa: negativa → NaN  (cero es válido: sin deuda)
    mascara = df["deuda_activa"] < 0
    n_inconsistencias += mascara.sum()
    df.loc[mascara, "deuda_activa"] = np.nan
 
    reporte["inconsistencias_convertidas_a_nan"] = int(n_inconsistencias)
 
    # ── PASO 4: Imputar valores faltantes ──────────────────────────────────────
    # Contamos NaN totales ANTES de imputar (incluye los recién convertidos)
    reporte["nulos_imputados"] = int(df[columnas_features].isnull().sum().sum())
 
    # Campos monetarios / continuos → mediana (robusta ante outliers)
    campos_mediana = [
        "ingresos_mensuales", "deuda_activa", "monto_solicitado",
        "historial_pagos", "utilizacion_credito", "antiguedad_laboral"
    ]
    for col in campos_mediana:
        mediana = df[col].median()
        df[col] = df[col].fillna(mediana)
 
    # Campos discretos enteros pequeños → moda
    campos_moda = ["atrasos_previos", "dependientes_economicos", "creditos_activos"]
    for col in campos_moda:
        moda = df[col].mode()[0]  # mode() devuelve una Series; tomamos el primero
        df[col] = df[col].fillna(moda)
 
    # ── PASO 5: Estandarización con StandardScaler ─────────────────────────────
    scaler = StandardScaler()
    df[columnas_features] = scaler.fit_transform(df[columnas_features])
    _scaler = scaler  # guardamos en memoria para usarlo en predicción
 
    # Persistir el scaler en disco (lo necesitamos entre reinicios del servidor)
    os.makedirs(STORAGE_DIR, exist_ok=True)
    with open(os.path.join(STORAGE_DIR, "scaler.pkl"), "wb") as f:
        pickle.dump(scaler, f)
 
    # ── Guardar resultado ──────────────────────────────────────────────────────
    save_clean_csv(df)
 
    filas_originales = len(get_original_data())
    filas_eliminadas = reporte["duplicados_eliminados"] + reporte["registros_basura_eliminados"]

    reporte["registros_finales"] = len(df)
    reporte["mensaje"] = (
        f"{reporte['registros_finales']} registros listos. "
        f"{reporte['duplicados_eliminados']} duplicados eliminados, "
        f"{reporte['registros_basura_eliminados']} registros basura eliminados, "
        f"{reporte['inconsistencias_convertidas_a_nan']} inconsistencias corregidas, "
        f"{reporte['nulos_imputados']} valores nulos imputados."
    )
 
    return {
        "filas_originales": filas_originales,
        "filas_resultantes": reporte["registros_finales"],
        "filas_eliminadas": filas_eliminadas,
        "valores_imputados": reporte["nulos_imputados"],
        "inconsistencias_corregidas": reporte["inconsistencias_convertidas_a_nan"],
        "mensaje": reporte["mensaje"]
    }

# ── Entrenamiento ──────────────────────────────────────────────────────────────
 
def entrenar_modelo(hiperparametros: dict = None) -> dict:
    """
    Entrena un RandomForestClassifier con los datos ya limpios.
 
    Usa los hiperparámetros recibidos o los valores por defecto si no se pasan.
    Divide los datos en 80 % entrenamiento / 20 % prueba con estratificación
    para respetar la proporción de clases.
 
    Args:
        hiperparametros: dict opcional con claves n_arboles, profundidad_maxima,
                         hojas_maximas. Valores fuera de rango son ignorados y
                         se sustituyen por los defaults.
 
    Returns:
        dict con metricas, hiperparametros, filas_entrenamiento, filas_prueba y mensaje.
 
    Raises:
        ValueError si no hay datos limpios disponibles.
    """
    global _modelo, _metricas, _hiperparams
 
    df = get_clean_data()
    if df is None:
        raise ValueError("No hay datos limpios. Ejecuta primero la limpieza de datos.")
 
    # ── Validar y normalizar hiperparámetros ───────────────────────────────────
    hp = dict(HIPERPARAMETROS_DEFAULT)  # partir de los defaults
 
    if hiperparametros:
        # n_arboles: rango recomendado 50–500
        n = int(hiperparametros.get("n_arboles", hp["n_arboles"]))
        hp["n_arboles"] = max(10, min(n, 1000))
 
        # profundidad_maxima: rango recomendado 5–30
        p = int(hiperparametros.get("profundidad_maxima", hp["profundidad_maxima"]))
        hp["profundidad_maxima"] = max(2, min(p, 100))
 
        # hojas_maximas: rango recomendado 10–200
        h = int(hiperparametros.get("hojas_maximas", hp["hojas_maximas"]))
        hp["hojas_maximas"] = max(2, min(h, 500))
 
    # ── Separar features y etiqueta ────────────────────────────────────────────
    X = df[COLUMNAS_FEATURES]
    y = df["en_riesgo"]
 
    # Estratificado para mantener la proporción de clases en ambos conjuntos
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )
 
    # ── Entrenar Random Forest ─────────────────────────────────────────────────
    modelo = RandomForestClassifier(
        n_estimators=hp["n_arboles"],
        max_depth=hp["profundidad_maxima"],
        max_leaf_nodes=hp["hojas_maximas"],
        random_state=42,
        n_jobs=-1,          # usar todos los núcleos disponibles
        class_weight="balanced",  # compensa desequilibrio de clases si lo hay
    )
    modelo.fit(X_train, y_train)
 
    # ── Evaluar en el conjunto de prueba ───────────────────────────────────────
    y_pred = modelo.predict(X_test)
 
    metricas = {
        "exactitud":  round(float(accuracy_score(y_test, y_pred)),  4),
        "precision":  round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
        "recall":     round(float(recall_score(y_test, y_pred, zero_division=0)),    4),
        "f1_score":   round(float(f1_score(y_test, y_pred, zero_division=0)),        4),
    }

    # >>>NOTA<<<: Esto es nuevo del proyecto :D  para que funcione con el frontend att: Pablo ----------------------------------------------------------------------------
    cm = confusion_matrix(y_test, y_pred)
    # Por si acaso solo hay una clase predicha en un dataset muy pequeño
    if cm.size == 1:
        if sum(y_test) == 0:
            tn, fp, fn, tp = cm[0][0], 0, 0, 0
        else:
            tn, fp, fn, tp = 0, 0, 0, cm[0][0]
    else:
        tn, fp, fn, tp = cm.ravel()
        
    matriz_confusion = {
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp)
    }

    dist_predicciones = {
        "sin_riesgo": int(sum(y_pred == 0)),
        "en_riesgo": int(sum(y_pred == 1))
    }
 # -------------------------------------------------------------------------------------------------------------------------------------

    # ── Persistir modelo en disco ──────────────────────────────────────────────
    os.makedirs(STORAGE_DIR, exist_ok=True)
    with open(os.path.join(STORAGE_DIR, "modelo.pkl"), "wb") as f:
        pickle.dump(modelo, f)
 
    # ── Actualizar estado global ───────────────────────────────────────────────
    _modelo      = modelo
    _metricas    = metricas
    _hiperparams = hp
 
    return {
        "metricas": metricas,
        "matriz_confusion": matriz_confusion,  #Nuevo pablo
        "distribucion_predicciones": dist_predicciones,  #Nuevo pablo
        "hiperparametros": {
            "n_arboles":          hp["n_arboles"],
            "profundidad_maxima": hp["profundidad_maxima"],
            "hojas_maximas":      hp["hojas_maximas"],
        },
        "filas_entrenamiento": int(len(X_train)),
        "filas_prueba":        int(len(X_test)),
        "mensaje": (
            f"Modelo entrenado con {len(X_train)} registros. "
            f"Exactitud: {metricas['exactitud']*100:.1f}%, "
            f"F1: {metricas['f1_score']*100:.1f}%."
        ),
    }