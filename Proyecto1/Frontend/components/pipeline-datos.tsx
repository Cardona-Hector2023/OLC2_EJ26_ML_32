'use client'

import { useRef, useState } from 'react'
import {
  Upload,
  Sparkles,
  Brain,
  FileSpreadsheet,
  CheckCircle2,
  Loader2,
} from 'lucide-react'
import { toast } from 'sonner'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import {
  cargarCSV,
  limpiarDatos,
  entrenarModelo,
  ApiError,
} from '@/lib/api'
import type {
  CargaResult,
  EntrenamientoResult,
  LimpiezaResult,
  Metricas,
} from '@/lib/types'

interface Props {
  onModeloEntrenado: (
    metricas: Metricas,
    resultado: EntrenamientoResult,
  ) => void
}

function PasoNumero({
  n,
  activo,
  hecho,
}: {
  n: number
  activo: boolean
  hecho: boolean
}) {
  return (
    <span
      className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-sm font-semibold ${
        hecho
          ? 'bg-success text-success-foreground'
          : activo
            ? 'bg-primary text-primary-foreground'
            : 'bg-muted text-muted-foreground'
      }`}
      aria-hidden="true"
    >
      {hecho ? <CheckCircle2 className="h-4 w-4" /> : n}
    </span>
  )
}

export function PipelineDatos({ onModeloEntrenado }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [archivo, setArchivo] = useState<File | null>(null)

  const [carga, setCarga] = useState<CargaResult | null>(null)
  const [limpieza, setLimpieza] = useState<LimpiezaResult | null>(null)
  const [entrenado, setEntrenado] = useState(false)

  const [cargando, setCargando] = useState(false)
  const [limpiando, setLimpiando] = useState(false)
  const [entrenando, setEntrenando] = useState(false)

  function describirError(e: unknown, fallback: string) {
    if (e instanceof ApiError) return e.message
    if (e instanceof TypeError)
      return 'No se pudo conectar con el backend. Verifica que el servidor de Python esté activo.'
    return fallback
  }

  function seleccionarArchivo(file: File | null) {
    if (!file) return
    if (!file.name.toLowerCase().endsWith('.csv')) {
      toast.error('Formato inválido', {
        description: 'Solo se permiten archivos en formato CSV.',
      })
      return
    }
    setArchivo(file)
    // reiniciar estado del pipeline al cambiar de archivo
    setCarga(null)
    setLimpieza(null)
    setEntrenado(false)
  }

  async function handleCargar() {
    if (!archivo) {
      toast.error('Selecciona un archivo CSV primero.')
      return
    }
    setCargando(true)
    try {
      const res = await cargarCSV(archivo)
      setCarga(res)
      setLimpieza(null)
      setEntrenado(false)
      toast.success('Carga masiva completada', {
        description: `${res.filas} registros y ${res.columnas} columnas cargados desde ${res.nombre_archivo}.`,
      })
    } catch (e) {
      toast.error('Error en la carga', { description: describirError(e, 'No se pudo cargar el archivo.') })
    } finally {
      setCargando(false)
    }
  }

  async function handleLimpiar() {
    setLimpiando(true)
    try {
      const res = await limpiarDatos()
      setLimpieza(res)
      setEntrenado(false)
      toast.success('Limpieza de datos completada', {
        description: `${res.filas_resultantes} registros válidos tras eliminar ${res.filas_eliminadas} y corregir ${res.inconsistencias_corregidas} inconsistencias.`,
      })
    } catch (e) {
      toast.error('Error en la limpieza', { description: describirError(e, 'No se pudo limpiar el conjunto de datos.') })
    } finally {
      setLimpiando(false)
    }
  }

  async function handleEntrenar() {
    setEntrenando(true)
    try {
      const res = await entrenarModelo()
      setEntrenado(true)
      onModeloEntrenado(res.metricas, res)
      toast.success('Entrenamiento completado', {
        description: `Modelo entrenado con éxito. Exactitud: ${(res.metricas.exactitud * 100).toFixed(1)}%.`,
      })
    } catch (e) {
      toast.error('Error en el entrenamiento', { description: describirError(e, 'No se pudo entrenar el modelo.') })
    } finally {
      setEntrenando(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Preparación y entrenamiento</CardTitle>
        <CardDescription>
          Carga los registros, depura su calidad y entrena el modelo de
          predicción.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Paso 1: Carga masiva */}
        <div className="flex gap-4">
          <PasoNumero n={1} activo={!carga} hecho={!!carga} />
          <div className="flex-1 space-y-3">
            <div>
              <h3 className="font-medium text-foreground">Carga masiva</h3>
              <p className="text-sm text-muted-foreground">
                Selecciona un archivo CSV con los registros crediticios de la
                institución.
              </p>
            </div>

            <input
              ref={inputRef}
              type="file"
              accept=".csv,text/csv"
              className="sr-only"
              onChange={(e) => seleccionarArchivo(e.target.files?.[0] ?? null)}
            />

            <button
              type="button"
              onClick={() => inputRef.current?.click()}
              className="flex w-full items-center gap-3 rounded-lg border border-dashed border-border bg-muted/40 px-4 py-3 text-left transition-colors hover:bg-muted"
            >
              <FileSpreadsheet className="h-5 w-5 text-muted-foreground" aria-hidden="true" />
              <span className="flex-1 truncate text-sm">
                {archivo ? (
                  <span className="font-medium text-foreground">{archivo.name}</span>
                ) : (
                  <span className="text-muted-foreground">
                    Haz clic para seleccionar un archivo .csv
                  </span>
                )}
              </span>
              <span className="text-xs font-medium text-primary">Examinar</span>
            </button>

            <div className="flex flex-wrap items-center gap-3">
              <Button onClick={handleCargar} disabled={!archivo || cargando}>
                {cargando ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Upload className="h-4 w-4" />
                )}
                Cargar datos
              </Button>
              {carga && (
                <Badge variant="secondary" className="gap-1">
                  <CheckCircle2 className="h-3.5 w-3.5 text-success" />
                  {carga.filas} filas · {carga.columnas} columnas
                </Badge>
              )}
            </div>
          </div>
        </div>

        <Separator />

        {/* Paso 2: Limpieza */}
        <div className="flex gap-4">
          <PasoNumero n={2} activo={!!carga && !limpieza} hecho={!!limpieza} />
          <div className="flex-1 space-y-3">
            <div>
              <h3 className="font-medium text-foreground">Limpieza de datos</h3>
              <p className="text-sm text-muted-foreground">
                Maneja valores faltantes, estandariza e identifica
                inconsistencias (ingresos negativos, porcentajes fuera de rango,
                montos en cero).
              </p>
            </div>
            <Button
              variant="secondary"
              onClick={handleLimpiar}
              disabled={!carga || limpiando}
            >
              {limpiando ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Sparkles className="h-4 w-4" />
              )}
              Limpiar datos
            </Button>

            {limpieza && (
              <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
                <ResumenLimpieza label="Originales" valor={limpieza.filas_originales} />
                <ResumenLimpieza label="Resultantes" valor={limpieza.filas_resultantes} acento />
                <ResumenLimpieza label="Eliminadas" valor={limpieza.filas_eliminadas} />
                <ResumenLimpieza label="Imputados" valor={limpieza.valores_imputados} />
              </div>
            )}
          </div>
        </div>

        <Separator />

        {/* Paso 3: Entrenamiento */}
        <div className="flex gap-4">
          <PasoNumero n={3} activo={!!limpieza && !entrenado} hecho={entrenado} />
          <div className="flex-1 space-y-3">
            <div>
              <h3 className="font-medium text-foreground">Entrenamiento</h3>
              <p className="text-sm text-muted-foreground">
                Entrena el modelo seleccionado con los datos ya preprocesados.
              </p>
            </div>
            <Button onClick={handleEntrenar} disabled={!limpieza || entrenando}>
              {entrenando ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Brain className="h-4 w-4" />
              )}
              Entrenar modelo
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

function ResumenLimpieza({
  label,
  valor,
  acento,
}: {
  label: string
  valor: number
  acento?: boolean
}) {
  return (
    <div className="rounded-lg border border-border bg-muted/40 px-3 py-2">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p
        className={`font-mono text-lg font-semibold ${acento ? 'text-success' : 'text-foreground'}`}
      >
        {valor.toLocaleString('es-GT')}
      </p>
    </div>
  )
}
