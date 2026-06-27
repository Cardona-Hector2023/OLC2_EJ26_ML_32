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
        # Aquí guardaremos temporalmente los DataFrames de Pandas tal como
        # llegaron del CSV original (crudos, sin ninguna limpieza).
        # Se conservan así para poder mostrar comparativas "antes y después"
        # en el EDA del manual técnico, y para poder re-ejecutar la limpieza
        # si el usuario presiona "Limpiar Datos" más de una vez.
        self.df_freelancers = None
        self.df_resenas = None
 
        # Aquí guardaremos los DataFrames después de pasar por
        # preprocessor.limpiar_freelancers() / nlp.limpiar_resenas().
        # Estos son los que se usan en Configuración y Entrenamiento,
        # Interpretación de Segmentos, Evaluación, etc.
        self.df_freelancers_limpio = None
        self.df_resenas_limpio = None
 
        # Aquí podremos guardar el modelo entrenado
        self.modelo_freelancers = None
        self.modelo_resenas = None
 
    def hay_datos_cargados(self) -> bool:
        """True si al menos uno de los dos archivos fue cargado."""
        return self.df_freelancers is not None or self.df_resenas is not None
 
    def reset_limpieza(self) -> None:
        """
        Limpia el resultado de una limpieza previa, por si el usuario
        vuelve a presionar "Limpiar Datos" tras cargar un archivo nuevo.
        """
        self.df_freelancers_limpio = None
        self.df_resenas_limpio = None
 
 
# Instancia global (Singleton) a la que accederán los endpoints de api.py
global_state = AppState()
 