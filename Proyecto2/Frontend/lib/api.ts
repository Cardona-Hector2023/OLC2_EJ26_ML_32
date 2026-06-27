// Cliente API centralizado de TalentMosaic.
//
// Apunta a un backend FastAPI mediante la variable de entorno
// NEXT_PUBLIC_API_URL (por ejemplo http://localhost:8000).
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
  LimpiezaResultado,
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

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

type BackendPerfilSegmento = {
  cantidad_registros: number
}

type BackendTrainResponse = {
  k: number
  perfiles: Record<string, BackendPerfilSegmento>
  mensaje: string
}

async function request<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  try {
    const res = await fetch(`${BASE_URL}${path}`, init)
    if (!res.ok) {
      const detail = await res.text().catch(() => "")
      throw new Error(detail || `Error ${res.status} en ${path}`)
    }
    return (await res.json()) as T
  } catch (err) {
    console.error("[TalentMosaic] API Error:", path, (err as Error).message)
    throw err;
  }
}

export const api = {
  // ---- Carga y preprocesamiento ----
  uploadFreelancers(file: File): Promise<CsvPreview> {
    const form = new FormData()
    form.append("file", file)
    return request("/datos/cargar/freelancers", { method: "POST", body: form })
  },

  uploadResenas(file: File): Promise<CsvPreview> {
    const form = new FormData()
    form.append("file", file)
    return request("/datos/cargar/resenas", { method: "POST", body: form })
  },

  cleanData(): Promise<LimpiezaResultado> {
    return request("/datos/limpiar", { method: "POST" })
  },

  // ---- Entrenamiento ----
  train(config: TrainConfig): Promise<TrainResult> {
    if (config.algoritmo !== "kmeans") {
      throw new Error(
        "El backend actual solo soporta entrenamiento con K-Means.",
      )
    }

    const path =
      config.dataset === "freelancers"
        ? "/entrenar/freelancers"
        : "/entrenar/resenas"

    const body =
      config.dataset === "freelancers"
        ? { k: config.k ?? 4 }
        : {
            k: config.k ?? 4,
            metodo_vectorizacion:
              config.vectorizador === "bow" ? "Bag of Words" : "TF-IDF",
          }

    return request<BackendTrainResponse>(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then((result) => ({
      dataset: config.dataset,
      algoritmo: config.algoritmo,
      nSegmentos: result.k,
      distribucion: Object.entries(result.perfiles)
        .map(([segmento, perfil]) => ({
          segmento: Number(segmento),
          registros: perfil.cantidad_registros,
        }))
        .sort((a, b) => a.segmento - b.segmento),
      mensaje: result.mensaje,
    }))
  },

  // ---- Segmentos ----
  getSegments(dataset: DatasetKey): Promise<SegmentsResponse> {
    return request(`/segmentos?dataset=${dataset}`)
  },

  getCrossTab(): Promise<CrossTab> {
    return request("/segmentos/tabla-cruzada")
  },

  // ---- Evaluación ----
  getEvaluation(dataset: DatasetKey): Promise<EvaluationMetrics> {
    return request(`/evaluacion?dataset=${dataset}`)
  },

  // ---- Clasificación ----
  classifyFreelancer(
    data: Omit<Freelancer, "freelancer_id" | "segmento">,
  ): Promise<ClassifyResult> {
    return request("/clasificar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tipo: "freelancer", datos: data }),
    })
  },

  classifyResena(texto: string): Promise<ClassifyResult> {
    return request("/clasificar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tipo: "resena", texto }),
    })
  },

  // ---- Exportación ----
  exportReports(items: ExportItem[]): Promise<ExportResult> {
    return request("/exportar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ items }),
    })
  },
}
