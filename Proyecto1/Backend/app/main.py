from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router

# Crea la API y a poder configurar los parámetros de la API.
app = FastAPI(
    title="CreditGuard API - Grupo 32",
    description="Backend para predicción de riesgo crediticio",
    version="1.0.0"
)

# Configuración de CORS, los CORS son las políticas de seguridad que permiten la comunicación entre el frontend y el backend.
app.add_middleware(
    CORSMiddleware, # Nos ayuda a poder configurar los CORS.
    allow_origins=["*"],  # En producción, configurar el dominio exacto
    allow_credentials=True, # Nos ayuda a poder comunicar el frontend con el backend.
    allow_methods=["*"], # Nos sirve para poder permitir el paso de los métodos.
    allow_headers=["*"], # Nos sirve para poder permitir el paso de los encabezados.
)

# Registrar las rutas
app.include_router(router)

# Ruta principal para poder probar si la API está funcionando y poder obtener información sobre el proyecto.
@app.get("/")
def read_root():
    return {"mensaje": "API de CreditGuard en funcionamiento"}
