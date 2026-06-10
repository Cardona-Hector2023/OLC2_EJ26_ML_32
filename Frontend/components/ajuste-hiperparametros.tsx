'use client'

import { useState } from 'react'
import { SlidersHorizontal, RefreshCw, Loader2, TreePine } from 'lucide-react'
import { toast } from 'sonner'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import { reentrenarModelo, ApiError } from '@/lib/api'
import type {
  EntrenamientoResult,
  Hiperparametros,
  Metricas,
} from '@/lib/types'

interface Props {
  modeloEntrenado: boolean
  hiperparametros: Hiperparametros
  onReentrenado: (metricas: Metricas, resultado: EntrenamientoResult) => void
}

interface HParamConfig {
  key: keyof Hiperparametros
  label: string
  descripcion: string
  min: number
  max: number
  step: number
}

const HPARAMS: HParamConfig[] = [
  {
    key: 'n_arboles',
    label: 'Cantidad de árboles de decisión',
    descripcion: 'Número de estimadores del bosque',
    min: 10,
    max: 500,
    step: 10,
  },
  {
    key: 'profundidad_maxima',
    label: 'Profundidad máxima de los árboles',
    descripcion: 'Niveles máximos de cada árbol',
    min: 1,
    max: 50,
    step: 1,
  },
  {
    key: 'hojas_maximas',
    label: 'Número máximo de hojas por árbol',
    descripcion: 'Nodos terminales máximos por árbol',
    min: 2,
    max: 200,
    step: 2,
  },
]

export function AjusteHiperparametros({
  modeloEntrenado,
  hiperparametros,
  onReentrenado,
}: Props) {
  const [valores, setValores] = useState<Hiperparametros>(hiperparametros)
  const [reentrenando, setReentrenando] = useState(false)

  function actualizar(key: keyof Hiperparametros, valor: number) {
    setValores((prev) => ({ ...prev, [key]: valor }))
  }

  async function handleReentrenar() {
    // validación básica del frontend
    const invalido = HPARAMS.find(
      (h) => valores[h.key] < h.min || valores[h.key] > h.max,
    )
    if (invalido) {
      toast.error('Valor fuera de rango', {
        description: `${invalido.label} debe estar entre ${invalido.min} y ${invalido.max}.`,
      })
      return
    }

    setReentrenando(true)
    try {
      const res = await reentrenarModelo(valores)
      onReentrenado(res.metricas, res)
      toast.success('Modelo reentrenado', {
        description: `Nueva exactitud: ${(res.metricas.exactitud * 100).toFixed(1)}%.`,
      })
    } catch (e) {
      const msg =
        e instanceof ApiError
          ? e.message
          : e instanceof TypeError
            ? 'No se pudo conectar con el backend. Verifica que el servidor de Python esté activo.'
            : 'No se pudo reentrenar el modelo.'
      toast.error('Error al reentrenar', { description: msg })
    } finally {
      setReentrenando(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <SlidersHorizontal className="h-5 w-5 text-muted-foreground" aria-hidden="true" />
          <CardTitle>Ajuste de hiperparámetros</CardTitle>
        </div>
        <CardDescription>
          Configura los hiperparámetros del modelo y reentrena para mejorar la
          calidad de las predicciones.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {HPARAMS.map((h) => (
          <div key={h.key} className="space-y-2">
            <div className="flex items-center justify-between gap-3">
              <Label htmlFor={h.key} className="flex items-center gap-2">
                <TreePine className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
                {h.label}
              </Label>
              <Input
                id={h.key}
                type="number"
                min={h.min}
                max={h.max}
                step={h.step}
                value={valores[h.key]}
                onChange={(e) =>
                  actualizar(h.key, Number(e.target.value))
                }
                className="w-24 text-right font-mono"
              />
            </div>
            <Slider
              value={[valores[h.key]]}
              min={h.min}
              max={h.max}
              step={h.step}
              onValueChange={(v) =>
                actualizar(h.key, Array.isArray(v) ? v[0] : v)
              }
              aria-label={h.label}
            />
            <p className="text-xs text-muted-foreground">{h.descripcion}</p>
          </div>
        ))}

        <Button
          onClick={handleReentrenar}
          disabled={!modeloEntrenado || reentrenando}
          className="w-full sm:w-auto"
        >
          {reentrenando ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <RefreshCw className="h-4 w-4" />
          )}
          Reentrenar modelo
        </Button>
        {!modeloEntrenado && (
          <p className="text-xs text-muted-foreground">
            Entrena el modelo al menos una vez antes de ajustar hiperparámetros.
          </p>
        )}
      </CardContent>
    </Card>
  )
}
