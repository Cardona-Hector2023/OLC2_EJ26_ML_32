// Cliente API de CreditGuard.
// La URL base del backend de Python se configura con NEXT_PUBLIC_API_URL.
// Por defecto apunta a http://localhost:8000 (FastAPI/Flask típico).

import type {
  CargaResult,
  EntrenamientoResult,
  Hiperparametros,
  LimpiezaResult,
  Metricas,
  PrediccionResult,
  SolicitanteInput,
} from './types'

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, '') || 'http://localhost:8000'

class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detalle = `Error ${res.status}`
    try {
      const body = await res.json()
      detalle = body.detail || body.mensaje || body.message || detalle
    } catch {
      // respuesta sin cuerpo JSON
    }
    throw new ApiError(detalle, res.status)
  }
  return res.json() as Promise<T>
}

/** POST /carga — sube el CSV con los registros crediticios. */
export async function cargarCSV(file: File): Promise<CargaResult> {
  const formData = new FormData()
  formData.append('archivo', file)
  const res = await fetch(`${API_BASE_URL}/carga`, {
    method: 'POST',
    body: formData,
  })
  return handleResponse<CargaResult>(res)
}

/** POST /limpieza — ejecuta el proceso de limpieza de datos. */
export async function limpiarDatos(): Promise<LimpiezaResult> {
  const res = await fetch(`${API_BASE_URL}/limpieza`, { method: 'POST' })
  return handleResponse<LimpiezaResult>(res)
}

/** POST /entrenamiento — entrena el modelo con los datos preprocesados. */
export async function entrenarModelo(): Promise<EntrenamientoResult> {
  const res = await fetch(`${API_BASE_URL}/entrenamiento`, { method: 'POST' })
  return handleResponse<EntrenamientoResult>(res)
}

/** POST /reentrenamiento — reentrena el modelo con nuevos hiperparámetros. */
export async function reentrenarModelo(
  hiperparametros: Hiperparametros,
): Promise<EntrenamientoResult> {
  const res = await fetch(`${API_BASE_URL}/reentrenamiento`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(hiperparametros),
  })
  return handleResponse<EntrenamientoResult>(res)
}

/** GET /metricas — obtiene las métricas del modelo entrenado (opcional). */
export async function obtenerMetricas(): Promise<Metricas> {
  const res = await fetch(`${API_BASE_URL}/metricas`)
  return handleResponse<Metricas>(res)
}

/** POST /prediccion — predice el riesgo de un solicitante individual. */
export async function predecir(
  datos: SolicitanteInput,
): Promise<PrediccionResult> {
  const res = await fetch(`${API_BASE_URL}/prediccion`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(datos),
  })
  return handleResponse<PrediccionResult>(res)
}

export { ApiError }
