# CreditGuard

CreditGuard es una aplicación web para la predicción de riesgo crediticio basada en aprendizaje supervisado. El proyecto se compone de un backend en FastAPI encargado de cargar, limpiar, entrenar y predecir, y un frontend en Next.js que permite interactuar con el modelo desde una interfaz web.

## Requisitos del Sistema

- Python 3.11 o superior.
- Node.js 20 o superior.
- pnpm para el frontend.
- Git, si se desea clonar el repositorio desde un control de versiones.

## Estructura General

- `Proyecto1/Backend`: API en FastAPI y lógica de procesamiento de datos y modelo.
- `Proyecto1/Frontend`: interfaz web en Next.js.
- `Proyecto1/Manuales`: documentación técnica y de usuario.

## Instalación del Backend

1. Abrir una terminal en `Proyecto1/Backend`.
2. Crear y activar un entorno virtual de Python.
3. Instalar las dependencias del backend.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Instalación del Frontend

1. Abrir una terminal en `Proyecto1/Frontend`.
2. Instalar las dependencias del frontend con pnpm.

```bash
pnpm install
```

## Ejecución de la Aplicación

1. Iniciar el backend.

```bash
cd Proyecto1/Backend
uvicorn app.main:app --reload
```

2. Iniciar el frontend en otra terminal.

```bash
cd Proyecto1/Frontend
pnpm dev
```

3. Abrir la aplicación en el navegador desde la URL que indique Next.js, normalmente `http://localhost:3000`.
4. Confirmar que el backend esté disponible en `http://localhost:8000`.

## Formato del Archivo CSV de Carga Masiva

El archivo CSV debe incluir exactamente estas columnas:

- `ingresos_mensuales`
- `deuda_activa`
- `historial_pagos`
- `antiguedad_laboral`
- `creditos_activos`
- `monto_solicitado`
- `atrasos_previos`
- `dependientes_economicos`
- `utilizacion_credito`
- `en_riesgo`

## Notas Importantes

- El CSV debe ser un archivo `.csv` válido y legible por pandas.
- La columna `en_riesgo` es la variable objetivo usada para entrenar el modelo.
- Las columnas numéricas deben mantener un formato consistente con el esquema esperado por el backend.
- Si falta alguna de las columnas requeridas, la carga será rechazada por la API.

## Resumen del Flujo

1. Cargar el CSV en el backend.
2. Ejecutar la limpieza de datos.
3. Entrenar el modelo.
4. Revisar métricas y ajustar hiperparámetros si es necesario.
5. Realizar predicciones individuales para nuevos solicitantes.

## Tecnologías Usadas

- Backend: FastAPI, Python, pandas, scikit-learn.
- Frontend: Next.js, React, TypeScript, Tailwind CSS.
