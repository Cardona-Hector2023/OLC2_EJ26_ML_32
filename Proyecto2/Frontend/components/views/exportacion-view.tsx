"use client"

import { useState } from "react"
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
import { FeedbackMessage } from "@/components/feedback-message"
import { api } from "@/lib/api"
import type { ExportItem, Feedback } from "@/lib/types"
import { cn } from "@/lib/utils"
import { Download, Loader2, FileText, FileSpreadsheet, Check } from "lucide-react"

const ITEMS: {
  key: ExportItem
  title: string
  description: string
  formato: "CSV" | "PDF"
}[] = [
  {
    key: "freelancers_segmentado",
    title: "Dataset de freelancers segmentado",
    description: "Incluye la columna de segmento asignado.",
    formato: "CSV",
  },
  {
    key: "resenas_segmentado",
    title: "Dataset de reseñas segmentado",
    description: "Incluye la columna de segmento asignado.",
    formato: "CSV",
  },
  {
    key: "resumen_estadistico",
    title: "Resumen estadístico por segmento",
    description: "Promedios y modas por característica.",
    formato: "CSV",
  },
  {
    key: "metricas_evaluacion",
    title: "Métricas de evaluación del modelo",
    description: "Silhouette, Davies-Bouldin y Calinski-Harabasz.",
    formato: "CSV",
  },
  {
    key: "reporte_visual",
    title: "Reporte gráfico",
    description:
      "Combina dispersión, nube de palabras y descripciones interpretativas.",
    formato: "PDF",
  },
]

export function ExportacionView() {
  const [selected, setSelected] = useState<Set<ExportItem>>(new Set())
  const [loading, setLoading] = useState(false)
  const [fb, setFb] = useState<Feedback | null>(null)

  function toggle(key: ExportItem) {
    setSelected((prev) => {
      const next = new Set(prev)
      next.has(key) ? next.delete(key) : next.add(key)
      return next
    })
    setFb(null)
  }

  async function exportar() {
    if (selected.size === 0) {
      setFb({
        kind: "error",
        text: "Debes seleccionar al menos un elemento para exportar.",
      })
      return
    }
    setLoading(true)
    setFb(null)
    try {
      const res = await api.exportReports([...selected])
      
      // Forzar la descarga creando un Blob para evitar que el navegador abra los PDF en la misma pestaña
      for (const ruta of res.archivos) {
        try {
          const url = `http://localhost:8000${ruta}`
          const response = await fetch(url)
          const blob = await response.blob()
          const blobUrl = window.URL.createObjectURL(blob)
          const a = document.createElement("a")
          a.style.display = "none"
          a.href = blobUrl
          a.download = ruta.split("/").pop() || "export"
          document.body.appendChild(a)
          a.click()
          window.URL.revokeObjectURL(blobUrl)
          document.body.removeChild(a)
        } catch (err) {
          console.error("Error descargando", ruta, err)
        }
      }

      setFb({
        kind: "success",
        text: `${res.mensaje} Las descargas iniciaron automáticamente.`,
      })
    } catch (e) {
      setFb({ kind: "error", text: (e as Error).message })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <PageHeader
        step="Vista 6"
        title="Exportación de Reportes"
        description="Selecciona qué elementos incluir en la exportación. Los elementos 1 a 4 se descargan como archivos CSV independientes; el reporte gráfico siempre se genera como un único PDF."
        actions={
          <Badge variant={selected.size ? "default" : "muted"}>
            {selected.size} seleccionado{selected.size === 1 ? "" : "s"}
          </Badge>
        }
      />

      <Card>
        <CardHeader>
          <CardTitle>Elementos a exportar</CardTitle>
          <CardDescription>
            Marca de forma independiente cada elemento. El formato de cada uno es
            fijo según el tipo de contenido.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {ITEMS.map((item, i) => {
            const checked = selected.has(item.key)
            return (
              <button
                key={item.key}
                type="button"
                onClick={() => toggle(item.key)}
                className={cn(
                  "flex w-full items-start gap-3 rounded-lg border p-4 text-left transition-colors",
                  checked
                    ? "border-primary bg-primary/5"
                    : "border-border bg-background/40 hover:border-border/80",
                )}
              >
                <span
                  className={cn(
                    "mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-md border transition-colors",
                    checked
                      ? "border-primary bg-primary text-primary-foreground"
                      : "border-border",
                  )}
                >
                  {checked && <Check className="size-3.5" />}
                </span>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-foreground">
                      {i + 1}. {item.title}
                    </span>
                  </div>
                  <p className="mt-0.5 text-sm leading-relaxed text-muted-foreground">
                    {item.description}
                  </p>
                </div>
                <Badge
                  variant={item.formato === "PDF" ? "warning" : "secondary"}
                  className="mt-0.5"
                >
                  {item.formato === "PDF" ? (
                    <FileText className="size-3" />
                  ) : (
                    <FileSpreadsheet className="size-3" />
                  )}
                  {item.formato}
                </Badge>
              </button>
            )
          })}

          <div className="flex flex-col gap-3 pt-2">
            <Button
              onClick={exportar}
              disabled={loading || selected.size === 0}
              className="w-fit"
            >
              {loading ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                <Download className="size-4" />
              )}
              Exportar Selección
            </Button>
            <FeedbackMessage feedback={fb} />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
