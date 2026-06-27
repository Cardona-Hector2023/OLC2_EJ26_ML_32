"use client"

import { useRef, useState } from "react"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { PageHeader } from "@/components/page-header"
import { DataTable } from "@/components/data-table"
import { FeedbackMessage } from "@/components/feedback-message"
import { useAppState } from "@/components/store"
import { api } from "@/lib/api"
import type { CsvPreview, Feedback } from "@/lib/types"
import { FileSpreadsheet, MessageSquareText, Sparkles, Loader2 } from "lucide-react"

interface UploaderProps {
  title: string
  description: string
  icon: typeof FileSpreadsheet
  preview: CsvPreview | null
  onUpload: (file: File) => Promise<void>
  loading: boolean
  feedback: Feedback | null
}

function Uploader({
  title,
  description,
  icon: Icon,
  preview,
  onUpload,
  loading,
  feedback,
}: UploaderProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [fileName, setFileName] = useState<string | null>(null)

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-3">
          <div className="flex size-9 items-center justify-center rounded-lg bg-primary/15 text-primary">
            <Icon className="size-4.5" />
          </div>
          <div className="flex-1">
            <CardTitle>{title}</CardTitle>
            <CardDescription>{description}</CardDescription>
          </div>
          {preview && <Badge variant="success">Cargado</Badge>}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <input
          ref={inputRef}
          type="file"
          accept=".csv"
          className="hidden"
          onChange={(e) => {
            const f = e.target.files?.[0]
            if (f) {
              setFileName(f.name)
              onUpload(f)
            }
          }}
        />
        <div className="flex flex-col items-start gap-3 rounded-lg border border-dashed border-border bg-background/40 p-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="text-sm">
            <p className="font-medium text-foreground">
              {fileName ?? "Ningún archivo seleccionado"}
            </p>
            <p className="text-xs text-muted-foreground">Formato esperado: .csv</p>
          </div>
          <Button
            variant="outline"
            onClick={() => inputRef.current?.click()}
            disabled={loading}
          >
            {loading ? (
              <Loader2 className="size-4 animate-spin" />
            ) : (
              <FileSpreadsheet className="size-4" />
            )}
            Seleccionar archivo
          </Button>
        </div>

        <FeedbackMessage feedback={feedback} />

        {preview && <DataTable preview={preview} />}
      </CardContent>
    </Card>
  )
}

export function CargaView() {
  const {
    freelancersPreview,
    resenasPreview,
    setFreelancersPreview,
    setResenasPreview,
    cleaned,
    setCleaned,
  } = useAppState()

  const [loadingF, setLoadingF] = useState(false)
  const [loadingR, setLoadingR] = useState(false)
  const [cleaning, setCleaning] = useState(false)
  const [fbF, setFbF] = useState<Feedback | null>(null)
  const [fbR, setFbR] = useState<Feedback | null>(null)
  const [fbClean, setFbClean] = useState<Feedback | null>(null)

  async function uploadFreelancers(file: File) {
    setLoadingF(true)
    setFbF(null)
    try {
      const preview = await api.uploadFreelancers(file)
      setFreelancersPreview(preview)
      setCleaned(false)
      setFbF({
        kind: "success",
        text: `Archivo de freelancers cargado: ${preview.totalRows} filas y ${preview.columns.length} columnas detectadas.`,
      })
    } catch (e) {
      setFbF({ kind: "error", text: (e as Error).message })
    } finally {
      setLoadingF(false)
    }
  }

  async function uploadResenas(file: File) {
    setLoadingR(true)
    setFbR(null)
    try {
      const preview = await api.uploadResenas(file)
      setResenasPreview(preview)
      setCleaned(false)
      setFbR({
        kind: "success",
        text: `Archivo de reseñas cargado: ${preview.totalRows} filas y ${preview.columns.length} columnas detectadas.`,
      })
    } catch (e) {
      setFbR({ kind: "error", text: (e as Error).message })
    } finally {
      setLoadingR(false)
    }
  }

  async function clean() {
    if (!freelancersPreview && !resenasPreview) {
      setFbClean({
        kind: "error",
        text: "Debes cargar al menos un archivo CSV antes de limpiar los datos.",
      })
      return
    }
    setCleaning(true)
    setFbClean(null)
    try {
      const res = await api.cleanData()
      setCleaned(true)
      const detalles = [
        res.freelancers
          ? `Freelancers: ${res.freelancers.registros_finales} registros finales, ${res.freelancers.duplicados_eliminados} duplicados eliminados y ${res.freelancers.valores_nulos_imputados} nulos imputados.`
          : null,
        res.resenas
          ? `Reseñas: ${res.resenas.registros_finales} registros finales, ${res.resenas.duplicados_eliminados} duplicados eliminados y ${res.resenas.valores_nulos_imputados} nulos imputados.`
          : null,
      ].filter(Boolean)
      setFbClean({
        kind: "success",
        text: [res.mensaje, ...detalles].join(" "),
      })
    } catch (e) {
      setFbClean({ kind: "error", text: (e as Error).message })
    } finally {
      setCleaning(false)
    }
  }

  return (
    <div>
      <PageHeader
        step="Vista 1"
        title="Carga y Preprocesamiento de Datos"
        description="Incorpora de forma independiente el archivo de perfiles de freelancers y el de reseñas de clientes. Cada archivo sigue su propio flujo de limpieza y transformación antes del análisis."
        actions={
          cleaned ? (
            <Badge variant="success">Datos limpios</Badge>
          ) : (
            <Badge variant="muted">Sin limpiar</Badge>
          )
        }
      />

      <div className="grid gap-6 lg:grid-cols-2">
        <Uploader
          title="freelancers.csv"
          description="Perfil y desempeño de cada freelancer."
          icon={FileSpreadsheet}
          preview={freelancersPreview}
          onUpload={uploadFreelancers}
          loading={loadingF}
          feedback={fbF}
        />
        <Uploader
          title="reseñas_clientes.csv"
          description="Reseñas textuales escritas por los clientes."
          icon={MessageSquareText}
          preview={resenasPreview}
          onUpload={uploadResenas}
          loading={loadingR}
          feedback={fbR}
        />
      </div>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Limpieza y transformación</CardTitle>
          <CardDescription>
            Ejecuta la limpieza, normalización de variables numéricas y
            preparación del texto de reseñas. El resultado se muestra abajo.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Button onClick={clean} disabled={cleaning}>
            {cleaning ? (
              <Loader2 className="size-4 animate-spin" />
            ) : (
              <Sparkles className="size-4" />
            )}
            Limpiar Datos
          </Button>
          <FeedbackMessage feedback={fbClean} />
        </CardContent>
      </Card>
    </div>
  )
}
