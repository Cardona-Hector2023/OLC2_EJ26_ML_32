"""
Este archivo contiene los Modelos de Pydantic (Data Transfer Objects).
Su propósito es servir de "molde" estricto para los datos que entran
(ej: la configuración al momento de entrenar) y los que salen (JSON de respuesta).

Usar Pydantic nos permite:
1. Validar automáticamente los tipos de datos (si esperamos un int, rechazará un string no numérico).
2. Autogenerar la documentación Swagger en FastAPI.
3. Mantener tipado fuerte en el código Python.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class ResumenLimpiezaArchivo(BaseModel):
    """
    Resumen de lo que ocurrió al limpiar un único archivo (freelancers o
    reseñas). Se usa para construir el mensaje de resultado que pide el
    enunciado en la Vista 1 ("Registros cargados: 1,250 | Valores nulos
    imputados: 38 | Duplicados eliminados: 14 | Registros corregidos: 9").
    """

    registros_originales: int
    registros_finales: int
    duplicados_eliminados: int
    valores_nulos_imputados: int


class LimpiezaResultado(BaseModel):
    """
    Respuesta del endpoint POST /datos/limpiar.

    Cada campo es opcional porque el usuario pudo haber cargado solo uno
    de los dos archivos (freelancers o reseñas) antes de presionar
    "Limpiar Datos".
    """

    freelancers: Optional[ResumenLimpiezaArchivo] = None
    resenas: Optional[ResumenLimpiezaArchivo] = None
    mensaje: str


# -----------------------------------------------------------------------------
# Vista 2: Configuración y Entrenamiento del Modelo
# -----------------------------------------------------------------------------


class ConfigEntrenamientoFreelancers(BaseModel):
    """
    Body esperado por POST /entrenar/freelancers.

    Nota: el mockup del enunciado incluye un selector de "métrica de
    distancia", pero KMeans de scikit-learn solo soporta distancia
    euclidiana de forma nativa, por lo que ese parámetro no se expone
    aquí (no tendría ningún efecto real sobre el entrenamiento).
    """

    k: int = Field(ge=2, le=20, description="Número de clusters a generar.")


class ConfigEntrenamientoResenas(BaseModel):
    """
    Body esperado por POST /entrenar/resenas.

    metodo_vectorizacion acepta únicamente "TF-IDF" o "Bag of Words"
    (ver clustering.configurar_vectorizador); cualquier otro valor es
    rechazado por el backend con un error 400.
    """

    k: int = Field(ge=2, le=20, description="Número de clusters a generar.")
    metodo_vectorizacion: Literal["TF-IDF", "Bag of Words"] = "TF-IDF"


class PuntoCodo(BaseModel):
    """
    Un punto de la curva del método del codo.
    - k       : número de clusters evaluado.
    - inercia : WCSS (Within-Cluster Sum of Squares) para ese k.
    - silhouette: Coeficiente de Silueta para ese k (solo se calcula
                  en el endpoint GET /evaluacion; en el entrenamiento
                  se omite para no penalizar el tiempo de respuesta).
    """

    k: int
    inercia: float
    silhouette: Optional[float] = None


class EvaluacionRespuesta(BaseModel):
    """Respuesta del endpoint GET /evaluacion."""

    dataset: str
    silhouette: float
    daviesBouldin: float
    calinskiHarabasz: float
    interpretacion: str
    curva: list[PuntoCodo]


class PuntoDispersion(BaseModel):
    """Un punto del scatter plot de segmentos (tras reducir a 2D)."""

    x: float
    y: float
    cluster: int


class MetricasEvaluacion(BaseModel):
    """Las tres métricas internas de validación obligatorias."""

    silhouette_score: float
    davies_bouldin_index: float
    calinski_harabasz_index: float


class TerminoTop(BaseModel):
    """Un término relevante dentro de un segmento de reseñas."""

    termino: str
    peso: float


class PerfilSegmentoTexto(BaseModel):
    """Perfil de un segmento de reseñas (pipeline de texto)."""

    nombre_corto: str
    terminos_top: list[TerminoTop]
    cantidad_registros: int


class PerfilSegmentoNumerico(BaseModel):
    """Perfil de un segmento de freelancers (pipeline numérico)."""

    nombre_corto: str
    promedios: dict[str, float]
    cantidad_registros: int


class EntrenamientoResultadoFreelancers(BaseModel):
    """Respuesta de POST /entrenar/freelancers."""

    k: int
    inercia: float
    metricas: MetricasEvaluacion
    interpretacion: str
    curva_codo: list[PuntoCodo]
    dispersion: list[PuntoDispersion]
    perfiles: dict[int, PerfilSegmentoNumerico]
    mensaje: str


class EntrenamientoResultadoResenas(BaseModel):
    """Respuesta de POST /entrenar/resenas."""

    k: int
    metodo_vectorizacion: str
    inercia: float
    metricas: MetricasEvaluacion
    interpretacion: str
    curva_codo: list[PuntoCodo]
    dispersion: list[PuntoDispersion]
    perfiles: dict[int, PerfilSegmentoTexto]
    mensaje: str


# -----------------------------------------------------------------------------
# Vista 5: Clasificación de Nuevo Registro
# -----------------------------------------------------------------------------

class ClasificarRequest(BaseModel):
    """Body esperado por POST /clasificar."""
    tipo: Literal["freelancer", "resena"]
    datos: Optional[dict] = None
    texto: Optional[str] = None

class ClasificarRespuesta(BaseModel):
    """Respuesta de POST /clasificar."""
    segmento: int
    nombreSegmento: str
    descripcion: str
    confianza: Optional[float] = None

# -----------------------------------------------------------------------------
# Vista 6: Exportación de Reportes
# -----------------------------------------------------------------------------

class ExportarRequest(BaseModel):
    """Body esperado por POST /exportar."""
    items: list[str]

class ExportResult(BaseModel):
    """Respuesta de POST /exportar."""
    archivos: list[str]
    mensaje: str