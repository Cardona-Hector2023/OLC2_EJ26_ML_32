import type { SolicitanteInput } from './types'

export interface CampoConfig {
  key: keyof SolicitanteInput
  label: string
  descripcion: string
  unidad?: string
  min?: number
  max?: number
  step?: number
  placeholder: string
}

// Las 9 variables que evalúa CreditGuard, según el enunciado del proyecto.
export const CAMPOS_SOLICITANTE: CampoConfig[] = [
  {
    key: 'ingresos_mensuales',
    label: 'Ingresos mensuales',
    descripcion: 'Ingreso mensual del solicitante',
    unidad: 'Q',
    min: 0,
    step: 0.01,
    placeholder: '8500.00',
  },
  {
    key: 'deuda_activa',
    label: 'Deuda activa',
    descripcion: 'Monto total de deuda activa',
    unidad: 'Q',
    min: 0,
    step: 0.01,
    placeholder: '12000.00',
  },
  {
    key: 'historial_pagos',
    label: 'Historial de pagos',
    descripcion: 'Puntaje de historial de pagos (0 a 100)',
    min: 0,
    max: 100,
    step: 1,
    placeholder: '85',
  },
  {
    key: 'antiguedad_laboral',
    label: 'Antigüedad laboral',
    descripcion: 'Años de antigüedad laboral',
    unidad: 'años',
    min: 0,
    step: 0.5,
    placeholder: '4',
  },
  {
    key: 'creditos_activos',
    label: 'Créditos activos',
    descripcion: 'Número de créditos activos simultáneos',
    min: 0,
    step: 1,
    placeholder: '2',
  },
  {
    key: 'monto_solicitado',
    label: 'Monto solicitado',
    descripcion: 'Monto del crédito solicitado',
    unidad: 'Q',
    min: 0,
    step: 0.01,
    placeholder: '25000.00',
  },
  {
    key: 'atrasos_previos',
    label: 'Atrasos previos',
    descripcion: 'Atrasos registrados en los últimos 12 meses',
    min: 0,
    step: 1,
    placeholder: '1',
  },
  {
    key: 'dependientes_economicos',
    label: 'Dependientes económicos',
    descripcion: 'Número de dependientes económicos',
    min: 0,
    step: 1,
    placeholder: '3',
  },
  {
    key: 'utilizacion_credito',
    label: 'Utilización del crédito',
    descripcion: 'Porcentaje de utilización del límite disponible (0 a 100)',
    unidad: '%',
    min: 0,
    max: 100,
    step: 1,
    placeholder: '45',
  },
]
