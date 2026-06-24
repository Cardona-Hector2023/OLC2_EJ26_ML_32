"use client"

import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts"
import type { ScatterPoint } from "@/lib/types"

const CLUSTER_COLORS = [
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
]

export function clusterColor(i: number) {
  return CLUSTER_COLORS[i % CLUSTER_COLORS.length]
}

export function SegmentScatter({ points }: { points: ScatterPoint[] }) {
  const segmentos = [...new Set(points.map((p) => p.segmento))].sort(
    (a, b) => a - b,
  )

  return (
    <ResponsiveContainer width="100%" height={360}>
      <ScatterChart margin={{ top: 10, right: 16, bottom: 20, left: 0 }}>
        <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" />
        <XAxis
          type="number"
          dataKey="x"
          name="Componente 1"
          tick={{ fill: "var(--muted-foreground)", fontSize: 12 }}
          stroke="var(--border)"
          label={{
            value: "Componente principal 1 (PCA)",
            position: "insideBottom",
            offset: -10,
            fill: "var(--muted-foreground)",
            fontSize: 12,
          }}
        />
        <YAxis
          type="number"
          dataKey="y"
          name="Componente 2"
          tick={{ fill: "var(--muted-foreground)", fontSize: 12 }}
          stroke="var(--border)"
          label={{
            value: "Componente 2",
            angle: -90,
            position: "insideLeft",
            fill: "var(--muted-foreground)",
            fontSize: 12,
          }}
        />
        <Tooltip
          cursor={{ strokeDasharray: "3 3", stroke: "var(--muted-foreground)" }}
          contentStyle={{
            background: "var(--popover)",
            border: "1px solid var(--border)",
            borderRadius: 8,
            color: "var(--popover-foreground)",
            fontSize: 12,
          }}
        />
        <Legend
          wrapperStyle={{ fontSize: 12, color: "var(--muted-foreground)" }}
        />
        {segmentos.map((seg) => (
          <Scatter
            key={seg}
            name={`Segmento ${seg}`}
            data={points.filter((p) => p.segmento === seg)}
            fill={clusterColor(seg)}
            fillOpacity={0.8}
          />
        ))}
      </ScatterChart>
    </ResponsiveContainer>
  )
}
