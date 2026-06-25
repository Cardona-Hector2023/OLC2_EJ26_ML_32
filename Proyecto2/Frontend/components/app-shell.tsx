"use client"

import { useState } from "react"
import { cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"
import { useAppState } from "@/components/store"
import {
  Upload,
  Cpu,
  LayoutGrid,
  Gauge,
  UserPlus,
  Download,
  Boxes,
  Lock,
} from "lucide-react"
import type { LucideIcon } from "lucide-react"

import { CargaView } from "@/components/views/carga-view"
import { EntrenamientoView } from "@/components/views/entrenamiento-view"
import { SegmentosView } from "@/components/views/segmentos-view"
import { EvaluacionView } from "@/components/views/evaluacion-view"
import { ClasificacionView } from "@/components/views/clasificacion-view"
import { ExportacionView } from "@/components/views/exportacion-view"

type ViewId =
  | "carga"
  | "entrenamiento"
  | "segmentos"
  | "evaluacion"
  | "clasificacion"
  | "exportacion"

interface NavItem {
  id: ViewId
  label: string
  short: string
  icon: LucideIcon
}

const NAV: NavItem[] = [
  { id: "carga", label: "Carga de Datos", short: "1", icon: Upload },
  { id: "entrenamiento", label: "Entrenamiento", short: "2", icon: Cpu },
  { id: "segmentos", label: "Segmentos", short: "3", icon: LayoutGrid },
  { id: "evaluacion", label: "Evaluación", short: "4", icon: Gauge },
  { id: "clasificacion", label: "Clasificación", short: "5", icon: UserPlus },
  { id: "exportacion", label: "Exportación", short: "6", icon: Download },
]

export function AppShell() {
  const [active, setActive] = useState<ViewId>("carga")
  const { trained } = useAppState()

  const algunModelo = Boolean(trained.freelancers || trained.resenas)

  // Vistas que requieren al menos un modelo entrenado (según las Notas).
  const requiereModelo: Record<ViewId, boolean> = {
    carga: false,
    entrenamiento: false,
    segmentos: true,
    evaluacion: true,
    clasificacion: true,
    exportacion: true,
  }

  return (
    <div className="flex min-h-screen bg-background">
      {/* Sidebar */}
      <aside className="sticky top-0 flex h-screen w-64 shrink-0 flex-col border-r border-sidebar-border bg-sidebar">
        <div className="flex items-center gap-2.5 px-5 py-5">
          <div className="flex size-9 items-center justify-center rounded-lg bg-primary/15 text-primary">
            <Boxes className="size-5" />
          </div>
          <div>
            <p className="font-heading text-sm font-semibold leading-none text-sidebar-foreground">
              TalentMosaic
            </p>
            <p className="mt-1 text-xs text-muted-foreground">
              Aprendizaje no supervisado
            </p>
          </div>
        </div>

        <nav className="flex flex-1 flex-col gap-1 px-3 py-2">
          {NAV.map((item) => {
            const locked = requiereModelo[item.id] && !algunModelo
            const isActive = active === item.id
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => !locked && setActive(item.id)}
                disabled={locked}
                aria-current={isActive ? "page" : undefined}
                className={cn(
                  "group flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-sidebar-accent text-sidebar-foreground"
                    : "text-muted-foreground hover:bg-sidebar-accent/60 hover:text-sidebar-foreground",
                  locked && "cursor-not-allowed opacity-45 hover:bg-transparent",
                )}
                title={
                  locked
                    ? "Entrena al menos un modelo para habilitar esta vista"
                    : undefined
                }
              >
                <span
                  className={cn(
                    "flex size-6 shrink-0 items-center justify-center rounded-md text-[11px] font-semibold",
                    isActive
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted text-muted-foreground",
                  )}
                >
                  {item.short}
                </span>
                <item.icon className="size-4 shrink-0" />
                <span className="flex-1 text-left">{item.label}</span>
                {locked && <Lock className="size-3.5 shrink-0" />}
              </button>
            )
          })}
        </nav>

        <div className="border-t border-sidebar-border px-5 py-4">
          <Badge variant="success" className="w-full justify-center">
            Backend conectado
          </Badge>
          <p className="mt-2 text-center text-[11px] leading-relaxed text-muted-foreground">
            {process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}
          </p>
        </div>
      </aside>

      {/* Contenido */}
      <main className="flex-1 overflow-x-hidden">
        <div className="mx-auto max-w-6xl px-6 py-8 lg:px-10">
          {active === "carga" && <CargaView />}
          {active === "entrenamiento" && <EntrenamientoView />}
          {active === "segmentos" && <SegmentosView />}
          {active === "evaluacion" && <EvaluacionView />}
          {active === "clasificacion" && <ClasificacionView />}
          {active === "exportacion" && <ExportacionView />}
        </div>
      </main>
    </div>
  )
}
