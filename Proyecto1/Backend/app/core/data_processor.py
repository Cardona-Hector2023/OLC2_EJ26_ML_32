import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import StandardScaler
import os
import pickle
from app.core.model_manager import model_manager

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
# Nos ayuda a poder guardar el dataframe original en memoria.
def set_original_data(df: pd.DataFrame):
    """Guarda el dataframe original en memoria en el directorio storage."""
    global _original_df
    _original_df = df

# Nos ayuda a poder obtener el dataframe original de la memoria.
def get_original_data() -> pd.DataFrame:
    """Devuelve el dataframe original de la memoria o el disco."""
    global _original_df
    if _original_df is None:
        filepath = os.path.join(STORAGE_DIR, "dataset_original.csv")
        if os.path.exists(filepath):
            _original_df = pd.read_csv(filepath)
    return _original_df

# Nos ayuda a poder guardar un respaldo del CSV original en storage/.
def save_original_csv(df: pd.DataFrame):
    """Guarda un respaldo del CSV original en storage/."""
    os.makedirs(STORAGE_DIR, exist_ok=True)
    filepath = os.path.join(STORAGE_DIR, "dataset_original.csv")
    df.to_csv(filepath, index=False)

# Nos ayuda a poder obtener el dataframe limpio de la memoria.
def get_clean_data() -> pd.DataFrame:
    """Devuelve el dataframe limpio de la memoria o del disco."""
    global _clean_df
    if _clean_df is None:
        filepath = os.path.join(STORAGE_DIR, "dataset_clean.csv")
        if os.path.exists(filepath):
            _clean_df = pd.read_csv(filepath)
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
 
def get_modelo():
    """Devuelve el modelo entrenado o None si aún no se ha entrenado."""
    return model_manager.get_modelo()
 
def get_metricas() -> dict:
    """Devuelve las métricas del último entrenamiento."""
    return model_manager.get_metricas()
 
def get_hiperparametros() -> dict:
    """Devuelve los hiperparámetros usados en el último entrenamiento."""
    return model_manager.get_hiperparametros()


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
    df = get_clean_data()
    if df is None:
        raise ValueError("No hay datos limpios. Ejecuta primero la limpieza de datos.")
    return model_manager.train(df, hiperparametros)

# ── Predicción Individual ──────────────────────────────────────────────────────

def predecir_individual(datos: dict) -> dict:
    global _scaler
    
    if _scaler is None:
        path_scaler = os.path.join(STORAGE_DIR, "scaler.pkl")
        if os.path.exists(path_scaler):
            with open(path_scaler, "rb") as f:
                _scaler = pickle.load(f)
        else:
            raise ValueError("El escalador no existe. Por favor realiza la limpieza de datos primero.")
            
    try:
        df_individual = pd.DataFrame([datos], columns=COLUMNAS_FEATURES)
    except KeyError as e:
         raise ValueError(f"Falta una columna esperada: {str(e)}")
         
    df_escalado = _scaler.transform(df_individual)
    
    modelo = model_manager.obtener_modelo()
    if modelo is None:
        raise ValueError("El modelo no está entrenado. Por favor entrena el modelo primero.")
        
    prediccion = modelo.predict(df_escalado)[0]
    probabilidad = modelo.predict_proba(df_escalado)[0][1]
    
    return {
        "riesgo": bool(prediccion == 1),
        "probabilidad": float(probabilidad),
        "mensaje": "Predicción generada con éxito"
    }