import type {
  Freelancer,
  Resena,
  CsvPreview,
  SegmentsResponse,
  CrossTab,
  EvaluationMetrics,
  DatasetKey,
} from "./types"

const CATEGORIAS = [
  "Desarrollo de Software",
  "Diseño Gráfico",
  "Redacción y Traducción",
  "Marketing Digital",
  "Soporte Administrativo Virtual",
]

const TEXTOS_RESENA = [
  "Entregó el proyecto antes de lo esperado y con excelente calidad.",
  "La comunicación fue lenta pero el resultado final fue bueno.",
  "Muy profesional, volvería a contratarlo sin dudarlo.",
  "El trabajo tuvo varios errores que hubo que corregir después.",
  "Cumplió con todos los requisitos y fue muy atento al detalle.",
  "Precio razonable y entrega puntual, recomendado.",
  "No respetó los tiempos acordados, tuve que insistir varias veces.",
  "Gran capacidad técnica y disposición para resolver dudas.",
]

function rnd(min: number, max: number, dec = 0) {
  const v = Math.random() * (max - min) + min
  return dec === 0 ? Math.round(v) : Number(v.toFixed(dec))
}

export function generateFreelancers(n = 60): Freelancer[] {
  return Array.from({ length: n }, (_, i) => ({
    freelancer_id: `FL-${String(i + 1).padStart(4, "0")}`,
    proyectos_completados: rnd(3, 320),
    ingresos_totales: rnd(800, 220000),
    tarifa_hora_promedio: rnd(8, 140),
    anios_experiencia: rnd(0, 18),
    tiempo_respuesta_horas: rnd(1, 48, 1),
    tasa_finalizacion: rnd(55, 100),
    calificacion_promedio: rnd(2.8, 5, 1),
    categoria_principal: CATEGORIAS[rnd(0, CATEGORIAS.length - 1)],
    clientes_recurrentes: rnd(0, 80),
    horas_trabajadas_mes: rnd(20, 220),
  }))
}

export function generateResenas(n = 90): Resena[] {
  return Array.from({ length: n }, (_, i) => {
    const texto = TEXTOS_RESENA[rnd(0, TEXTOS_RESENA.length - 1)]
    return {
      resena_id: `RV-${String(i + 1).padStart(4, "0")}`,
      freelancer_id: `FL-${String(rnd(1, 60)).padStart(4, "0")}`,
      texto_resena: texto,
      fecha_resena: `2025-${String(rnd(1, 12)).padStart(2, "0")}-${String(rnd(1, 28)).padStart(2, "0")}`,
      categoria_servicio: CATEGORIAS[rnd(0, CATEGORIAS.length - 1)],
      longitud_resena: texto.split(" ").length,
    }
  })
}

export function toPreview(
  rows: Record<string, string | number>[],
  limit = 8,
): CsvPreview {
  const columns = rows.length > 0 ? Object.keys(rows[0]) : []
  return {
    columns,
    rows: rows.slice(0, limit),
    totalRows: rows.length,
  }
}

export const mockFreelancersPreview = toPreview(
  generateFreelancers(12) as unknown as Record<string, string | number>[],
)
export const mockResenasPreview = toPreview(
  generateResenas(12) as unknown as Record<string, string | number>[],
)

// ---- Segmentos simulados ----

function buildScatter(segCount: number, perSeg: number, prefix: string) {
  const points = []
  for (let s = 0; s < segCount; s++) {
    const cx = rnd(-6, 6, 2)
    const cy = rnd(-6, 6, 2)
    for (let p = 0; p < perSeg; p++) {
      points.push({
        x: cx + rnd(-150, 150) / 100,
        y: cy + rnd(-150, 150) / 100,
        segmento: s,
        id: `${prefix}-${s}-${p}`,
      })
    }
  }
  return points
}

export function mockSegments(dataset: DatasetKey): SegmentsResponse {
  if (dataset === "freelancers") {
    return {
      dataset,
      scatter: buildScatter(4, 14, "FL"),
      resumen: [
        {
          segmento: 0,
          registros: 18,
          descripcion:
            "Profesionales de alto rendimiento: tarifas elevadas, gran experiencia y excelentes calificaciones.",
          caracteristicas: {
            proyectos_completados: 210,
            ingresos_totales: 168000,
            tarifa_hora_promedio: 98,
            anios_experiencia: 12,
            tasa_finalizacion: 96,
            calificacion_promedio: 4.8,
            categoria_principal: "Desarrollo de Software",
          },
        },
        {
          segmento: 1,
          registros: 22,
          descripcion:
            "Freelancers en crecimiento: actividad media, buenas calificaciones y tarifas moderadas.",
          caracteristicas: {
            proyectos_completados: 88,
            ingresos_totales: 42000,
            tarifa_hora_promedio: 45,
            anios_experiencia: 5,
            tasa_finalizacion: 89,
            calificacion_promedio: 4.3,
            categoria_principal: "Diseño Gráfico",
          },
        },
        {
          segmento: 2,
          registros: 12,
          descripcion:
            "Nuevos en la plataforma: pocos proyectos, baja experiencia y tiempos de respuesta más largos.",
          caracteristicas: {
            proyectos_completados: 19,
            ingresos_totales: 6800,
            tarifa_hora_promedio: 22,
            anios_experiencia: 1,
            tasa_finalizacion: 74,
            calificacion_promedio: 3.6,
            categoria_principal: "Soporte Administrativo Virtual",
          },
        },
        {
          segmento: 3,
          registros: 8,
          descripcion:
            "Perfiles de alto volumen: muchas horas trabajadas pero calificaciones variables.",
          caracteristicas: {
            proyectos_completados: 140,
            ingresos_totales: 71000,
            tarifa_hora_promedio: 38,
            anios_experiencia: 7,
            tasa_finalizacion: 83,
            calificacion_promedio: 4.0,
            categoria_principal: "Marketing Digital",
          },
        },
      ],
    }
  }

  return {
    dataset,
    scatter: buildScatter(3, 18, "RV"),
    resumen: [
      {
        segmento: 0,
        registros: 38,
        descripcion:
          "Reseñas muy positivas: destacan la calidad, profesionalismo y puntualidad.",
        caracteristicas: { longitud_promedio: 14, sentimiento: "Positivo" },
        terminos: [
          { termino: "excelente", peso: 0.92 },
          { termino: "profesional", peso: 0.81 },
          { termino: "recomendado", peso: 0.77 },
          { termino: "calidad", peso: 0.71 },
          { termino: "puntual", peso: 0.64 },
        ],
      },
      {
        segmento: 1,
        registros: 31,
        descripcion:
          "Reseñas neutrales centradas en comunicación, tiempos y precio.",
        caracteristicas: { longitud_promedio: 11, sentimiento: "Neutral" },
        terminos: [
          { termino: "comunicación", peso: 0.85 },
          { termino: "tiempo", peso: 0.74 },
          { termino: "precio", peso: 0.69 },
          { termino: "entrega", peso: 0.6 },
          { termino: "razonable", peso: 0.55 },
        ],
      },
      {
        segmento: 2,
        registros: 21,
        descripcion:
          "Reseñas críticas: mencionan errores, retrasos y necesidad de correcciones.",
        caracteristicas: { longitud_promedio: 13, sentimiento: "Negativo" },
        terminos: [
          { termino: "errores", peso: 0.88 },
          { termino: "retraso", peso: 0.8 },
          { termino: "corregir", peso: 0.72 },
          { termino: "insistir", peso: 0.61 },
          { termino: "lento", peso: 0.58 },
        ],
      },
    ],
  }
}

export const mockCrossTab: CrossTab = {
  filas: [0, 1, 2, 3],
  columnas: [0, 1, 2],
  celdas: [
    [
      { cantidad: 22, porcentaje: 73 },
      { cantidad: 6, porcentaje: 20 },
      { cantidad: 2, porcentaje: 7 },
    ],
    [
      { cantidad: 14, porcentaje: 47 },
      { cantidad: 11, porcentaje: 37 },
      { cantidad: 5, porcentaje: 16 },
    ],
    [
      { cantidad: 4, porcentaje: 22 },
      { cantidad: 6, porcentaje: 33 },
      { cantidad: 8, porcentaje: 45 },
    ],
    [
      { cantidad: 9, porcentaje: 41 },
      { cantidad: 7, porcentaje: 32 },
      { cantidad: 6, porcentaje: 27 },
    ],
  ],
}

export function mockEvaluation(dataset: DatasetKey): EvaluationMetrics {
  const base = dataset === "freelancers"
  return {
    dataset,
    silhouette: base ? 0.62 : 0.48,
    daviesBouldin: base ? 0.74 : 0.95,
    calinskiHarabasz: base ? 318.5 : 184.2,
    interpretacion: base
      ? "El coeficiente de silueta (0.62) indica clusters bien definidos y razonablemente separados. El índice de Davies-Bouldin bajo (0.74) confirma buena cohesión interna y separación entre grupos."
      : "El coeficiente de silueta (0.48) sugiere cierto traslape entre los grupos temáticos de reseñas, algo esperable en datos textuales. Aún así, los segmentos son interpretables.",
    curva: Array.from({ length: 8 }, (_, i) => {
      const k = i + 2
      return {
        k,
        inercia: Math.round(5200 / k + rnd(0, 120)),
        silhouette: Number((0.7 - Math.abs(k - (base ? 4 : 3)) * 0.06).toFixed(2)),
      }
    }),
  }
}
