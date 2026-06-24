import { AppStateProvider } from "@/components/store"
import { AppShell } from "@/components/app-shell"

export default function Page() {
  return (
    <AppStateProvider>
      <AppShell />
    </AppStateProvider>
  )
}
