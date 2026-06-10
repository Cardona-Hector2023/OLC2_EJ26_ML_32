// Tipos compartidos del dominio CreditGuard.
// El backend de Python debe responder con estas estructuras.

/** Las 9 variables que evalúa el modelo para un solicitante. */
export interface SolicitanteInput {
  ingresos_mensuales: number
  deuda_activa: number
  historial_pagos: number
  antiguedad_laboral: number
  creditos_activos: number
  monto_solicitado: number
  atrasos_previos: number
  dependientes_economicos: number
  utilizacion_credito: number
}

/** Hiperparámetros configurables del modelo (árboles de decisión). */
export interface Hiperparametros {
  n_arboles: number
  profundidad_maxima: number
  hojas_maximas: number
}

/** Métricas de evaluación del modelo entrenado. */
export interface Metricas {
  exactitud: number
  precision: number
  recall: number
  f1_score: number
}

/** Resultado de la carga masiva del CSV. */
export interface CargaResult {
  filas: number
  columnas: number
  nombre_archivo: string
  mensaje?: string
}

/** Resultado del proceso de limpieza de datos. */
export interface LimpiezaResult {
  filas_originales: number
  filas_resultantes: number
  filas_eliminadas: number
  valores_imputados: number
  inconsistencias_corregidas: number
  detalle?: string[]
  mensaje?: string
}

/** Resultado del entrenamiento o reentrenamiento. */
export interface EntrenamientoResult {
  metricas: Metricas
  hiperparametros: Hiperparametros
  filas_entrenamiento?: number
  filas_prueba?: number
  mensaje?: string
}

/** Resultado de una predicción individual. */
export interface PrediccionResult {
  // true = presenta riesgo de incumplimiento, false = no presenta riesgo
  riesgo: boolean
  probabilidad?: number
  mensaje?: string
}

export type EstadoPaso = 'pendiente' | 'completado' | 'error'
