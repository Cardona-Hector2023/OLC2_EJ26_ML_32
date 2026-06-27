import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importamos nuestro único archivo de rutas desde el paquete 'app'
from app.api import router as api_router

# Inicialización de la aplicación FastAPI
app = FastAPI(
    title="TalentMosaic API",
    description="Backend simplificado para análisis y clustering de freelancers y reseñas",
    version="1.0.0"
)

# Configuración de CORS (Cross-Origin Resource Sharing)
# Esto es vital para que tu frontend en localhost:3000 (o donde corra pnpm dev)
# pueda hacer peticiones a este backend en localhost:8000 sin ser bloqueado por el navegador.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, cambia esto por el dominio real de tu frontend
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los headers
)

import os
from fastapi.staticfiles import StaticFiles

# Registramos todas las rutas definidas en api.py
app.include_router(api_router)

os.makedirs("exports", exist_ok=True)
app.mount("/exports", StaticFiles(directory="exports"), name="exports")

@app.get("/", tags=["Health"])
def read_root():
    """
    Ruta base de salud. 
    Sirve para verificar rápidamente en el navegador si el servidor está levantado y respondiendo.
    """
    return {"mensaje": "Bienvenido a TalentMosaic API"}

if __name__ == "__main__":
    # Ejecutamos el servidor uvicorn. 
    # Apuntamos a "main:app" porque el objeto 'app' ahora está en este archivo main.py de la raíz.
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
