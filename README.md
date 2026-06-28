# TalentMosaic - Portal de Segmentación de Freelancers y Reseñas de Clientes
Es una plataforma diseñada para segmentar perfiles de freelancers y agrupar reseñas de clientes utilizando técnicas de aprendizaje automático no supervisado (Clustering).

El proyecto se divide en dos componentes principales:
1. **Backend**: API construida con FastAPI (Python) que maneja el procesamiento de datos (limpieza y NLP), modelado (K-Means con PCA y SVD) y generación de reportes (PDF/CSV).
2. **Frontend**: Aplicación web desarrollada con Next.js (React y TypeScript) y estilizada con Tailwind CSS para proporcionar una interfaz de usuario interactiva y fluida.

---

## 📋 Requisitos del Sistema

Para ejecutar y compilar el proyecto localmente, asegúrate de contar con las siguientes herramientas instaladas:

*   **Sistema Operativo**: Windows, macOS o Linux.
*   **Python**: Versión `3.10` o superior.
*   **Node.js**: Versión `18.0.0` o superior (se recomienda la LTS activa).
*   **Gestor de Paquetes Node**: **pnpm** (versión 10+ recomendada) o alternativamente **npm**.

---

## ⚙️ Configuración e Instalación Paso a Paso

### 1. Clonar el repositorio
Si aún no estás dentro de la carpeta del proyecto, ábrelo en tu terminal:
```bash
cd Proyecto2
```

### 2. Configuración del Backend

Navega a la carpeta del Backend:
```bash
cd Backend
```

#### A. Crear un entorno virtual (Recomendado)
Es una buena práctica crear un entorno virtual para aislar las dependencias del backend:
*   **Windows (PowerShell)**:
    ```powershell
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    ```
*   **Windows (CMD)**:
    ```cmd
    python -m venv venv
    call venv\Scripts\activate.bat
    ```
*   **macOS / Linux**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

#### B. Instalar Dependencias
Una vez activado el entorno virtual, ejecuta:
```bash
pip install -r requirements.txt
```
*Las dependencias principales instaladas son:*
*   `fastapi==0.110.0` (Framework Web)
*   `uvicorn==0.28.0` (Servidor ASGI)
*   `python-multipart==0.0.9` (Soporte para carga de archivos)
*   `pandas==2.2.1` (Manipulación de datos)
*   `fpdf==1.7.2` (Generación de PDF)
*   `matplotlib==3.11.0` (Graficación de curvas y siluetas)
*   `scikit-learn` (Algoritmos de ML - KMeans, PCA, SVD, etc.)

#### C. Configurar Variables de Entorno
Copia el archivo de plantilla `.env.example` y renómbralo como `.env`:
```bash
copy .env.example .env     # Windows
cp .env.example .env       # macOS / Linux
```

---

### 3. Configuración del Frontend

Navega a la carpeta del Frontend:
```bash
cd ../Frontend
```

#### A. Instalar pnpm (si no está instalado)
El frontend utiliza `pnpm` por su rapidez y manejo eficiente del espacio en disco. Instálalo de forma global ejecutando:
```bash
npm install -g pnpm
```

#### B. Instalar Dependencias del Frontend
```bash
pnpm install
```
*(Si prefieres no instalar `pnpm`, puedes usar `npm install`, aunque se recomienda la consistencia con el archivo lock del repositorio).*

#### C. Configurar Conexión con la API del Backend
Crea un archivo `.env.local` en la raíz de la carpeta `Frontend/` con el siguiente contenido para indicarle la URL de la API:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```
*Nota: Si no creas este archivo, el frontend funcionará en **Modo Demo** con datos locales simulados (mock).*

---

## 🚀 Instrucciones para Ejecutar la Aplicación

Para utilizar la plataforma completa, debes iniciar tanto el Backend como el Frontend de manera simultánea (en terminales separadas).

### Ejecutar el Backend
Desde la carpeta `Proyecto2/Backend`, con el entorno virtual activado, ejecuta:
```bash
uvicorn main:app --reload
```
*   La API estará disponible en: **`http://localhost:8000`**
*   Documentación Interactiva (Swagger UI): **`http://localhost:8000/docs`**
*   Documentación ReDoc: **`http://localhost:8000/redoc`**

### Ejecutar el Frontend
Desde la carpeta `Proyecto2/Frontend`, ejecuta:
```bash
pnpm dev
```
*   La aplicación web estará disponible en: **`http://localhost:3000`**

---

## 📊 Formato y Columnas de Archivos CSV para Carga Masiva

La aplicación permite la carga masiva de datos en formato CSV para freelancers y reseñas de clientes. Los archivos deben respetar la siguiente estructura y tipos de datos exactos:

### 1. Archivo de Freelancers (`freelancers.csv`)
Este archivo contiene la información demográfica, de experiencia, tarifas e ingresos de los colaboradores.

| Nombre de Columna | Tipo de Dato | Descripción / Restricciones / Reglas de Limpieza |
| :--- | :--- | :--- |
| **`freelancer_id`** | Texto (String) | Identificador único del freelancer (ej. `FL0001`). No debe repetirse. |
| **`proyectos_completados`** | Entero (Int) | Número total de proyectos entregados. Los valores negativos son corregidos a su valor absoluto. Valores nulos o textos basura se imputan con la mediana del dataset. |
| **`ingresos_totales`** | Decimal (Float) | Ingresos totales del freelancer. Los valores nulos o con formato incorrecto se imputan con la mediana. |
| **`tarifa_hora_promedio`** | Decimal (Float) | Tarifa cobrada por hora. Nulos se imputan con la mediana. |
| **`anios_experiencia`** | Decimal (Float) | Años de experiencia en su profesión. Valores superiores a `50.0` se consideran errores de captura y se marcan como nulos para ser imputados con la mediana. |
| **`tiempo_respuesta_horas`** | Decimal (Float) | Tiempo promedio de respuesta en horas. Nulos se imputan con la mediana. |
| **`tasa_finalizacion`** | Decimal (Float) | Porcentaje de finalización de proyectos. Se acota obligatoriamente entre `0` y `100` (método clip). Nulos se imputan con la mediana. |
| **`calificacion_promedio`** | Decimal (Float) | Calificación promedio del freelancer. Se acota obligatoriamente entre `0.0` y `5.0` (método clip). Nulos se imputan con la mediana. |
| **`categoria_principal`** | Texto (String) | Área de especialidad (ej. `Desarrollo de Software`, `Diseño Gráfico`, `Marketing Digital`, `Redacción y Traducción`, `Soporte Administrativo Virtual`). |
| **`clientes_recurrentes`** | Entero (Int) | Cantidad de clientes habituales que posee. Nulos se imputan con la mediana. |
| **`horas_trabajadas_mes`** | Decimal (Float) | Total de horas trabajadas en el último mes. Nulos se imputan con la mediana. |

*Ejemplo de contenido:*
```csv
freelancer_id,proyectos_completados,ingresos_totales,tarifa_hora_promedio,anios_experiencia,tiempo_respuesta_horas,tasa_finalizacion,calificacion_promedio,categoria_principal,clientes_recurrentes,horas_trabajadas_mes
FL0001,42,73500.53,107.08,14.5,4.9,90.1,4.26,Desarrollo de Software,8,69.3
FL0002,37,4601.49,20.75,3.4,7.3,68.1,4.57,Diseño Gráfico,10,85.5
```

---

### 2. Archivo de Reseñas de Clientes (`reseñas_clientes.csv`)
Este archivo contiene las opiniones y retroalimentación que los clientes dejaron sobre los freelancers.

| Nombre de Columna | Tipo de Dato | Descripción / Restricciones / Reglas de Limpieza |
| :--- | :--- | :--- |
| **`reseña_id`** | Texto (String) | Identificador único de la reseña (ej. `RV00001`). |
| **`freelancer_id`** | Texto (String) | Identificador del freelancer asociado a la reseña. Actúa como llave foránea. |
| **`texto_reseña`** | Texto (String) | Opinión escrita por el cliente. Si falta (nulo), se conserva como `NaN` para evitar inventar texto y se omite únicamente del entrenamiento del NLP y clustering de texto. |
| **`fecha_reseña`** | Fecha (YYYY-MM-DD) | Fecha en la que se publicó la reseña. Si falta, se conserva como `NaN` y se excluye de gráficos de evolución temporal. |
| **`categoria_servicio`** | Texto (String) | Categoría del trabajo evaluado. Si está vacío (nulo), se reemplaza automáticamente por el término literal `"Sin categoría"`. |

*Ejemplo de contenido:*
```csv
reseña_id,freelancer_id,texto_reseña,fecha_reseña,categoria_servicio
RV00001,FL0001,"La comunicación fue lo que más valoro del trabajo realizado en este proyecto.",2020-06-06,Desarrollo de Software
RV00002,FL0001,"La calidad final fue buena aunque el proceso fue más largo de lo necesario.",2021-05-14,Desarrollo de Software
```
---

## 🛠️ Tecnologías Utilizadas en el Proyecto

### Backend
*   **FastAPI**: API REST rápida y moderna con validación de tipos basada en Pydantic.
*   **Uvicorn**: Servidor ASGI de alto rendimiento.
*   **Pandas**: Carga, manipulación y limpieza de los DataFrames.
*   **Scikit-Learn**:
    *   **K-Means**: Algoritmo de aprendizaje no supervisado principal para agrupar freelancers y reseñas.
    *   **PCA (Principal Component Analysis)**: Reducción a 2 dimensiones para la dispersión del perfil numérico de freelancers.
    *   **SVD (Truncated SVD)**: Reducción dimensional de matrices dispersas TF-IDF a 2 dimensiones para graficar reseñas.
    *   **TfidfVectorizer**: Vectorización de los textos en características numéricas.
*   **FPDF**: Motor de generación de reportes consolidados en formato PDF.

### Frontend
*   **Next.js (App Router)**: Renderizado y enrutamiento del lado del cliente/servidor.
*   **React 19 & TypeScript 5.7**: Estructuración segura de la interfaz de usuario.
*   **Tailwind CSS 4.0**: Estilos rápidos y responsivos con variables de tema modernas.
*   **Recharts**: Gráficas interactivas 2D (gráficos de dispersión para clusters, codos de inercia, etc.).
*   **shadcn/ui & Lucide Icons**: Biblioteca de componentes y set de íconos estilizados.

---

## 📁 Estructura General del Proyecto

```text
Proyecto2/
├── Backend/                    # Código del Backend (FastAPI + ML)
│   ├── app/
│   │   ├── ml/                 # Modelos de Machine Learning y NLP
│   │   ├── api.py              # Controladores y Endpoints de la API
│   │   ├── reports.py          # Generador de Reportes PDF/CSV
│   │   ├── schemas.py          # Validaciones de Datos (Pydantic)
│   │   └── state.py            # Singleton del Estado Global en memoria
│   ├── models_storage/         # Modelos serializados persistidos (.pkl)
│   ├── exports/                # Carpeta para reportes descargables
│   ├── main.py                 # Punto de entrada de la API
│   ├── requirements.txt        # Dependencias de Python
│   └── README.md               # Documentación específica del backend
│
├── Frontend/                   # Código del Frontend (Next.js + React)
│   ├── app/                    # Estructura de vistas y estilos Next.js
│   ├── components/             # Componentes modulares de UI y gráficas
│   ├── lib/                    # Cliente de API y funciones auxiliares
│   ├── package.json            # Dependencias y scripts de Node
│   └── README.md               # Documentación específica del frontend
│
└── Manuales/                   # Jupyter Notebooks y Documentos Técnicos
```

---

## ❓ Solución de Problemas Comunes

1. **Error de CORS en el Navegador**:
   Asegúrate de que el Backend esté corriendo en `http://localhost:8000` y que la variable `NEXT_PUBLIC_API_URL` esté correctamente declarada en el archivo `.env.local` del Frontend.
2. **Reinicio del Servidor del Backend y Pérdida de Datos**:
   El backend persistirá automáticamente los DataFrames entrenados en `models_storage/` (`freelancers_segmentado.pkl` y `resenas_segmentado.pkl`). Si el servidor se reinicia, los datos y modelos de clustering se recuperan al consultar el endpoint correspondiente sin requerir una recarga manual de los archivos.
3. **El puerto 3000 de Next.js está ocupado**:
   Si necesitas levantar la aplicación en otro puerto para evitar conflictos, ejecuta:
   ```bash
   pnpm dev -- -p 3001
   ```
