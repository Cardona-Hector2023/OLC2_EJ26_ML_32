from pydantic import BaseModel, Field

class SolicitanteInput(BaseModel):
    ingresos_mensuales: float
    deuda_activa: float
    historial_pagos: float
    antiguedad_laboral: float
    creditos_activos: float
    monto_solicitado: float
    atrasos_previos: float
    dependientes_economicos: float
    utilizacion_credito: float
