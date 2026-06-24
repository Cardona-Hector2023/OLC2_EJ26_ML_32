import { cn } from "@/lib/utils"
import type { Feedback } from "@/lib/types"
import {
  CircleCheck,
  CircleAlert,
  Info,
  TriangleAlert,
} from "lucide-react"

const config = {
  info: {
    icon: Info,
    cls: "border-primary/30 bg-primary/10 text-primary",
  },
  success: {
    icon: CircleCheck,
    cls: "border-emerald-500/30 bg-emerald-500/10 text-emerald-400",
  },
  warning: {
    icon: TriangleAlert,
    cls: "border-amber-500/30 bg-amber-500/10 text-amber-400",
  },
  error: {
    icon: CircleAlert,
    cls: "border-destructive/30 bg-destructive/10 text-destructive",
  },
} as const

export function FeedbackMessage({
  feedback,
  className,
}: {
  feedback: Feedback | null
  className?: string
}) {
  if (!feedback) return null
  const { icon: Icon, cls } = config[feedback.kind]
  return (
    <div
      role="status"
      className={cn(
        "flex items-start gap-2.5 rounded-lg border p-3 text-sm leading-relaxed",
        cls,
        className,
      )}
    >
      <Icon className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
      <span>{feedback.text}</span>
    </div>
  )
}
