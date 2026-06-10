# OLC2_EJ26_ML_32

- **Catedrático:** Luis Fernando Espino Barrios
- **Auxiliar:** Carlos Fernando Enrique Lopez Garcia
- **Grupo:** 32  

## Integrantes del Proyecto

| Nombre                          | Carnet    |
|---------------------------------|-----------|
| Pablo Daniel Velásquez Hernández | 202302232 |
| Héctor Antonio Cardona Cos      | 202307354 |


---
# ¿Qué es CreditGuard?

CreditGuard es una aplicación web desarrollada como proyecto del curso Organización de Lenguajes y Compiladores 2.

La idea principal del sistema es ayudar a instituciones financieras a detectar posibles riesgos de incumplimiento crediticio utilizando técnicas de aprendizaje supervisado. Para ello, el sistema analiza información financiera de clientes y genera predicciones basadas en patrones encontrados en los datos históricos.

Además de entrenar modelos predictivos, la aplicación también permite limpiar datos, visualizar métricas y modificar hiperparámetros para mejorar el rendimiento del modelo.

---

# Problemática

En muchas instituciones financieras, el análisis de riesgo crediticio todavía depende bastante de procesos manuales. Esto puede provocar evaluaciones lentas, errores humanos o decisiones poco precisas.

Con CreditGuard se busca automatizar parte de este proceso mediante inteligencia artificial, permitiendo identificar clientes con mayor probabilidad de incumplimiento antes de aprobar un crédito.

---

# Objetivos del Proyecto

## Objetivo General

Crear una aplicación capaz de entrenar y evaluar modelos de predicción de riesgo crediticio utilizando aprendizaje supervisado.

## Objetivos Específicos

* Procesar y limpiar información financiera obtenida desde archivos CSV.
* Implementar un modelo de machine learning desarrollado en Python.
* Mostrar métricas que permitan evaluar el desempeño del modelo.
* Permitir modificar hiperparámetros desde la interfaz.
* Generar predicciones individuales para nuevos solicitantes.

---

# Funcionalidades

## Carga de Datos

El sistema permite subir archivos CSV con registros históricos de clientes.

Entre los datos utilizados se encuentran:

* Ingresos mensuales
* Deuda activa
* Historial de pagos
* Antigüedad laboral
* Créditos activos
* Monto solicitado
* Atrasos previos
* Dependientes económicos
* Utilización del crédito

---

## Limpieza de Datos

Antes de entrenar el modelo, el sistema realiza un preprocesamiento de la información para mejorar la calidad de los datos.

Por ejemplo:

* Manejo de valores nulos
* Corrección de inconsistencias
* Validación de rangos inválidos
* Normalización de datos

---

## Entrenamiento del Modelo

Con los datos ya procesados, el sistema permite entrenar un modelo de aprendizaje supervisado encargado de clasificar el riesgo crediticio.

El modelo es desarrollado completamente en Python y no utiliza APIs externas ni modelos preentrenados.

---

## Evaluación del Modelo

Después del entrenamiento, el sistema muestra diferentes métricas para analizar el rendimiento del modelo:

* Exactitud
* Precisión
* Recall
* F1 Score
* Matriz de confusión

Estas métricas ayudan a determinar qué tan confiables son las predicciones generadas.

---

## Ajuste de Hiperparámetros

La aplicación también incluye una sección donde es posible modificar ciertos parámetros del modelo para intentar mejorar los resultados.

Algunos de los parámetros configurables son:

* Número de árboles
* Profundidad máxima
* Cantidad máxima de hojas

---

## Predicción Individual

Una vez entrenado el modelo, el usuario puede ingresar los datos de un solicitante específico para obtener una predicción inmediata.

El sistema indicará si existe:

* Riesgo de incumplimiento
* O ausencia de riesgo detectado

---

# Tecnologías Utilizadas

## Backend

* Python
* FastAPI

## Frontend

* React + NEXT.js

## Librerías

* Pandas
* NumPy
* Scikit-learn

## Control de versiones

* Git
* GitHub

---

# Estructura del Proyecto

```bash id="t5pc4t"
Proyecto1/
│
├── backend/
│   ├── app.py
│   ├── controllers/
│   ├── services/
│   ├── models/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
└── README.md
```

---

# Instalación

## Clonar repositorio

```bash id="ttd84h"
git clone https://github.com/[TuUsuario]/OLC2_EJ26_ML_32.git
```

## Entrar al proyecto

```bash id="4x4nnx"
cd OLC2_EJ26_ML_32/Proyecto1
```

---

# Configuración Backend

## Crear entorno virtual

```bash id="s4wk04"
python -m venv venv
```

## Activar entorno virtual

### Windows

```bash id="pzrd48"
venv\Scripts\activate
```

### Linux / Mac

```bash id="1p35zj"
source venv/bin/activate
```

## Instalar dependencias

```bash id="zuh13k"
pip install -r requirements.txt
```

## Ejecutar servidor

```bash id="2bp9ku"
python app.py
```

---

# Configuración Frontend

## Instalar dependencias

```bash id="bzy8s9"
 pnpm install
```

## Ejecutar aplicación

```bash id="mwpt8u"
pnpm dev
```

---

# Flujo Básico de Uso

1. Subir archivo CSV.
2. Limpiar los datos.
3. Entrenar el modelo.
4. Revisar métricas.
5. Ajustar hiperparámetros.
6. Realizar predicciones.

---

# Restricciones

* No se permite utilizar APIs externas.
* El modelo debe desarrollarse desde cero.
* El backend debe implementarse en Python.
* El repositorio debe mantenerse privado.
* Se deben seguir buenas prácticas de programación.

---

# Curso

Organización de Lenguajes y Compiladores 2
Facultad de Ingeniería - USAC
Escuela de Vacaciones Junio 2026
