import { ShieldCheck } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { API_BASE_URL } from '@/lib/api'

export function DashboardHeader() {
  return (
    <header className="border-b border-border bg-card">
      <div className="mx-auto flex max-w-6xl flex-col gap-3 px-4 py-5 sm:flex-row sm:items-center sm:justify-between sm:px-6">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <ShieldCheck className="h-5 w-5" aria-hidden="true" />
          </div>
          <div>
            <h1 className="text-lg font-semibold leading-tight text-foreground">
              CreditGuard
            </h1>
            <p className="text-sm text-muted-foreground">
              Predicción de riesgo crediticio con aprendizaje supervisado
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="font-mono text-xs">
            API: {API_BASE_URL}
          </Badge>
        </div>
      </div>
    </header>
  )
}
