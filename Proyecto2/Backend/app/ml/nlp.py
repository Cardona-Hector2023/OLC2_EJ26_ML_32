"""
Módulo de limpieza y procesamiento de texto para el dataset de reseñas
(reseñas_clientes.csv).

A diferencia de freelancers.csv, aquí los datos faltantes no se imputan
con un valor estadístico: cada columna se trata según su naturaleza y se
documenta explícitamente la ausencia de información en vez de inventarla.

Orden de limpieza aplicado (definido y justificado en el manual técnico):
    1. Cálculo de longitud_reseña a partir de texto_reseña, ANTES de
       cualquier limpieza (es un valor derivado, no una imputación).
    2. Eliminación de filas duplicadas.
    3. texto_reseña nulo -> se conserva como NaN. La fila permanece en el
       dataset para todo el análisis, pero se excluye únicamente al
       entrenar el vectorizador / modelo de clustering de texto.
    4. fecha_reseña nulo -> se conserva como NaN. Se excluye solo de
       análisis o vistas agrupadas por fecha.
    5. categoria_servicio nulo -> se reemplaza por la categoría explícita
       "Sin categoría". La fila se conserva, pero se excluye de tablas o
       gráficas que agrupen por categoría de servicio.

Nota sobre freelancer_id huérfanos: las reseñas cuyo freelancer_id no
existe en freelancers.csv NO se tocan en este módulo. Se mantienen
intactas; la exclusión correspondiente ocurre únicamente al construir la
tabla cruzada de segmentos (responsabilidad de otro módulo / vista).
"""

import numpy as np
import pandas as pd

CATEGORIA_FALTANTE = "Sin categoría"


def calcular_longitud_resena(serie_texto: pd.Series) -> pd.Series:
    """
    Calcula longitud_reseña como el número de palabras de texto_reseña.

    Si el texto es nulo, la longitud es 0: no se trata de un dato faltante
    que haya que imputar, sino de un valor derivado correcto (no hay
    texto -> no hay palabras que contar).
    """
    return serie_texto.str.split().str.len().fillna(0).astype(int)


def normalizar_categoria_servicio(
    serie_categoria: pd.Series, etiqueta: str = CATEGORIA_FALTANTE
) -> pd.Series:
    """
    Reemplaza los nulos de categoria_servicio por una categoría explícita
    ("Sin categoría"), en vez de imputar con la moda o eliminar la fila.

    Esto preserva la reseña completa para el resto del análisis (texto,
    clustering, fecha) y deja una marca explícita de que el dato de
    categoría no estaba disponible, en vez de atribuirle una categoría
    real que no se puede confirmar.
    """
    return serie_categoria.fillna(etiqueta)


def agregar_longitud_resena(df: pd.DataFrame) -> pd.DataFrame:
    """
    Paso 0 del flujo: agrega la columna longitud_reseña al DataFrame crudo,
    antes de aplicar cualquier limpieza.

    Se hace antes de limpiar para que la longitud calculada corresponda
    siempre al texto original tal como llegó en el archivo fuente.
    """
    df = df.copy()
    df["longitud_reseña"] = calcular_longitud_resena(df["texto_reseña"])
    return df


def limpiar_resenas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica el flujo completo de limpieza al dataset de reseñas.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame crudo, tal como se carga desde reseñas_clientes.csv.
        Debe incluir, como mínimo, las columnas: reseña_id, freelancer_id,
        texto_reseña, fecha_reseña, categoria_servicio.

    Returns
    -------
    pd.DataFrame
        DataFrame limpio, con longitud_reseña calculada, sin duplicados,
        con texto_reseña y fecha_reseña conservados como NaN cuando faltan
        (no se imputan), y categoria_servicio sin nulos (reemplazados por
        "Sin categoría").
    """
    df = df.copy()

    # 1. Calcular longitud_reseña con el texto original, antes de limpiar.
    if "longitud_reseña" not in df.columns:
        df = agregar_longitud_resena(df)

    # 2. Eliminar duplicados exactos.
    df = df.drop_duplicates()

    # 3. texto_reseña: no se toca, se deja como NaN cuando falta.
    #    La exclusión del entrenamiento del vectorizador se hace en el
    #    módulo de vectorización (ver obtener_textos_para_entrenamiento).

    # 4. fecha_reseña: se convierte a datetime; los valores no parseables
    #    o ausentes quedan como NaT y se conservan en el DataFrame.
    df["fecha_reseña"] = pd.to_datetime(df["fecha_reseña"], errors="coerce")

    # 5. categoria_servicio: nulos -> "Sin categoría".
    df["categoria_servicio"] = normalizar_categoria_servicio(
        df["categoria_servicio"]
    )

    return df


def obtener_textos_para_entrenamiento(df: pd.DataFrame) -> pd.DataFrame:
    """
    Devuelve únicamente las filas con texto_reseña válido (no nulo), que
    son las que deben usarse para ajustar el vectorizador (TF-IDF / Bag of
    Words) y entrenar el modelo de clustering de reseñas.

    El resto de las filas (texto_reseña nulo) permanecen en el DataFrame
    limpio completo para cualquier otro análisis, pero no participan aquí.
    """
    return df[df["texto_reseña"].notna()].copy()


def obtener_resenas_para_analisis_por_fecha(df: pd.DataFrame) -> pd.DataFrame:
    """
    Devuelve únicamente las filas con fecha_reseña válida, para usarse en
    vistas o análisis que agrupen o grafiquen por fecha.
    """
    return df[df["fecha_reseña"].notna()].copy()


def obtener_resenas_para_analisis_por_categoria(
    df: pd.DataFrame, etiqueta: str = CATEGORIA_FALTANTE
) -> pd.DataFrame:
    """
    Devuelve únicamente las filas cuya categoria_servicio es conocida
    (excluye "Sin categoría"), para usarse en tablas o gráficas agrupadas
    por categoría de servicio.
    """
    return df[df["categoria_servicio"] != etiqueta].copy()