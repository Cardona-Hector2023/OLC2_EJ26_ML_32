'use client'

import { Target, Crosshair, Radar, Gauge, BarChart3 } from 'lucide-react'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import type { Metricas } from '@/lib/types'

interface Props {
  metricas: Metricas | null
}

const ITEMS: {
  key: keyof Metricas
  label: string
  descripcion: string
  icon: typeof Target
}[] = [
  {
    key: 'exactitud',
    label: 'Exactitud',
    descripcion: 'Proporción total de predicciones correctas',
    icon: Target,
  },
  {
    key: 'precision',
    label: 'Precisión',
    descripcion: 'Aciertos entre los clasificados como riesgo',
    icon: Crosshair,
  },
  {
    key: 'recall',
    label: 'Recall',
    descripcion: 'Casos de riesgo correctamente identificados',
    icon: Radar,
  },
  {
    key: 'f1_score',
    label: 'F1 Score',
    descripcion: 'Equilibrio entre precisión y recall',
    icon: Gauge,
  },
]

function colorPorValor(v: number) {
  if (v >= 0.85) return 'text-success'
  if (v >= 0.7) return 'text-warning'
  return 'text-destructive'
}

export function PanelMetricas({ metricas }: Props) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Evaluación de rendimiento</CardTitle>
        <CardDescription>
          Métricas del modelo entrenado. Indican su precisión y fiabilidad antes
          de evaluar solicitantes reales.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {!metricas ? (
          <div className="flex flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-border py-12 text-center">
            <BarChart3 className="h-8 w-8 text-muted-foreground" aria-hidden="true" />
            <p className="text-sm text-muted-foreground">
              Aún no hay métricas. Entrena el modelo para ver su rendimiento.
            </p>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2">
            {ITEMS.map(({ key, label, descripcion, icon: Icon }) => {
              const valor = metricas[key]
              const pct = Math.round(valor * 100)
              return (
                <div
                  key={key}
                  className="rounded-lg border border-border bg-card p-4"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <Icon className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
                      <span className="text-sm font-medium text-foreground">
                        {label}
                      </span>
                    </div>
                    <span
                      className={`font-mono text-2xl font-semibold ${colorPorValor(valor)}`}
                    >
                      {pct}%
                    </span>
                  </div>
                  <p className="mt-1 text-xs text-muted-foreground">{descripcion}</p>
                  <Progress value={pct} className="mt-3" />
                </div>
              )
            })}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
