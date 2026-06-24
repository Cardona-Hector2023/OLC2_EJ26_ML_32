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
import { SegmentScatter, clusterColor } from "@/components/charts/scatter-chart"
import { useAppState } from "@/components/store"
import { api } from "@/lib/api"
import type {
  CrossTab,
  DatasetKey,
  SegmentsResponse,
  SegmentSummaryRow,
} from "@/lib/types"
import { cn } from "@/lib/utils"
import { Loader2 } from "lucide-react"

function DatasetSwitch({
  value,
  onChange,
  options,
}: {
  value: DatasetKey
  onChange: (v: DatasetKey) => void
  options: { key: DatasetKey; label: string; disabled: boolean }[]
}) {
  return (
    <div className="inline-flex rounded-lg border border-border bg-card p-1">
      {options.map((o) => (
        <button
          key={o.key}
          type="button"
          disabled={o.disabled}
          onClick={() => onChange(o.key)}
          className={cn(
            "rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
            value === o.key
              ? "bg-primary text-primary-foreground"
              : "text-muted-foreground hover:text-foreground",
            o.disabled && "cursor-not-allowed opacity-40",
          )}
        >
          {o.label}
        </button>
      ))}
    </div>
  )
}

function SummaryTable({ rows }: { rows: SegmentSummaryRow[] }) {
  const featureKeys = [
    ...new Set(rows.flatMap((r) => Object.keys(r.caracteristicas))),
  ]
  return (
    <div className="overflow-hidden rounded-lg border border-border">
      <div className="overflow-auto">
        <table className="w-full border-collapse text-sm">
          <thead className="bg-muted">
            <tr>
              <th className="px-3 py-2 text-left font-medium text-muted-foreground">
                Segmento
              </th>
              <th className="px-3 py-2 text-left font-medium text-muted-foreground">
                Registros
              </th>
              {featureKeys.map((k) => (
                <th
                  key={k}
                  className="whitespace-nowrap px-3 py-2 text-left font-medium text-muted-foreground"
                >
                  {k}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.segmento} className="even:bg-muted/30">
                <td className="px-3 py-2">
                  <span className="inline-flex items-center gap-2">
                    <span
                      className="size-2.5 rounded-full"
                      style={{ background: clusterColor(r.segmento) }}
                    />
                    <span className="font-medium">{r.segmento}</span>
                  </span>
                </td>
                <td className="px-3 py-2 font-medium">{r.registros}</td>
                {featureKeys.map((k) => (
                  <td
                    key={k}
                    className="whitespace-nowrap px-3 py-2 text-foreground/90"
                  >
                    {r.caracteristicas[k] ?? "—"}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function CrossTabTable({ data }: { data: CrossTab }) {
  return (
    <div className="overflow-hidden rounded-lg border border-border">
      <div className="overflow-auto">
        <table className="w-full border-collapse text-sm">
          <thead className="bg-muted">
            <tr>
              <th className="px-3 py-2 text-left font-medium text-muted-foreground">
                Freelancers ↓ / Reseñas →
              </th>
              {data.columnas.map((c) => (
                <th
                  key={c}
                  className="px-3 py-2 text-center font-medium text-muted-foreground"
                >
                  Seg. reseña {c}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.filas.map((fila, i) => (
              <tr key={fila} className="even:bg-muted/30">
                <td className="px-3 py-2 font-medium">
                  <span className="inline-flex items-center gap-2">
                    <span
                      className="size-2.5 rounded-full"
                      style={{ background: clusterColor(fila) }}
                    />
                    Seg. freelancer {fila}
                  </span>
                </td>
                {data.columnas.map((_, j) => {
                  const cell = data.celdas[i][j]
                  return (
                    <td key={j} className="px-3 py-2 text-center">
                      <span className="font-medium">{cell.cantidad}</span>
                      <span className="ml-1 text-xs text-muted-foreground">
                        ({cell.porcentaje}%)
                      </span>
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export function SegmentosView() {
  const { trained } = useAppState()
  const [dataset, setDataset] = useState<DatasetKey>(
    trained.freelancers ? "freelancers" : "resenas",
  )
  const [data, setData] = useState<SegmentsResponse | null>(null)
  const [crossTab, setCrossTab] = useState<CrossTab | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true
    setLoading(true)
    api.getSegments(dataset).then((res) => {
      if (active) {
        setData(res)
        setLoading(false)
      }
    })
    return () => {
      active = false
    }
  }, [dataset])

  useEffect(() => {
    api.getCrossTab().then(setCrossTab)
  }, [])

  const bothTrained = trained.freelancers && trained.resenas

  return (
    <div>
      <PageHeader
        step="Vista 3"
        title="Interpretación y Perfilado de Segmentos"
        description="Visualiza los segmentos resultantes, su perfil estadístico y una descripción interpretativa. Alterna entre los segmentos de freelancers y los de reseñas."
        actions={
          <DatasetSwitch
            value={dataset}
            onChange={setDataset}
            options={[
              {
                key: "freelancers",
                label: "Freelancers",
                disabled: !trained.freelancers,
              },
              {
                key: "resenas",
                label: "Reseñas",
                disabled: !trained.resenas,
              },
            ]}
          />
        }
      />

      {loading || !data ? (
        <div className="flex h-64 items-center justify-center text-muted-foreground">
          <Loader2 className="size-6 animate-spin" />
        </div>
      ) : (
        <div className="space-y-6">
          <div className="grid gap-6 lg:grid-cols-[1.3fr_1fr]">
            <Card>
              <CardHeader>
                <CardTitle>Dispersión de segmentos</CardTitle>
                <CardDescription>
                  Proyección 2D mediante reducción de dimensionalidad (PCA).
                  Cada color representa un segmento.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <SegmentScatter points={data.scatter} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Descripción de segmentos</CardTitle>
                <CardDescription>
                  Características más representativas de cada grupo.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {data.resumen.map((r) => (
                  <div
                    key={r.segmento}
                    className="rounded-lg border border-border bg-background/40 p-3"
                  >
                    <div className="mb-1 flex items-center gap-2">
                      <span
                        className="size-3 rounded-full"
                        style={{ background: clusterColor(r.segmento) }}
                      />
                      <span className="text-sm font-semibold">
                        Segmento {r.segmento}
                      </span>
                      <Badge variant="muted" className="ml-auto">
                        {r.registros} reg.
                      </Badge>
                    </div>
                    <p className="text-sm leading-relaxed text-muted-foreground">
                      {r.descripcion}
                    </p>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Resumen estadístico por segmento</CardTitle>
              <CardDescription>
                Cantidad de registros y valor promedio (o más frecuente) de cada
                característica dentro del segmento.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <SummaryTable rows={data.resumen} />
            </CardContent>
          </Card>

          {/* Términos relevantes solo para reseñas */}
          {dataset === "resenas" && (
            <Card>
              <CardHeader>
                <CardTitle>Términos más relevantes por segmento</CardTitle>
                <CardDescription>
                  Palabras predominantes que identifican el tema de cada grupo de
                  reseñas.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {data.resumen.map((r) => (
                    <div
                      key={r.segmento}
                      className="rounded-lg border border-border p-4"
                    >
                      <div className="mb-3 flex items-center gap-2">
                        <span
                          className="size-3 rounded-full"
                          style={{ background: clusterColor(r.segmento) }}
                        />
                        <span className="text-sm font-semibold">
                          Segmento {r.segmento}
                        </span>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {r.terminos?.map((t) => (
                          <span
                            key={t.termino}
                            className="rounded-md bg-primary/10 px-2 py-1 text-xs font-medium text-primary"
                            style={{
                              fontSize: `${0.7 + t.peso * 0.5}rem`,
                            }}
                          >
                            {t.termino}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Tabla cruzada */}
          <Card>
            <CardHeader>
              <CardTitle>Tabla cruzada de segmentos</CardTitle>
              <CardDescription>
                Para cada segmento de freelancers, cantidad y porcentaje de sus
                reseñas asociadas que caen en cada segmento de reseñas (unión por
                freelancer_id).
              </CardDescription>
            </CardHeader>
            <CardContent>
              {bothTrained && crossTab ? (
                <CrossTabTable data={crossTab} />
              ) : (
                <div className="rounded-lg border border-dashed border-border bg-background/40 p-6 text-center text-sm text-muted-foreground">
                  La tabla cruzada requiere haber entrenado tanto el modelo de
                  freelancers como el de reseñas.
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
