from pydantic import BaseModel

class Hiperparametros(BaseModel):
    n_arboles: int
    profundidad_maxima: int
    hojas_maximas: int
