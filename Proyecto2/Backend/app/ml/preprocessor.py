"""
Lógica para transformar, limpiar y preparar (Preprocesar) los DataFrames antes de enviarlos a entrenar.

Funciones que irán aquí:
- clean_freelancers(): Imputar valores nulos, estandarizar columnas numéricas (StandardScaler).
- clean_reviews(): Pasar texto a minúsculas, quitar caracteres especiales, eliminar "stopwords".

Mantener esto separado del endpoint asegura que el endpoint sea limpio (solo recibe la orden)
y esta capa haga el trabajo pesado de datos.
"""
