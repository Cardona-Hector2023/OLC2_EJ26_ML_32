import type { CsvPreview } from "@/lib/types"

export function DataTable({ preview }: { preview: CsvPreview }) {
  return (
    <div className="overflow-hidden rounded-lg border border-border">
      <div className="max-h-80 overflow-auto">
        <table className="w-full border-collapse text-sm">
          <thead className="sticky top-0 z-10 bg-muted">
            <tr>
              {preview.columns.map((col) => (
                <th
                  key={col}
                  className="whitespace-nowrap border-b border-border px-3 py-2 text-left font-medium text-muted-foreground"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {preview.rows.map((row, i) => (
              <tr key={i} className="even:bg-muted/30">
                {preview.columns.map((col) => (
                  <td
                    key={col}
                    className="whitespace-nowrap border-b border-border/60 px-3 py-2 text-foreground/90"
                  >
                    {String(row[col] ?? "")}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="border-t border-border bg-card px-3 py-2 text-xs text-muted-foreground">
        Mostrando {preview.rows.length} de {preview.totalRows} filas
      </div>
    </div>
  )
}
