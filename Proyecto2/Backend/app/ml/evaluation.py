"""
Módulo de evaluación y validación de modelos de clustering.

Contiene únicamente lo relacionado con MEDIR la calidad de un agrupamiento
ya obtenido (Vista 4 del enunciado: Evaluación y Validación del Modelo).
No contiene nada de entrenamiento ni de interpretación/perfilado de
segmentos — eso vive en clustering.py.

Aplica tanto al pipeline numérico (freelancers) como al de texto
(reseñas): ambos le pasan la matriz que usaron para entrenar (escalada o
vectorizada) junto con las etiquetas de cluster resultantes.
"""

from sklearn.cluster import KMeans
from sklearn.metrics import (
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)
from scipy.sparse import issparse

SEED = 42


def evaluar_modelo(X, labels) -> dict:
    """
    Calcula las tres métricas internas de validación obligatorias según
    el enunciado: Coeficiente de Silueta, Índice de Davies-Bouldin e
    Índice de Calinski-Harabasz.

    Parameters
    ----------
    X : matriz usada para entrenar el modelo (escalada para freelancers,
        vectorizada -TF-IDF/BoW- para reseñas). Nunca el DataFrame crudo.
    labels : etiquetas de cluster asignadas (modelo.labels_).

    Returns
    -------
    dict con las claves silhouette_score, davies_bouldin_index y
    calinski_harabasz_index, listo para serializar a JSON.

    Nota: silhouette_score acepta matrices dispersas directamente, pero
    davies_bouldin_score y calinski_harabasz_score de scikit-learn
    requieren un array denso. Cuando X proviene del pipeline de texto
    (matriz dispersa), se convierte a denso solo para esas dos métricas.
    Para el pipeline numérico (ya denso) esta conversión no tiene costo
    ni efecto.
    """
    X_denso = X.toarray() if issparse(X) else X

    return {
        "silhouette_score": float(silhouette_score(X, labels)),
        "davies_bouldin_index": float(davies_bouldin_score(X_denso, labels)),
        "calinski_harabasz_index": float(calinski_harabasz_score(X_denso, labels)),
    }


def calcular_curva_codo(X, k_min: int = 2, k_max: int = 10) -> list[dict]:
    """
    Calcula la inercia (WCSS) y el Coeficiente de Silueta de KMeans para
    un rango de valores de k.

    El enunciado pide explícitamente en la Vista 4 una "Gráfica de apoyo
    a la elección del número de clusters", con soporte para mostrar tanto
    la curva del codo (inercia/WCSS) como los coeficientes de silueta
    para distintos valores de k.

    Returns
    -------
    list[dict] con la forma:
        [{"k": 2, "inercia": 123.4, "silhouette": 0.45}, ...]
    lista para graficar las dos curvas directamente en el frontend.

    Nota: el cálculo de silhouette_score por cada k añade tiempo de
    cómputo lineal en el número de registros. Para datasets grandes puede
    ser lento, pero se acepta dado que esta función solo se invoca desde
    los endpoints de entrenamiento y evaluación, no en tiempo real.
    """
    resultado = []
    for k in range(k_min, k_max + 1):
        modelo_k = KMeans(n_clusters=k, n_init=10, random_state=SEED).fit(X)
        sil = float(silhouette_score(X, modelo_k.labels_))
        resultado.append({
            "k": k,
            "inercia": float(modelo_k.inertia_),
            "silhouette": sil,
        })
    return resultado


def interpretar_metricas(metricas: dict) -> str:
    """
    Traduce las métricas numéricas en una breve interpretación textual,
    tal como pide el enunciado: "Breve interpretación textual de lo que
    indican las métricas obtenidas (por ejemplo, si los clusters están
    bien separados o se traslapan)".

    Los umbrales usados son heurísticas de referencia general (no existe
    un estándar único en la literatura), aplicadas de forma consistente
    para dar una lectura rápida; la interpretación detallada por dataset
    debe complementarse en el manual técnico.
    """
    silueta = metricas["silhouette_score"]

    if silueta >= 0.5:
        calidad = "Los segmentos están bien separados entre sí."
    elif silueta >= 0.25:
        calidad = "Los segmentos presentan una separación moderada, con cierto traslape."
    else:
        calidad = "Los segmentos se traslapan considerablemente; la separación es débil."

    return (
        f"{calidad} Coeficiente de Silueta: {silueta:.2f} "
        f"(rango -1 a 1, mayor es mejor). "
        f"Índice de Davies-Bouldin: {metricas['davies_bouldin_index']:.2f} "
        f"(menor es mejor). "
        f"Índice de Calinski-Harabasz: {metricas['calinski_harabasz_index']:.1f} "
        f"(mayor es mejor)."
    )