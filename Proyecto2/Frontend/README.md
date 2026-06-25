# TalentMosaic — Frontend

Frontend de la plataforma **TalentMosaic**, una aplicación web para segmentar freelancers y agrupar reseñas de clientes mediante técnicas de aprendizaje no supervisado (clustering).

---

## Tecnologías utilizadas

| Tecnología | Versión | Descripción |
|---|---|---|
| **Next.js** | 16.2.6 | Framework de React para aplicaciones web con renderizado del lado del servidor |
| **React** | 19 | Librería para construir interfaces de usuario |
| **TypeScript** | 5.7.3 | Superset de JavaScript con tipado estático |
| **Tailwind CSS** | 4.2 | Framework de CSS utilitario para estilos |
| **Recharts** | 3.9 | Librería de gráficas construida sobre D3 y React |
| **Lucide React** | 1.16+ | Íconos SVG como componentes de React |
| **shadcn/ui** | 4.8+ | Componentes de UI reutilizables (Button, Card, Badge, Field) |
| **pnpm** | 10+ | Gestor de paquetes (recomendado) |

---

## Prerrequisitos

Antes de comenzar, asegúrate de tener instalado lo siguiente en tu máquina:

### 1. Node.js (versión 18 o superior)

Descárgalo desde: https://nodejs.org/

Para verificar que lo tienes instalado, abre una terminal y ejecuta:

```bash
node --version
```

Deberías ver algo como `v18.x.x`, `v20.x.x` o superior.

### 2. pnpm (gestor de paquetes)

Este proyecto usa **pnpm** en lugar de npm. Para instalarlo globalmente:

```bash
npm install -g pnpm
```

Para verificar la instalación:

```bash
pnpm --version
```

> **Nota:** Si prefieres no instalar pnpm, puedes usar `npm` como alternativa, pero se recomienda pnpm para mantener consistencia con el `pnpm-lock.yaml`.

---

## Cómo ejecutar el proyecto

### 1. Clonar o descargar el repositorio

Si aún no tienes el proyecto, clónalo o descárgalo y navega a la carpeta del frontend:

```bash
cd Proyecto2/Frontend
```

### 2. Instalar las dependencias

```bash
pnpm install
```

Esto descargará todas las librerías necesarias definidas en `package.json`. Solo necesitas hacer esto **la primera vez** o cuando se agreguen nuevas dependencias.

### 3. Iniciar el servidor de desarrollo

```bash
pnpm dev
```

Esto levantará el servidor en modo desarrollo. Verás un mensaje como:

```
▲ Next.js 16.2.6 (Turbopack)
- Local:    http://localhost:3000
✓ Ready in ~1s
```

### 4. Abrir en el navegador

Abre tu navegador y visita:

```
http://localhost:3000
```

---

## Conexión con el Backend

El frontend se conecta a un backend de **FastAPI** mediante la variable de entorno `NEXT_PUBLIC_API_URL`.

- **Sin backend:** La app funciona en **modo demo** con datos simulados (mock). No necesitas el backend para navegar la interfaz.
- **Con backend:** Crea un archivo `.env.local` en la raíz del frontend con el siguiente contenido:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Luego reinicia el servidor de desarrollo (`Ctrl+C` y `pnpm dev`).

---

## Scripts disponibles

| Comando | Descripción |
|---|---|
| `pnpm dev` | Inicia el servidor de desarrollo en `localhost:3000` |
| `pnpm build` | Genera la build de producción |
| `pnpm start` | Sirve la build de producción |
| `pnpm lint` | Ejecuta ESLint para revisar errores de código |

---

## Estructura del proyecto

```
Frontend/
├── app/                    # Páginas y layout de Next.js
│   ├── globals.css         # Variables de tema y estilos globales
│   ├── layout.tsx          # Layout raíz (fuentes, metadata)
│   └── page.tsx            # Página principal
├── components/             # Componentes de React
│   ├── app-shell.tsx       # Sidebar + navegación principal
│   ├── data-table.tsx      # Tabla de datos genérica
│   ├── feedback-message.tsx# Mensajes de estado (éxito, error, etc.)
│   ├── page-header.tsx     # Encabezado de cada vista
│   ├── store.tsx           # Estado global (Context API)
│   ├── charts/             # Componentes de gráficas
│   │   └── scatter-chart.tsx
│   ├── ui/                 # Componentes base de UI
│   │   ├── badge.tsx
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   └── field.tsx
│   └── views/              # Vistas principales de la app
│       ├── carga-view.tsx          # 1. Carga de datos
│       ├── entrenamiento-view.tsx  # 2. Entrenamiento de modelos
│       ├── segmentos-view.tsx      # 3. Exploración de segmentos
│       ├── evaluacion-view.tsx     # 4. Métricas de evaluación
│       ├── clasificacion-view.tsx  # 5. Clasificación de nuevos datos
│       └── exportacion-view.tsx    # 6. Exportación de reportes
├── lib/                    # Utilidades y lógica
│   ├── api.ts              # Cliente HTTP para el backend
│   ├── mock-data.ts        # Datos simulados (modo demo)
│   ├── types.ts            # Tipos e interfaces de TypeScript
│   └── utils.ts            # Utilidades generales
├── public/                 # Archivos estáticos
│   └── Icono.png           # Favicon de la app
├── package.json            # Dependencias y scripts
├── pnpm-lock.yaml          # Lockfile de dependencias exactas
├── next.config.mjs         # Configuración de Next.js
├── postcss.config.mjs      # Configuración de PostCSS
└── tsconfig.json           # Configuración de TypeScript
```

---

## Solución de problemas comunes

### El puerto 3000 ya está en uso

Si otro proceso está usando el puerto 3000, puedes usar otro puerto:

```bash
pnpm dev -- -p 3001
```

### Error al instalar dependencias

Si `pnpm install` falla, intenta eliminar la carpeta `node_modules` y el lockfile:

```bash
Remove-Item -Recurse -Force node_modules
pnpm install
```