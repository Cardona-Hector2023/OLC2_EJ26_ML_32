"use client"

import { useState, useEffect } from "react"
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
import { FieldGroup, Input, Select, Textarea } from "@/components/ui/field"
import { clusterColor } from "@/components/charts/scatter-chart"
import { useAppState } from "@/components/store"
import { api } from "@/lib/api"
import type { ClassifyResult, Feedback } from "@/lib/types"
import { cn } from "@/lib/utils"
import { UserPlus, Loader2, Target } from "lucide-react"

type Tipo = "freelancer" | "resena"

const CATEGORIAS = [
  "Desarrollo de Software",
  "Diseño Gráfico",
  "Redacción y Traducción",
  "Marketing Digital",
  "Soporte Administrativo Virtual",
]

const NUM_FIELDS: { key: string; label: string; step?: number }[] = [
  { key: "proyectos_completados", label: "Proyectos completados" },
  { key: "ingresos_totales", label: "Ingresos totales (USD)" },
  { key: "tarifa_hora_promedio", label: "Tarifa por hora promedio (USD)" },
  { key: "anios_experiencia", label: "Años de experiencia" },
  { key: "tiempo_respuesta_horas", label: "Tiempo de respuesta (horas)", step: 0.1 },
  { key: "tasa_finalizacion", label: "Tasa de finalización (0–100)" },
  { key: "calificacion_promedio", label: "Calificación promedio (0–5)", step: 0.1 },
  { key: "clientes_recurrentes", label: "Clientes recurrentes" },
  { key: "horas_trabajadas_mes", label: "Horas trabajadas al mes" },
]

export function ClasificacionView() {
  const { trained } = useAppState()
  const [tipo, setTipo] = useState<Tipo>("freelancer")
  const [form, setForm] = useState<Record<string, string>>({})
  const [categoria, setCategoria] = useState(CATEGORIAS[0])
  const [texto, setTexto] = useState("")
  const [loading, setLoading] = useState(false)
  const [fb, setFb] = useState<Feedback | null>(null)
  const [result, setResult] = useState<ClassifyResult | null>(null)

  useEffect(() => {
    try {
      const saved = sessionStorage.getItem("clasificacionState")
      if (saved) {
        const parsed = JSON.parse(saved)
        if (parsed.tipo) setTipo(parsed.tipo)
        if (parsed.form) setForm(parsed.form)
        if (parsed.categoria) setCategoria(parsed.categoria)
        if (parsed.texto) setTexto(parsed.texto)
        if (parsed.result) setResult(parsed.result)
      }
    } catch (e) {
      // Ignorar errores de parsing
    }
  }, [])

  useEffect(() => {
    sessionStorage.setItem("clasificacionState", JSON.stringify({
      tipo, form, categoria, texto, result
    }))
  }, [tipo, form, categoria, texto, result])


  const modeloDisponible =
    tipo === "freelancer" ? Boolean(trained.freelancers) : Boolean(trained.resenas)

  async function classify() {
    setResult(null)
    if (!modeloDisponible) {
      setFb({
        kind: "error",
        text: `No existe un modelo entrenado para ${
          tipo === "freelancer" ? "freelancers" : "reseñas"
        }. Entrena uno en la Vista 2 antes de clasificar.`,
      })
      return
    }
    if (tipo === "freelancer") {
      const faltan = NUM_FIELDS.filter((f) => !form[f.key])
      if (faltan.length) {
        setFb({
          kind: "error",
          text: `Completa todos los campos numéricos. Faltan: ${faltan
            .map((f) => f.label)
            .join(", ")}.`,
        })
        return
      }
    } else if (!texto.trim()) {
      setFb({
        kind: "error",
        text: "Ingresa el contenido de la reseña a clasificar.",
      })
      return
    }

    setLoading(true)
    setFb(null)
    try {
      const res =
        tipo === "freelancer"
          ? await api.classifyFreelancer({
              ...(Object.fromEntries(
                NUM_FIELDS.map((f) => [f.key, Number(form[f.key])]),
              ) as Record<string, number>),
              categoria_principal: categoria,
            } as any)
          : await api.classifyResena(texto)
      setResult(res)
      setFb({
        kind: "success",
        text: `Registro asignado correctamente a "${res.nombreSegmento}".`,
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
        step="Vista 5"
        title="Clasificación de Nuevo Registro"
        description="Asigna un freelancer o una reseña que no formó parte del entrenamiento al segmento existente que mejor le corresponde, reutilizando el modelo y los artefactos ya entrenados."
      />

      <div className="grid gap-6 lg:grid-cols-[1.2fr_1fr]">
        <Card>
          <CardHeader>
            <CardTitle>Datos del registro</CardTitle>
            <CardDescription>
              Selecciona el tipo de registro y completa la información.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-5">
            <FieldGroup label="Tipo de registro a clasificar">
              <div className="inline-flex w-full rounded-lg border border-border bg-card p-1">
                {(["freelancer", "resena"] as Tipo[]).map((t) => (
                  <button
                    key={t}
                    type="button"
                    onClick={() => {
                      setTipo(t)
                      setResult(null)
                      setFb(null)
                    }}
                    className={cn(
                      "flex-1 rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
                      tipo === t
                        ? "bg-primary text-primary-foreground"
                        : "text-muted-foreground hover:text-foreground",
                    )}
                  >
                    {t === "freelancer" ? "Freelancer" : "Reseña"}
                  </button>
                ))}
              </div>
            </FieldGroup>

            {!modeloDisponible && (
              <FeedbackMessage
                feedback={{
                  kind: "warning",
                  text: `Esta sección requiere un modelo entrenado de ${
                    tipo === "freelancer" ? "freelancers" : "reseñas"
                  }. Entrénalo en la Vista 2.`,
                }}
              />
            )}

            {tipo === "freelancer" ? (
              <fieldset
                disabled={!modeloDisponible}
                className="grid gap-4 sm:grid-cols-2 disabled:opacity-60"
              >
                {NUM_FIELDS.map((f) => (
                  <FieldGroup key={f.key} label={f.label}>
                    <Input
                      type="number"
                      step={f.step ?? 1}
                      value={form[f.key] ?? ""}
                      onChange={(e) =>
                        setForm((p) => ({ ...p, [f.key]: e.target.value }))
                      }
                      placeholder="0"
                    />
                  </FieldGroup>
                ))}
                <FieldGroup label="Categoría principal">
                  <Select
                    value={categoria}
                    onChange={(e) => setCategoria(e.target.value)}
                  >
                    {CATEGORIAS.map((c) => (
                      <option key={c} value={c}>
                        {c}
                      </option>
                    ))}
                  </Select>
                </FieldGroup>
              </fieldset>
            ) : (
              <FieldGroup
                label="Contenido de la reseña"
                hint="El texto se transforma con el mismo vectorizador ajustado durante el entrenamiento."
              >
                <Textarea
                  disabled={!modeloDisponible}
                  value={texto}
                  onChange={(e) => setTexto(e.target.value)}
                  placeholder="Escribe aquí la reseña del cliente..."
                  className="min-h-32"
                />
              </FieldGroup>
            )}

            <Button onClick={classify} disabled={loading || !modeloDisponible}>
              {loading ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                <UserPlus className="size-4" />
              )}
              Asignar Segmento
            </Button>

            <FeedbackMessage feedback={fb} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Resultado de la clasificación</CardTitle>
            <CardDescription>
              Segmento asignado y su descripción interpretativa.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {result ? (
              <div className="space-y-4">
                <div
                  className="rounded-lg border p-4"
                  style={{
                    borderColor: clusterColor(result.segmento),
                    background: "var(--background)",
                  }}
                >
                  <div className="mb-2 flex items-center gap-2">
                    <span
                      className="size-3 rounded-full"
                      style={{ background: clusterColor(result.segmento) }}
                    />
                    <span className="font-heading text-lg font-semibold">
                      {result.nombreSegmento}
                    </span>
                  </div>
                  <p className="text-sm leading-relaxed text-muted-foreground">
                    {result.descripcion}
                  </p>
                  {result.confianza != null && (
                    <Badge variant="muted" className="mt-3">
                      Confianza: {Math.round(result.confianza * 100)}%
                    </Badge>
                  )}
                </div>
              </div>
            ) : (
              <div className="flex h-48 flex-col items-center justify-center gap-2 text-center text-sm text-muted-foreground">
                <Target className="size-8 opacity-40" />
                <p>El segmento asignado aparecerá aquí.</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
