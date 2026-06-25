"""
Cálculo de métricas de calidad y gráficas 2D.

¿Para qué sirve?
Una vez que K-Means ha asignado a los freelancers al "Segmento 0", "Segmento 1", etc.,
¿Cómo sabemos si el algoritmo lo hizo bien o si los segmentos son basura?
Aquí implementaremos:
- Índice Silhouette (Para medir cohesión y separación).
- PCA (Principal Component Analysis): Para tomar datos de 8 dimensiones (experiencia, precio, etc.)
  y aplastarlos a 2 dimensiones (X, Y) para poder graficarlos en el Frontend (el "Scatter Plot").
"""
