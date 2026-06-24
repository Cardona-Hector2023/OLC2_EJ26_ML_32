"use client"

import { useEffect, useState } from "react"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { PageHeader } from "@/components/page-header"
import { FeedbackMessage } from "@/components/feedback-message"
import { useAppState } from "@/components/store"
import { api } from "@/lib/api"
import type { DatasetKey, EvaluationMetrics } from "@/lib/types"
import { cn } from "@/lib/utils"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts"
import { Loader2, TrendingUp, TrendingDown } from "lucide-react"

function Metric({
  label,
  value,
  hint,
  direction,
}: {
  label: string
  value: string
  hint: string
  direction: "higher" | "lower"
}) {
  return (
    <div className="rounded-lg border border-border bg-background/40 p-4">
      <div className="mb-1 flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          {label}
        </span>
        {direction === "higher" ? (
          <TrendingUp className="size-3.5 text-emerald-400" />
        ) : (
          <TrendingDown className="size-3.5 text-primary" />
        )}
      </div>
      <p className="font-heading text-2xl font-semibold text-foreground">
        {value}
      </p>
      <p className="mt-1 text-xs leading-relaxed text-muted-foreground">
        {hint}
      </p>
    </div>
  )
}

export function EvaluacionView() {
  const { trained } = useAppState()
  const [dataset, setDataset] = useState<DatasetKey>(
    trained.freelancers ? "freelancers" : "resenas",
  )
  const [metrics, setMetrics] = useState<EvaluationMetrics | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true
    setLoading(true)
    api.getEvaluation(dataset).then((m) => {
      if (active) {
        setMetrics(m)
        setLoading(false)
      }
    })
    return () => {
      active = false
    }
  }, [dataset])

  const options: { key: DatasetKey; label: string; disabled: boolean }[] = [
    { key: "freelancers", label: "Freelancers", disabled: !trained.freelancers },
    { key: "resenas", label: "Reseñas", disabled: !trained.resenas },
  ]

  return (
    <div>
      <PageHeader
        step="Vista 4"
        title="Evaluación y Validación del Modelo"
        description="Evalúa la calidad del agrupamiento mediante métricas internas de validación calculadas para el último modelo entrenado de cada conjunto de datos."
        actions={
          <div className="inline-flex rounded-lg border border-border bg-card p-1">
            {options.map((o) => (
              <button
                key={o.key}
                type="button"
                disabled={o.disabled}
                onClick={() => setDataset(o.key)}
                className={cn(
                  "rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
                  dataset === o.key
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:text-foreground",
                  o.disabled && "cursor-not-allowed opacity-40",
                )}
              >
                {o.label}
              </button>
            ))}
          </div>
        }
      />

      {loading || !metrics ? (
        <div className="flex h-64 items-center justify-center text-muted-foreground">
          <Loader2 className="size-6 animate-spin" />
        </div>
      ) : (
        <div className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-3">
            <Metric
              label="Coeficiente de Silueta"
              value={metrics.silhouette.toFixed(2)}
              hint="Rango -1 a 1. Más alto = clusters mejor separados."
              direction="higher"
            />
            <Metric
              label="Índice Davies-Bouldin"
              value={metrics.daviesBouldin.toFixed(2)}
              hint="Más bajo = mejor separación y cohesión."
              direction="lower"
            />
            <Metric
              label="Índice Calinski-Harabasz"
              value={metrics.calinskiHarabasz.toFixed(1)}
              hint="Más alto = clusters más densos y separados."
              direction="higher"
            />
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Elección del número de clusters</CardTitle>
              <CardDescription>
                Método del codo (inercia / WCSS) y coeficiente de silueta para
                distintos valores de k.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={320}>
                <LineChart
                  data={metrics.curva}
                  margin={{ top: 10, right: 16, bottom: 10, left: 0 }}
                >
                  <CartesianGrid
                    stroke="var(--border)"
                    strokeDasharray="3 3"
                  />
                  <XAxis
                    dataKey="k"
                    tick={{ fill: "var(--muted-foreground)", fontSize: 12 }}
                    stroke="var(--border)"
                    label={{
                      value: "Número de clusters (k)",
                      position: "insideBottom",
                      offset: -5,
                      fill: "var(--muted-foreground)",
                      fontSize: 12,
                    }}
                  />
                  <YAxis
                    yAxisId="left"
                    tick={{ fill: "var(--muted-foreground)", fontSize: 12 }}
                    stroke="var(--border)"
                  />
                  <YAxis
                    yAxisId="right"
                    orientation="right"
                    domain={[0, 1]}
                    tick={{ fill: "var(--muted-foreground)", fontSize: 12 }}
                    stroke="var(--border)"
                  />
                  <Tooltip
                    contentStyle={{
                      background: "var(--popover)",
                      border: "1px solid var(--border)",
                      borderRadius: 8,
                      color: "var(--popover-foreground)",
                      fontSize: 12,
                    }}
                  />
                  <Legend
                    wrapperStyle={{
                      fontSize: 12,
                      color: "var(--muted-foreground)",
                    }}
                  />
                  <Line
                    yAxisId="left"
                    type="monotone"
                    dataKey="inercia"
                    name="Inercia (WCSS)"
                    stroke="var(--chart-2)"
                    strokeWidth={2}
                    dot={{ r: 3 }}
                  />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="silhouette"
                    name="Silueta"
                    stroke="var(--chart-1)"
                    strokeWidth={2}
                    dot={{ r: 3 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Interpretación</CardTitle>
              <CardDescription>
                Lectura en lenguaje claro de lo que indican las métricas.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <FeedbackMessage
                feedback={{ kind: "info", text: metrics.interpretacion }}
              />
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
