from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router

app = FastAPI(
    title="CreditGuard API - Grupo 32",
    description="Backend para predicción de riesgo crediticio",
    version="1.0.0"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, configurar el dominio exacto
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar las rutas
app.include_router(router)

@app.get("/")
def read_root():
    return {"mensaje": "API de CreditGuard en funcionamiento"}
