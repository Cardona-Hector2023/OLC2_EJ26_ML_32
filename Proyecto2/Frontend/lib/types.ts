// Dominio de TalentMosaic
// Estos tipos reflejan las columnas de freelancers.csv y reseñas_clientes.csv
// descritas en el enunciado del proyecto.

export type DatasetKey = "freelancers" | "resenas"

export interface Freelancer {
  freelancer_id: string
  proyectos_completados: number
  ingresos_totales: number
  tarifa_hora_promedio: number
  anios_experiencia: number
  tiempo_respuesta_horas: number
  tasa_finalizacion: number // 0 - 100
  calificacion_promedio: number // 0 - 5
  categoria_principal: string
  clientes_recurrentes: number
  horas_trabajadas_mes: number
  // columna agregada tras el clustering
  segmento?: number
}

export interface Resena {
  resena_id: string
  freelancer_id: string
  texto_resena: string
  fecha_resena: string
  categoria_servicio: string
  longitud_resena: number
  // columna agregada tras el clustering
  segmento?: number
}

// Vista previa genérica de un CSV cargado
export interface CsvPreview {
  columns: string[]
  rows: Record<string, string | number>[]
  totalRows: number
}

// Algoritmos soportados
export type Algoritmo = "kmeans" | "dbscan" | "jerarquico" | "gmm"
export type Vectorizador = "tfidf" | "bow"

export interface TrainConfig {
  dataset: DatasetKey
  algoritmo: Algoritmo
  // parámetros opcionales según algoritmo
  k?: number
  metricaDistancia?: string
  epsilon?: number
  minPuntos?: number
  vectorizador?: Vectorizador
}

export interface TrainResult {
  dataset: DatasetKey
  algoritmo: Algoritmo
  nSegmentos: number
  distribucion: { segmento: number; registros: number }[]
  mensaje: string
}

// Punto en el espacio reducido (PCA) para el scatter
export interface ScatterPoint {
  x: number
  y: number
  segmento: number
  id: string
}

export interface SegmentSummaryRow {
  segmento: number
  registros: number
  // promedios o modas por característica
  caracteristicas: Record<string, string | number>
  descripcion: string
  // sólo para reseñas: términos más relevantes
  terminos?: { termino: string; peso: number }[]
}

export interface SegmentsResponse {
  dataset: DatasetKey
  scatter: ScatterPoint[]
  resumen: SegmentSummaryRow[]
}

// Tabla cruzada freelancers x reseñas
export interface CrossTab {
  filas: number[] // segmentos de freelancers
  columnas: number[] // segmentos de reseñas
  // celdas[fila][col] = { cantidad, porcentaje }
  celdas: { cantidad: number; porcentaje: number }[][]
}

export interface EvaluationMetrics {
  dataset: DatasetKey
  silhouette: number
  daviesBouldin: number
  calinskiHarabasz: number
  interpretacion: string
  // datos para la gráfica del codo / silueta por k
  curva: { k: number; inercia: number; silhouette: number }[]
}

export interface ClassifyResult {
  segmento: number
  nombreSegmento: string
  descripcion: string
  confianza?: number
}

export type ExportItem =
  | "freelancers_segmentado"
  | "resenas_segmentado"
  | "resumen_estadistico"
  | "metricas_evaluacion"
  | "reporte_visual"

export interface ExportResult {
  archivos: string[]
  mensaje: string
}

export type FeedbackKind = "info" | "success" | "error" | "warning"

export interface Feedback {
  kind: FeedbackKind
  text: string
}
