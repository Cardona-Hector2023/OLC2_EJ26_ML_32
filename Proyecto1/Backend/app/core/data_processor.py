import pandas as pd
import os

STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage")

# Variables en memoria para evitar recargar desde disco continuamente
_original_df = None
_clean_df = None

# Nos ayuda a poder guardar el dataframe original en memoria.
def set_original_data(df: pd.DataFrame):
    """Guarda el dataframe original en memoria."""
    global _original_df
    _original_df = df

# Nos ayuda a poder obtener el dataframe original de la memoria.
def get_original_data() -> pd.DataFrame:
    """Devuelve el dataframe original de la memoria."""
    return _original_df

# Nos ayuda a poder guardar un respaldo del CSV original en storage/.
def save_original_csv(df: pd.DataFrame):
    """Guarda un respaldo del CSV original en storage/."""
    os.makedirs(STORAGE_DIR, exist_ok=True)
    filepath = os.path.join(STORAGE_DIR, "dataset_original.csv")
    df.to_csv(filepath, index=False)

# Nos ayuda a poder obtener el dataframe limpio de la memoria.
def get_clean_data() -> pd.DataFrame:
    """Devuelve el dataframe limpio."""
    return _clean_df
# Nos ayuda a poder guardar el dataframe limpio en memoria y en storage/.
def save_clean_csv(df: pd.DataFrame):
    """Guarda un respaldo del CSV limpio y actualiza memoria."""
    global _clean_df
    _clean_df = df
    os.makedirs(STORAGE_DIR, exist_ok=True)
    filepath = os.path.join(STORAGE_DIR, "dataset_clean.csv")
    df.to_csv(filepath, index=False)




# Aquí agregaremos después las funciones puras de limpieza...  Aqui puedes empezar a programar el manejo de tu archivo CSV  -----------------------------