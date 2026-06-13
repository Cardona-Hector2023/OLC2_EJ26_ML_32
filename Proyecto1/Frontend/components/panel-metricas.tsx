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
import type { EntrenamientoResult, Metricas } from '@/lib/types'
import {
  PieChart,
  Pie,
  Cell,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from 'recharts'

interface Props {
  resultado: EntrenamientoResult | null
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

const COLORS = ['#10b981', '#ef4444'] // Verde para Sin Riesgo, Rojo para En Riesgo

export function PanelMetricas({ resultado }: Props) {
  const metricas = resultado?.metricas
  const dist = resultado?.distribucion_predicciones
  const cm = resultado?.matriz_confusion

  const pieData = dist
    ? [
        { name: 'Sin Riesgo', value: dist.sin_riesgo },
        { name: 'En Riesgo', value: dist.en_riesgo },
      ]
    : []

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
        {!resultado || !metricas ? (
          <div className="flex flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-border py-12 text-center">
            <BarChart3 className="h-8 w-8 text-muted-foreground" aria-hidden="true" />
            <p className="text-sm text-muted-foreground">
              Aún no hay métricas. Entrena el modelo para ver su rendimiento.
            </p>
          </div>
        ) : (
          <div className="space-y-8">
            {/* Métricas Principales */}
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

            <div className="grid gap-6 md:grid-cols-2">
              {/* Distribución de Predicciones */}
              {dist && (
                <div className="rounded-lg border border-border bg-card p-4 flex flex-col items-center">
                  <h4 className="text-sm font-medium mb-4 w-full text-left">Distribución de Predicciones (Test)</h4>
                  <div className="h-64 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={pieData}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                          label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                        >
                          {pieData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <RechartsTooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}

              {/* Matriz de Confusión */}
              {cm && (
                <div className="rounded-lg border border-border bg-card p-4 flex flex-col">
                  <h4 className="text-sm font-medium mb-4 w-full text-left">Matriz de Confusión</h4>
                  <div className="flex-1 flex items-center justify-center">
                    <div className="grid grid-cols-3 gap-2 text-center text-sm">
                      <div></div>
                      <div className="font-semibold text-muted-foreground">Predicho: 0</div>
                      <div className="font-semibold text-muted-foreground">Predicho: 1</div>
                      
                      <div className="font-semibold text-muted-foreground flex items-center justify-end pr-2">Real: 0</div>
                      <div className="bg-emerald-100 dark:bg-emerald-900/30 p-4 rounded-md border border-emerald-200 dark:border-emerald-800">
                        <div className="text-2xl font-bold text-emerald-700 dark:text-emerald-400">{cm.tn}</div>
                        <div className="text-xs text-muted-foreground">Verdaderos<br/>Negativos</div>
                      </div>
                      <div className="bg-red-50 dark:bg-red-900/10 p-4 rounded-md border border-red-100 dark:border-red-900/50">
                        <div className="text-2xl font-bold text-red-500">{cm.fp}</div>
                        <div className="text-xs text-muted-foreground">Falsos<br/>Positivos</div>
                      </div>

                      <div className="font-semibold text-muted-foreground flex items-center justify-end pr-2">Real: 1</div>
                      <div className="bg-red-50 dark:bg-red-900/10 p-4 rounded-md border border-red-100 dark:border-red-900/50">
                        <div className="text-2xl font-bold text-red-500">{cm.fn}</div>
                        <div className="text-xs text-muted-foreground">Falsos<br/>Negativos</div>
                      </div>
                      <div className="bg-emerald-100 dark:bg-emerald-900/30 p-4 rounded-md border border-emerald-200 dark:border-emerald-800">
                        <div className="text-2xl font-bold text-emerald-700 dark:text-emerald-400">{cm.tp}</div>
                        <div className="text-xs text-muted-foreground">Verdaderos<br/>Positivos</div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
