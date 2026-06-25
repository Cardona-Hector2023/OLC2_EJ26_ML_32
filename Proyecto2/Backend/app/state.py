"""
Este archivo es el administrador del estado global (En Memoria).
Dado que FastAPI no guarda datos entre diferentes peticiones (es stateless),
usaremos un objeto global aquí para almacenar los DataFrames de freelancers
y reseñas después de que el usuario los suba.

¿Para qué nos sirve?
Para que cuando el usuario haga clic en "Limpiar Datos" o "Entrenar",
podamos recuperar el DataFrame que subió en el paso de "Carga de Datos"
sin necesidad de volver a enviarlo por la red ni guardarlo en una base de datos.
"""

class AppState:
    def __init__(self):
        # Aquí guardaremos temporalmente los DataFrames de Pandas
        self.df_freelancers = None
        self.df_resenas = None
        
        # Aquí podremos guardar el modelo entrenado
        self.modelo_freelancers = None
        self.modelo_resenas = None

# Instancia global (Singleton) a la que accederán los endpoints de api.py
global_state = AppState()
