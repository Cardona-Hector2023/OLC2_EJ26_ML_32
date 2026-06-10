'use client'

import { useState } from 'react'
import {
  ShieldAlert,
  ShieldCheck,
  Loader2,
  UserSearch,
  Lock,
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
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { CAMPOS_SOLICITANTE } from '@/lib/campos'
import { predecir, ApiError } from '@/lib/api'
import type { PrediccionResult, SolicitanteInput } from '@/lib/types'

interface Props {
  habilitado: boolean
}

type FormState = Record<keyof SolicitanteInput, string>

const ESTADO_INICIAL = Object.fromEntries(
  CAMPOS_SOLICITANTE.map((c) => [c.key, '']),
) as FormState

export function FormularioPrediccion({ habilitado }: Props) {
  const [form, setForm] = useState<FormState>(ESTADO_INICIAL)
  const [resultado, setResultado] = useState<PrediccionResult | null>(null)
  const [prediciendo, setPrediciendo] = useState(false)

  function actualizar(key: keyof SolicitanteInput, valor: string) {
    setForm((prev) => ({ ...prev, [key]: valor }))
  }

  function validar(): SolicitanteInput | null {
    const datos = {} as SolicitanteInput
    for (const campo of CAMPOS_SOLICITANTE) {
      const raw = form[campo.key].trim()
      if (raw === '') {
        toast.error('Campos incompletos', {
          description: `Ingresa un valor para "${campo.label}". Todos los parámetros son obligatorios.`,
        })
        return null
      }
      const num = Number(raw)
      if (Number.isNaN(num)) {
        toast.error('Valor inválido', {
          description: `"${campo.label}" debe ser un número.`,
        })
        return null
      }
      if (campo.min !== undefined && num < campo.min) {
        toast.error('Valor fuera de rango', {
          description: `"${campo.label}" no puede ser menor que ${campo.min}.`,
        })
        return null
      }
      if (campo.max !== undefined && num > campo.max) {
        toast.error('Valor fuera de rango', {
          description: `"${campo.label}" no puede ser mayor que ${campo.max}.`,
        })
        return null
      }
      datos[campo.key] = num
    }
    return datos
  }

  async function handlePredecir() {
    const datos = validar()
    if (!datos) return

    setPrediciendo(true)
    setResultado(null)
    try {
      const res = await predecir(datos)
      setResultado(res)
      toast.success('Predicción generada', {
        description: res.riesgo
          ? 'El solicitante presenta riesgo de incumplimiento.'
          : 'El solicitante no presenta riesgo.',
      })
    } catch (e) {
      const msg =
        e instanceof ApiError
          ? e.message
          : e instanceof TypeError
            ? 'No se pudo conectar con el backend. Verifica que el servidor de Python esté activo.'
            : 'No se pudo generar la predicción.'
      toast.error('Error en la predicción', { description: msg })
    } finally {
      setPrediciendo(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <UserSearch className="h-5 w-5 text-muted-foreground" aria-hidden="true" />
          <CardTitle>Predicción individual</CardTitle>
        </div>
        <CardDescription>
          Ingresa todos los parámetros del solicitante. El modelo devuelve una
          clasificación binaria de riesgo.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-5">
        {!habilitado && (
          <div className="flex items-center gap-3 rounded-lg border border-warning/40 bg-warning/10 px-4 py-3">
            <Lock className="h-4 w-4 text-warning" aria-hidden="true" />
            <p className="text-white">
              La predicción se habilita cuando el modelo ha sido entrenado y
              alcanza métricas adecuadas.
            </p>
          </div>
        )}

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {CAMPOS_SOLICITANTE.map((campo) => (
            <div key={campo.key} className="space-y-1.5">
              <Label htmlFor={campo.key} className="text-sm">
                {campo.label}
                {campo.unidad && (
                  <span className="ml-1 text-xs text-muted-foreground">
                    ({campo.unidad})
                  </span>
                )}
              </Label>
              <Input
                id={campo.key}
                type="number"
                inputMode="decimal"
                min={campo.min}
                max={campo.max}
                step={campo.step}
                placeholder={campo.placeholder}
                value={form[campo.key]}
                disabled={!habilitado}
                onChange={(e) => actualizar(campo.key, e.target.value)}
              />
              <p className="text-xs text-muted-foreground">{campo.descripcion}</p>
            </div>
          ))}
        </div>

        <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
          <Button
            onClick={handlePredecir}
            disabled={!habilitado || prediciendo}
            size="lg"
          >
            {prediciendo ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <UserSearch className="h-4 w-4" />
            )}
            Predecir riesgo
          </Button>

          {resultado && <ResultadoPrediccion resultado={resultado} />}
        </div>
      </CardContent>
    </Card>
  )
}

function ResultadoPrediccion({ resultado }: { resultado: PrediccionResult }) {
  const riesgo = resultado.riesgo
  return (
    <div
      role="status"
      aria-live="polite"
      className={`flex flex-1 items-center gap-3 rounded-lg border px-4 py-3 ${
        riesgo
          ? 'border-destructive/40 bg-destructive/10'
          : 'border-success/40 bg-success/10'
      }`}
    >
      {riesgo ? (
        <ShieldAlert className="h-6 w-6 shrink-0 text-destructive" aria-hidden="true" />
      ) : (
        <ShieldCheck className="h-6 w-6 shrink-0 text-success" aria-hidden="true" />
      )}
      <div>
        <p
          className={`font-semibold ${riesgo ? 'text-destructive' : 'text-success'}`}
        >
          {riesgo ? 'Presenta riesgo de incumplimiento' : 'No presenta riesgo'}
        </p>
        {typeof resultado.probabilidad === 'number' && (
          <p className="text-xs text-muted-foreground">
            Probabilidad de incumplimiento:{' '}
            <span className="font-mono">
              {(resultado.probabilidad * 100).toFixed(1)}%
            </span>
          </p>
        )}
      </div>
    </div>
  )
}
