"""
Lógica para transformar, limpiar y preparar (Preprocesar) los DataFrames antes de enviarlos a entrenar.

Funciones que irán aquí:
- clean_freelancers(): Imputar valores nulos, estandarizar columnas numéricas (StandardScaler).
- clean_reviews(): Pasar texto a minúsculas, quitar caracteres especiales, eliminar "stopwords".

Mantener esto separado del endpoint asegura que el endpoint sea limpio (solo recibe la orden)
y esta capa haga el trabajo pesado de datos.



Orden de limpieza aplicado (definido y justificado en el manual técnico):
    1. Eliminación de filas duplicadas.
    2. Conversión de columnas numéricas mal tipadas (vienen como string,
       algunas con comillas y texto que representa datos faltantes).
    3. Corrección de errores de signo en proyectos_completados.
    4. Corrección de valores fuera del rango válido de cada variable.
    5. Imputación de nulos (originales + generados en los pasos 2-4)
       usando la mediana de cada columna.
"""


import numpy as np
import pandas as pd
 
# Strings que representan datos faltantes o errores de captura,
# encontrados en proyectos_completados y calificacion_promedio durante el EDA.
VALORES_NULOS_TEXTUALES = {
    "nd",
    "n/d",
    "?",
    "sin dato",
    "error",
    "desconocido",
    "nan",
    "none",
    "",
}
 
# Columnas que llegan como string (algunas con comillas) pero son numéricas.
COLUMNAS_NUMERICAS_SUCIAS = [
    "proyectos_completados",
    "tarifa_hora_promedio",
    "calificacion_promedio",
]
 
# Columnas numéricas que sí llegan tipadas como float/int pero requieren
# corrección de rango o de outliers.
COLUMNAS_NUMERICAS_LIMPIAS = [
    "ingresos_totales",
    "anios_experiencia",
    "tiempo_respuesta_horas",
    "tasa_finalizacion",
    "clientes_recurrentes",
    "horas_trabajadas_mes",
]
 
# Todas las columnas numéricas finales, usadas para la imputación por mediana.
COLUMNAS_NUMERICAS = COLUMNAS_NUMERICAS_SUCIAS + [
    c for c in COLUMNAS_NUMERICAS_LIMPIAS if c != "ingresos_totales"
] + ["ingresos_totales"]
 
 
def _normalizar_texto_nulo(valor: str) -> str:
    """Normaliza un string para compararlo contra VALORES_NULOS_TEXTUALES."""
    return valor.strip().strip('"').strip().lower()
 
 
def limpiar_columna_numerica_sucia(serie: pd.Series) -> pd.Series:
    """
    Convierte una columna que llegó como string (con comillas y/o texto
    basura) a numérica real.
 
    - Quita comillas y espacios.
    - Cualquier valor que coincida con VALORES_NULOS_TEXTUALES se convierte
      en NaN.
    - Cualquier otro valor no convertible a número también se convierte en
      NaN (red de seguridad ante texto inesperado no listado).
    """
    texto = serie.astype(str).str.strip().str.strip('"').str.strip()
    es_nulo_textual = texto.str.lower().isin(VALORES_NULOS_TEXTUALES)
    texto_para_convertir = texto.where(~es_nulo_textual, np.nan)
    return pd.to_numeric(texto_para_convertir, errors="coerce")
 
 
def corregir_proyectos_completados(serie: pd.Series) -> pd.Series:
    """
    proyectos_completados no puede ser negativo por definición del dominio.
 
    Se observó que las filas con valores negativos tienen el resto de sus
    variables (ingresos_totales, clientes_recurrentes, horas_trabajadas_mes,
    tasa_finalizacion) perfectamente consistentes con un freelancer activo
    real, y que abs(valor) cae dentro del rango normal de la distribución
    (percentiles 25-75). Esto indica un error de captura de signo, no un
    dato inválido, por lo que se corrige con abs() en vez de descartarlo
    como NaN.
    """
    return serie.abs()
 
 
def corregir_anios_experiencia(serie: pd.Series, limite_max: float = 50.0) -> pd.Series:
    """
    Años de experiencia mayores a 50 se consideran errores de captura
    (poco probables en el dominio de freelancers digitales) y se marcan
    como NaN para ser imputados posteriormente.
    """
    return serie.where(serie <= limite_max, np.nan)
 
 
def corregir_rango(serie: pd.Series, minimo: float, maximo: float) -> pd.Series:
    """Aplica clip a una columna numérica dentro de [minimo, maximo]."""
    return serie.clip(lower=minimo, upper=maximo)
 
 
def imputar_con_mediana(df: pd.DataFrame, columnas: list[str]) -> pd.DataFrame:
    """
    Imputa los nulos de cada columna con su propia mediana.
 
    Se usa mediana y no media porque, según el análisis de distribución
    (ver hist_data / skewness en el EDA), todas las columnas numéricas del
    dataset presentan asimetría relevante (|skew| > 1 en todos los casos),
    por lo que la mediana representa mejor el valor típico que la media.
    """
    df = df.copy()
    for col in columnas:
        mediana = df[col].median()
        df[col] = df[col].fillna(mediana)
    return df
 
 
def limpiar_freelancers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica el flujo completo de limpieza al dataset de freelancers.
 
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame crudo, tal como se carga desde freelancers.csv.
 
    Returns
    -------
    pd.DataFrame
        DataFrame limpio: sin duplicados, columnas numéricas con el tipo
        correcto, sin valores fuera de rango y sin nulos.
    """
    df = df.copy()
 
    # 1. Eliminar duplicados exactos.
    df = df.drop_duplicates()
 
    # 2. Convertir columnas numéricas sucias (string con comillas / texto basura).
    for col in COLUMNAS_NUMERICAS_SUCIAS:
        df[col] = limpiar_columna_numerica_sucia(df[col])
 
    # 3. Corregir error de signo en proyectos_completados.
    df["proyectos_completados"] = corregir_proyectos_completados(
        df["proyectos_completados"]
    )
 
    # 4. Corregir rangos y outliers.
    df["anios_experiencia"] = corregir_anios_experiencia(df["anios_experiencia"])
    df["tasa_finalizacion"] = corregir_rango(df["tasa_finalizacion"], 0, 100)
    df["calificacion_promedio"] = corregir_rango(df["calificacion_promedio"], 0, 5)
 
    # 5. Imputar nulos (originales + generados en los pasos 2-4) con mediana.
    columnas_a_imputar = [
        "proyectos_completados",
        "tarifa_hora_promedio",
        "anios_experiencia",
        "tiempo_respuesta_horas",
        "tasa_finalizacion",
        "calificacion_promedio",
    ]
    df = imputar_con_mediana(df, columnas_a_imputar)
 
    return df
 