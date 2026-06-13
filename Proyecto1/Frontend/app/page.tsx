'use client'

import { useState } from 'react'
import { Database, Brain, UserSearch } from 'lucide-react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { DashboardHeader } from '@/components/dashboard-header'
import { PipelineDatos } from '@/components/pipeline-datos'
import { PanelMetricas } from '@/components/panel-metricas'
import { AjusteHiperparametros } from '@/components/ajuste-hiperparametros'
import { FormularioPrediccion } from '@/components/formulario-prediccion'
import type {
  EntrenamientoResult,
  Hiperparametros,
  Metricas,
} from '@/lib/types'

const HPARAMS_INICIALES: Hiperparametros = {
  n_arboles: 100,
  profundidad_maxima: 10,
  hojas_maximas: 32,
}

export default function Page() {
  const [metricas, setMetricas] = useState<Metricas | null>(null)
  const [resultadoEntrenamiento, setResultadoEntrenamiento] = useState<EntrenamientoResult | null>(null)
  const [modeloEntrenado, setModeloEntrenado] = useState(false)
  const [hiperparametros, setHiperparametros] =
    useState<Hiperparametros>(HPARAMS_INICIALES)

  function handleEntrenado(m: Metricas, res: EntrenamientoResult) {
    setMetricas(m)
    setResultadoEntrenamiento(res)
    setModeloEntrenado(true)
    if (res.hiperparametros) setHiperparametros(res.hiperparametros)
  }

  return (
    <main className="min-h-svh bg-background">
      <DashboardHeader />

      <div className="mx-auto max-w-6xl px-4 py-6 sm:px-6 sm:py-8">
        <Tabs defaultValue="datos" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="datos" className="gap-2">
              <Database className="h-4 w-4" />
              <span className="hidden sm:inline">Datos y entrenamiento</span>
              <span className="sm:hidden">Datos</span>
            </TabsTrigger>
            <TabsTrigger value="modelo" className="gap-2">
              <Brain className="h-4 w-4" />
              <span className="hidden sm:inline">Rendimiento y ajuste</span>
              <span className="sm:hidden">Modelo</span>
            </TabsTrigger>
            <TabsTrigger value="prediccion" className="gap-2">
              <UserSearch className="h-4 w-4" />
              <span className="hidden sm:inline">Predicción</span>
              <span className="sm:hidden">Predecir</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="datos">
            <PipelineDatos onModeloEntrenado={handleEntrenado} />
          </TabsContent>

          <TabsContent value="modelo" className="space-y-6">
            <PanelMetricas resultado={resultadoEntrenamiento} />
            <AjusteHiperparametros
              modeloEntrenado={modeloEntrenado}
              hiperparametros={hiperparametros}
              metricasActuales={metricas}
              onReentrenado={handleEntrenado}
            />
          </TabsContent>

          <TabsContent value="prediccion">
            <FormularioPrediccion habilitado={modeloEntrenado} />
          </TabsContent>
        </Tabs>
      </div>
    </main>
  )
}
