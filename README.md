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

## Estrategia de Limpieza y Preprocesamiento de Datos Crediticios

## 1. Tratamiento de Duplicados y Registro Basura

* **Duplicados:**
    * *Acción:* Eliminación directa. 
    * *Justificación:* Un registro idéntico en datos crediticios no representa una segunda solicitud real, sino un error de carga en el sistema.
* **Registro basura completo (todos en cero):**
    * *Acción:* Se elimina antes de cualquier otra etapa de limpieza.
    * *Justificación:* Intentar imputar datos sobre una fila completamente inválida introduciría "ruido fabricado" que alteraría el análisis.

---

## 2. Inconsistencias y Valores Fuera de Rango

> **Principio de diseño:** La razón de convertir los valores inconsistentes a `NaN` antes de imputar es mantener un solo punto de control unificado para todos los valores faltantes, evitando tener lógica dispersa a lo largo del código.

| Campo | Problema | Estrategia |
| :--- | :--- | :--- |
| `ingresos_mensuales` | Negativos o cero | Convertir a `NaN` → luego imputar con mediana |
| `monto_solicitado` | Igual a cero | Convertir a `NaN` → luego imputar con mediana |
| `historial_pagos` | Fuera del rango 0–100 | Convertir a `NaN` → luego imputar con mediana |
| `utilizacion_credito` | Fuera del rango 0–100 | Convertir a `NaN` → luego imputar con mediana |
| `antiguedad_laboral` | Negativa | Convertir a `NaN` → luego imputar con mediana |
| `deuda_activa` | Igual a cero | **Se conserva** — un solicitante sin deuda activa es un escenario perfectamente válido. |
| `creditos_activos` | Igual a cero | **Se conserva** — también representa un caso real y válido. |

---

## 3. Tratamiento de Valores Faltantes
*(Aplicado tras la conversión de inconsistencias a `NaN`)*

| Campo | Estrategia | Razón |
| :--- | :--- | :--- |
| `ingresos_mensuales`<br>`deuda_activa`<br>`monto_solicitado` | **Mediana** | Campos monetarios con alta varianza y presencia de *outliers* (valores atípicos); la mediana es más robusta que la media. |
| `historial_pagos`<br>`utilizacion_credito` | **Mediana** | Porcentajes acotados pero con una distribución potencialmente asimétrica. |
| `antiguedad_laboral` | **Mediana** | Razón similar; valores enteros positivos con distribución sesgada. |
| `atrasos_previos`<br>`dependientes_economicos`<br>`creditos_activos` | **Moda** | Valores enteros pequeños y discretos; la moda refleja fielmente el caso más frecuente. |

---

## 4. Estandarización de Datos

Al final del proceso se aplica `StandardScaler` sobre todas las columnas numéricas de entrada (excluyendo la variable objetivo `en_riesgo`).

* **¿Por qué es necesario?** Los rangos de las variables son muy dispares. Por ejemplo, `ingresos_mensuales` puede oscilar entre miles y decenas de miles, mientras que `atrasos_previos` se mantiene en un rango corto de 0 a 7.
* **Impacto:** Sin este escalamiento, el modelo de Machine Learning le otorgaría de forma implícita un mayor peso a las variables de gran magnitud, sesgando los resultados.

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

```
OLC2_EJ26_ML32/
│
├── backend/
│   ├── main.py
│   ├── controllers/
│   ├── services/
│   ├── models/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   └── lib/
│   ├── public/
│   ├── next.config.js
│   └── package.json
│
└── README.md
```

---

# Instalación

## Clonar repositorio

```bash
git clone https://github.com/[TuUsuario]/OLC2_EJ26_ML_32.git
```

## Entrar al proyecto

```bash
cd OLC2_EJ26_ML_32/Proyecto1
```

---

# Configuración Backend

## Crear entorno virtual

```bash
python -m venv venv
```

## Activar entorno virtual

### Windows

```bash
venv\Scripts\activate
```

### Linux / Mac

```bash
source venv/bin/activate
```

## Instalar dependencias

```bash
pip install -r requirements.txt
```

## Ejecutar servidor

```bash
uvicorn main:app --reload
```

---

# Configuración

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
