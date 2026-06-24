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
import { FieldGroup, Select, Input } from "@/components/ui/field"
import { useAppState } from "@/components/store"
import { api } from "@/lib/api"
import type {
  Algoritmo,
  DatasetKey,
  Feedback,
  TrainConfig,
  Vectorizador,
} from "@/lib/types"
import { Cpu, Loader2, Info } from "lucide-react"

const ALGORITMOS: { value: Algoritmo; label: string; nativePredict: boolean }[] =
  [
    { value: "kmeans", label: "K-Means", nativePredict: true },
    { value: "gmm", label: "Gaussian Mixture Models", nativePredict: true },
    { value: "dbscan", label: "DBSCAN", nativePredict: false },
    {
      value: "jerarquico",
      label: "Clustering Jerárquico Aglomerativo",
      nativePredict: false,
    },
  ]

export function EntrenamientoView() {
  const { trained, setTrained, cleaned } = useAppState()

  const [dataset, setDataset] = useState<DatasetKey>("freelancers")
  const [algoritmo, setAlgoritmo] = useState<Algoritmo>("kmeans")
  const [k, setK] = useState(4)
  const [metrica, setMetrica] = useState("euclidiana")
  const [epsilon, setEpsilon] = useState(0.5)
  const [minPuntos, setMinPuntos] = useState(5)
  const [vectorizador, setVectorizador] = useState<Vectorizador>("tfidf")
  const [loading, setLoading] = useState(false)
  const [fb, setFb] = useState<Feedback | null>(null)

  const algoMeta = ALGORITMOS.find((a) => a.value === algoritmo)!
  const usaK = algoritmo === "kmeans" || algoritmo === "gmm"
  const usaDbscan = algoritmo === "dbscan"

  async function train() {
    if (!cleaned) {
      setFb({
        kind: "warning",
        text: "Recomendación: limpia los datos en la Vista 1 antes de entrenar para obtener mejores resultados.",
      })
    }
    setLoading(true)
    const config: TrainConfig = {
      dataset,
      algoritmo,
      k: usaK ? k : undefined,
      metricaDistancia: usaK || algoritmo === "jerarquico" ? metrica : undefined,
      epsilon: usaDbscan ? epsilon : undefined,
      minPuntos: usaDbscan ? minPuntos : undefined,
      vectorizador: dataset === "resenas" ? vectorizador : undefined,
    }
    try {
      const result = await api.train(config)
      setTrained(dataset, result)
      setFb({
        kind: "success",
        text: result.mensaje,
      })
    } catch (e) {
      setFb({ kind: "error", text: (e as Error).message })
    } finally {
      setLoading(false)
    }
  }

  const lastResult = trained[dataset]

  return (
    <div>
      <PageHeader
        step="Vista 2"
        title="Configuración y Entrenamiento del Modelo"
        description="Selecciona el conjunto de datos, el algoritmo de clustering y sus parámetros. El entrenamiento se ejecuta de forma independiente para cada conjunto."
        actions={
          <div className="flex gap-2">
            {trained.freelancers && (
              <Badge variant="success">Freelancers entrenado</Badge>
            )}
            {trained.resenas && (
              <Badge variant="success">Reseñas entrenado</Badge>
            )}
          </div>
        }
      />

      <div className="grid gap-6 lg:grid-cols-[1.4fr_1fr]">
        <Card>
          <CardHeader>
            <CardTitle>Configuración del modelo</CardTitle>
            <CardDescription>
              Los parámetros disponibles cambian según el algoritmo elegido.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-5">
            <div className="grid gap-4 sm:grid-cols-2">
              <FieldGroup label="Conjunto de datos">
                <Select
                  value={dataset}
                  onChange={(e) => setDataset(e.target.value as DatasetKey)}
                >
                  <option value="freelancers">Freelancers</option>
                  <option value="resenas">Reseñas</option>
                </Select>
              </FieldGroup>

              <FieldGroup label="Algoritmo de clustering">
                <Select
                  value={algoritmo}
                  onChange={(e) => setAlgoritmo(e.target.value as Algoritmo)}
                >
                  {ALGORITMOS.map((a) => (
                    <option key={a.value} value={a.value}>
                      {a.label}
                    </option>
                  ))}
                </Select>
              </FieldGroup>
            </div>

            {/* Parámetros condicionales */}
            <div className="grid gap-4 sm:grid-cols-2">
              {usaK && (
                <FieldGroup label="Número de clusters (k)">
                  <Input
                    type="number"
                    min={2}
                    max={15}
                    value={k}
                    onChange={(e) => setK(Number(e.target.value))}
                  />
                </FieldGroup>
              )}
              {(usaK || algoritmo === "jerarquico") && (
                <FieldGroup label="Métrica de distancia">
                  <Select
                    value={metrica}
                    onChange={(e) => setMetrica(e.target.value)}
                  >
                    <option value="euclidiana">Euclidiana</option>
                    <option value="manhattan">Manhattan</option>
                    <option value="coseno">Coseno</option>
                  </Select>
                </FieldGroup>
              )}
              {usaDbscan && (
                <>
                  <FieldGroup label="Epsilon (ε)">
                    <Input
                      type="number"
                      step={0.1}
                      min={0.1}
                      value={epsilon}
                      onChange={(e) => setEpsilon(Number(e.target.value))}
                    />
                  </FieldGroup>
                  <FieldGroup label="Mínimo de puntos">
                    <Input
                      type="number"
                      min={1}
                      value={minPuntos}
                      onChange={(e) => setMinPuntos(Number(e.target.value))}
                    />
                  </FieldGroup>
                </>
              )}
            </div>

            {/* Vectorización solo para reseñas */}
            {dataset === "resenas" && (
              <FieldGroup
                label="Técnica de vectorización de texto"
                hint="Se aplica únicamente al conjunto de reseñas para transformar el texto en vectores."
              >
                <Select
                  value={vectorizador}
                  onChange={(e) =>
                    setVectorizador(e.target.value as Vectorizador)
                  }
                >
                  <option value="tfidf">TF-IDF</option>
                  <option value="bow">Bag of Words</option>
                </Select>
              </FieldGroup>
            )}

            {!algoMeta.nativePredict && (
              <div className="flex items-start gap-2.5 rounded-lg border border-amber-500/30 bg-amber-500/10 p-3 text-sm leading-relaxed text-amber-400">
                <Info className="mt-0.5 size-4 shrink-0" />
                <span>
                  {algoMeta.label} no soporta predicción nativa sobre nuevos
                  registros. Se aplicará una estrategia de aproximación
                  (asignar el registro al segmento del punto etiquetado más
                  cercano) para la Vista 5.
                </span>
              </div>
            )}

            <Button onClick={train} disabled={loading}>
              {loading ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                <Cpu className="size-4" />
              )}
              Entrenar Modelo
            </Button>

            <FeedbackMessage feedback={fb} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Resultado del entrenamiento</CardTitle>
            <CardDescription>
              Segmentos generados y registros asignados a cada uno.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {lastResult ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between rounded-lg bg-muted/50 px-4 py-3">
                  <span className="text-sm text-muted-foreground">
                    Segmentos generados
                  </span>
                  <span className="font-heading text-2xl font-semibold text-primary">
                    {lastResult.nSegmentos}
                  </span>
                </div>
                <ul className="space-y-2">
                  {lastResult.distribucion.map((d) => {
                    const total = lastResult.distribucion.reduce(
                      (s, x) => s + x.registros,
                      0,
                    )
                    const pct = Math.round((d.registros / total) * 100)
                    return (
                      <li key={d.segmento} className="text-sm">
                        <div className="mb-1 flex items-center justify-between">
                          <span className="font-medium">
                            Segmento {d.segmento}
                          </span>
                          <span className="text-muted-foreground">
                            {d.registros} registros ({pct}%)
                          </span>
                        </div>
                        <div className="h-2 overflow-hidden rounded-full bg-muted">
                          <div
                            className="h-full rounded-full bg-primary"
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                      </li>
                    )
                  })}
                </ul>
                <p className="text-xs text-muted-foreground">
                  Modelo y artefactos de preprocesamiento serializados en disco
                  para reutilizarse en la clasificación.
                </p>
              </div>
            ) : (
              <div className="flex h-48 flex-col items-center justify-center gap-2 text-center text-sm text-muted-foreground">
                <Cpu className="size-8 opacity-40" />
                <p>
                  Aún no has entrenado un modelo para{" "}
                  <span className="font-medium text-foreground">
                    {dataset === "freelancers" ? "Freelancers" : "Reseñas"}
                  </span>
                  .
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
