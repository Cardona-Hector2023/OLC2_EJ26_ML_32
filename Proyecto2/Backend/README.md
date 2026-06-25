# TalentMosaic API - Backend 🚀

Este directorio contiene el **Backend** de la aplicación **TalentMosaic**, desarrollado con **FastAPI** y **Python**. Está diseñado para gestionar la carga de datos de freelancers y sus reseñas, ejecutar procesos de Limpieza y Procesamiento de Lenguaje Natural (NLP), y entrenar modelos de Clustering para agrupar y analizar perfiles de freelancers.

---

## 📂 Estructura del Proyecto

A continuación se detalla la estructura simplificada y limpia del backend:

```text
backend/
├── app/
│   ├── __init__.py
│   ├── api.py                    # Rutas y Endpoints de la API (Carga, Limpieza, Clustering)
│   ├── config.py                 # Configuración global del backend (variables de entorno)
│   ├── reports.py                # Lógica para la generación de reportes consolidados
│   ├── schemas.py                # Modelos Pydantic para validación y tipado de datos de la API
│   ├── state.py                  # Estado en memoria para almacenar DataFrames y datos procesados
│   │
│   └── ml/                       # Módulos de Procesamiento y Aprendizaje Automático (Machine Learning)
│       ├── __init__.py
│       ├── preprocessor.py       # Limpieza de datos estructurados, manejo de nulos y escalado
│       ├── nlp.py                # Procesamiento de lenguaje natural (limpieza y vectorización de reseñas)
│       ├── clustering.py         # Algoritmos de clustering (ej. K-Means, inicialización de centroides)
│       └── evaluation.py         # Métricas de evaluación (ej. Coeficiente de Silueta, Inercia)
│
├── models_storage/               # Directorio para almacenar modelos y vectorizadores serializados (.pkl)
├── uploads/                      # Directorio para almacenamiento opcional de archivos CSV subidos
├── .env.example                  # Plantilla de ejemplo para variables de entorno locales
├── .gitignore                    # Especifica qué archivos y carpetas debe ignorar Git (ej. entornos virtuales, .env)
├── main.py                       # Punto de entrada de la aplicación. Configura FastAPI, CORS e inicia Uvicorn
├── requirements.txt              # Archivo con la lista de dependencias y librerías del proyecto
└── README.md                     # Este archivo de documentación
```

---

## 🛠️ Descripción detallada de Archivos y Carpetas

### Directorio Raíz
*   **main.py**: Es el punto de inicio de la aplicación. Configura FastAPI, inicializa el middleware de CORS para permitir la comunicación segura con el Frontend en React/Next.js y arranca el servidor web local **Uvicorn** cuando ejecutas `python main.py`.
*   **models_storage/**: Carpeta creada para almacenar los modelos de Machine Learning (como clusters de K-Means) o transformadores (como TF-IDF) entrenados. De esta forma, se guardan en formato `.pkl` (pickle) para cargarse al instante en producción sin necesidad de entrenarlos de nuevo.
*   **uploads/**: Carpeta destinada a guardar los archivos `.csv` subidos si se requiere un almacenamiento local o auditoría de archivos recibidos.
*   **.env.example**: Plantilla que muestra qué variables de entorno necesita la aplicación (ej. puertos de red, claves secretas) sin exponer datos sensibles en el repositorio de Git.

### Carpeta `app/` (Código de la Aplicación)
*   **api.py**: Contiene los controladores de rutas (endpoints). Define las funciones asociadas a peticiones HTTP (como `POST /datos/cargar/freelancers` y `POST /datos/cargar/resenas`).
*   **state.py**: Maneja un almacenamiento global en memoria mientras el servidor está activo. Esto permite mantener los datos de freelancers y opiniones en memoria intermedia para realizar la limpieza, NLP y modelado sin depender de una base de datos pesada en esta fase de desarrollo.
*   **schemas.py**: Define los esquemas de validación mediante `pydantic`. Valida que las respuestas enviadas al frontend tengan la estructura exacta esperada (como las previsualizaciones de tablas y metadatos de los CSVs).
*   **reports.py**: Agrupa la lógica encargada de generar resúmenes, estadísticas descriptivas y datos formateados para mostrar gráficos y reportes consolidados en el frontend.

### Carpeta `ml/` (Inteligencia Artificial y NLP)
*   **preprocessor.py**: Lógica para la preparación de los datos numéricos y categóricos de freelancers (imputación de valores faltantes, conversión de tipos de datos, escalamiento MinMax o Standard).
*   **nlp.py**: Lógica de procesamiento de lenguaje natural para las reseñas de los clientes (limpieza de texto, remoción de stopwords, vectorización con TF-IDF o Word Embeddings, y análisis de sentimiento).
*   **clustering.py**: Implementa los algoritmos de clustering (K-Means) para agrupar tanto perfiles numéricos como opiniones vectorizadas de los freelancers.
*   **evaluation.py**: Proporciona métricas de calidad para determinar el número óptimo de clusters (método del codo/inercia y coeficiente de silueta).

---

## 🚀 Guía de Ejecución

Sigue estos pasos para configurar y ejecutar el servidor del Backend de forma local:

### 1. Requisitos Previos
Asegúrate de tener instalado **Python 3.10** o superior en tu sistema.

### 2. Creación del Entorno Virtual (Recomendado)
Es una buena práctica crear un entorno virtual para aislar las dependencias del proyecto:

En Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

En macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias
Una vez activado el entorno virtual, instala las librerías necesarias ejecutando:
```bash
pip install -r requirements.txt
```

*(Las dependencias principales son `fastapi`, `uvicorn`, `pandas`, `scikit-learn` y `python-multipart`)*.

### 4. Configurar Variables de Entorno
Copia el archivo `.env.example` y renómbralo como `.env`:
```bash
copy .env.example .env     # En Windows (CMD/PowerShell)
cp .env.example .env       # En macOS/Linux
```
*(Puedes dejar los valores predeterminados o ajustar el puerto y variables según lo necesites).*

### 5. Iniciar el Servidor de Desarrollo
Para correr el servidor FastAPI local con recarga automática activada (recarga en caliente al guardar cambios), ejecuta el script principal en la raíz:
```bash
python main.py
```

El servidor se iniciará y estará escuchando peticiones en:
👉 **`http://localhost:8000`**

### 6. Documentación Interactiva (Swagger UI)
FastAPI genera automáticamente documentación interactiva para que puedas probar los endpoints directamente desde tu navegador:
*   **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
*   **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
