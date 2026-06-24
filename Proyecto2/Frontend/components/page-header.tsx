import type { ReactNode } from "react"

export function PageHeader({
  step,
  title,
  description,
  actions,
}: {
  step: string
  title: string
  description: string
  actions?: ReactNode
}) {
  return (
    <header className="mb-8 flex flex-col gap-4 border-b border-border pb-6 sm:flex-row sm:items-end sm:justify-between">
      <div className="max-w-2xl">
        <p className="mb-1.5 text-xs font-semibold uppercase tracking-wider text-primary">
          {step}
        </p>
        <h1 className="font-heading text-2xl font-semibold tracking-tight text-balance">
          {title}
        </h1>
        <p className="mt-2 text-sm leading-relaxed text-muted-foreground text-pretty">
          {description}
        </p>
      </div>
      {actions && <div className="flex shrink-0 items-center gap-2">{actions}</div>}
    </header>
  )
}
