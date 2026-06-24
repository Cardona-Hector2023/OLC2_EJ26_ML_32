// Cliente API centralizado de TalentMosaic.
//
// Apunta a un backend FastAPI mediante la variable de entorno
// NEXT_PUBLIC_API_URL (por ejemplo http://localhost:8000).
//
// Mientras el backend no esté disponible, cada método cae automáticamente
// a datos simulados (mock) para que el frontend sea navegable. Cuando
// conectes tu backend, basta con definir NEXT_PUBLIC_API_URL y el cliente
// usará los endpoints reales.
//
// Endpoints esperados (FastAPI):
//   POST   /datos/cargar/freelancers   (multipart: file)
//   POST   /datos/cargar/resenas       (multipart: file)
//   POST   /datos/limpiar
//   POST   /modelo/entrenar            (JSON: TrainConfig)
//   GET    /segmentos?dataset=...
//   GET    /segmentos/tabla-cruzada
//   GET    /evaluacion?dataset=...
//   POST   /clasificar                 (JSON)
//   POST   /exportar                   (JSON: { items: ExportItem[] })

import type {
  CsvPreview,
  TrainConfig,
  TrainResult,
  SegmentsResponse,
  CrossTab,
  EvaluationMetrics,
  ClassifyResult,
  ExportItem,
  ExportResult,
  DatasetKey,
  Freelancer,
} from "./types"
import {
  mockFreelancersPreview,
  mockResenasPreview,
  mockSegments,
  mockCrossTab,
  mockEvaluation,
} from "./mock-data"

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? ""

export const usingMock = BASE_URL === ""

const delay = (ms: number) => new Promise((r) => setTimeout(r, ms))

async function request<T>(
  path: string,
  init: RequestInit | undefined,
  fallback: () => T | Promise<T>,
): Promise<T> {
  if (!BASE_URL) {
    await delay(500)
    return fallback()
  }
  try {
    const res = await fetch(`${BASE_URL}${path}`, init)
    if (!res.ok) {
      const detail = await res.text().catch(() => "")
      throw new Error(detail || `Error ${res.status} en ${path}`)
    }
    return (await res.json()) as T
  } catch (err) {
    // Si el backend no responde, usar mock para no bloquear la UI.
    console.log("[TalentMosaic] API fallback to mock:", path, (err as Error).message)
    await delay(400)
    return fallback()
  }
}

export const api = {
  // ---- Carga y preprocesamiento ----
  uploadFreelancers(file: File): Promise<CsvPreview> {
    const form = new FormData()
    form.append("file", file)
    return request(
      "/datos/cargar/freelancers",
      { method: "POST", body: form },
      () => mockFreelancersPreview,
    )
  },

  uploadResenas(file: File): Promise<CsvPreview> {
    const form = new FormData()
    form.append("file", file)
    return request(
      "/datos/cargar/resenas",
      { method: "POST", body: form },
      () => mockResenasPreview,
    )
  },

  cleanData(): Promise<{ mensaje: string; detalles: string[] }> {
    return request(
      "/datos/limpiar",
      { method: "POST" },
      () => ({
        mensaje: "Datos limpiados y transformados correctamente.",
        detalles: [
          "Freelancers: 60 filas válidas, 2 duplicados eliminados, 1 valor nulo imputado.",
          "Reseñas: 90 filas válidas, longitud_resena calculada para 90 registros.",
          "Variables numéricas normalizadas (StandardScaler).",
          "Texto de reseñas normalizado: minúsculas, sin acentos ni stopwords.",
        ],
      }),
    )
  },

  // ---- Entrenamiento ----
  train(config: TrainConfig): Promise<TrainResult> {
    return request(
      "/modelo/entrenar",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config),
      },
      () => {
        const k = config.k ?? (config.dataset === "freelancers" ? 4 : 3)
        const total = config.dataset === "freelancers" ? 60 : 90
        const base = Math.floor(total / k)
        const distribucion = Array.from({ length: k }, (_, i) => ({
          segmento: i,
          registros: i === k - 1 ? total - base * (k - 1) : base,
        }))
        return {
          dataset: config.dataset,
          algoritmo: config.algoritmo,
          nSegmentos: k,
          distribucion,
          mensaje: `Modelo entrenado: ${k} segmentos generados sobre ${total} registros de ${config.dataset}.`,
        }
      },
    )
  },

  // ---- Segmentos ----
  getSegments(dataset: DatasetKey): Promise<SegmentsResponse> {
    return request(`/segmentos?dataset=${dataset}`, undefined, () =>
      mockSegments(dataset),
    )
  },

  getCrossTab(): Promise<CrossTab> {
    return request("/segmentos/tabla-cruzada", undefined, () => mockCrossTab)
  },

  // ---- Evaluación ----
  getEvaluation(dataset: DatasetKey): Promise<EvaluationMetrics> {
    return request(`/evaluacion?dataset=${dataset}`, undefined, () =>
      mockEvaluation(dataset),
    )
  },

  // ---- Clasificación ----
  classifyFreelancer(
    data: Omit<Freelancer, "freelancer_id" | "segmento">,
  ): Promise<ClassifyResult> {
    return request(
      "/clasificar",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tipo: "freelancer", datos: data }),
      },
      () => ({
        segmento: 0,
        nombreSegmento: "Segmento 0 — Alto rendimiento",
        descripcion:
          "Profesionales de alto rendimiento: tarifas elevadas, gran experiencia y excelentes calificaciones.",
        confianza: 0.87,
      }),
    )
  },

  classifyResena(texto: string): Promise<ClassifyResult> {
    return request(
      "/clasificar",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tipo: "resena", texto }),
      },
      () => ({
        segmento: 0,
        nombreSegmento: "Segmento 0 — Reseñas positivas",
        descripcion:
          "Reseñas muy positivas: destacan la calidad, profesionalismo y puntualidad.",
        confianza: 0.79,
      }),
    )
  },

  // ---- Exportación ----
  exportReports(items: ExportItem[]): Promise<ExportResult> {
    const nombres: Record<ExportItem, string> = {
      freelancers_segmentado: "freelancers_segmentado.csv",
      resenas_segmentado: "resenas_segmentado.csv",
      resumen_estadistico: "resumen_estadistico.csv",
      metricas_evaluacion: "metricas_evaluacion.csv",
      reporte_visual: "reporte_visual.pdf",
    }
    return request(
      "/exportar",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ items }),
      },
      () => ({
        archivos: items.map((i) => nombres[i]),
        mensaje: `Se generaron ${items.length} archivo(s) correctamente.`,
      }),
    )
  },
}
