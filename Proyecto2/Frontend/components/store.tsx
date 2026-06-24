"use client"

import { createContext, useContext, useState, type ReactNode } from "react"
import type { CsvPreview, TrainResult, DatasetKey } from "@/lib/types"

interface AppState {
  freelancersPreview: CsvPreview | null
  resenasPreview: CsvPreview | null
  cleaned: boolean
  trained: Record<DatasetKey, TrainResult | null>
  setFreelancersPreview: (p: CsvPreview | null) => void
  setResenasPreview: (p: CsvPreview | null) => void
  setCleaned: (v: boolean) => void
  setTrained: (dataset: DatasetKey, result: TrainResult | null) => void
}

const AppStateContext = createContext<AppState | null>(null)

export function AppStateProvider({ children }: { children: ReactNode }) {
  const [freelancersPreview, setFreelancersPreview] =
    useState<CsvPreview | null>(null)
  const [resenasPreview, setResenasPreview] = useState<CsvPreview | null>(null)
  const [cleaned, setCleaned] = useState(false)
  const [trained, setTrainedState] = useState<
    Record<DatasetKey, TrainResult | null>
  >({
    freelancers: null,
    resenas: null,
  })

  const setTrained = (dataset: DatasetKey, result: TrainResult | null) =>
    setTrainedState((prev) => ({ ...prev, [dataset]: result }))

  return (
    <AppStateContext.Provider
      value={{
        freelancersPreview,
        resenasPreview,
        cleaned,
        trained,
        setFreelancersPreview,
        setResenasPreview,
        setCleaned,
        setTrained,
      }}
    >
      {children}
    </AppStateContext.Provider>
  )
}

export function useAppState() {
  const ctx = useContext(AppStateContext)
  if (!ctx)
    throw new Error("useAppState debe usarse dentro de AppStateProvider")
  return ctx
}
