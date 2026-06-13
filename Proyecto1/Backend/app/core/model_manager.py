import os
import pickle
from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split


STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage")

COLUMNAS_FEATURES = [
    "ingresos_mensuales", "deuda_activa", "historial_pagos",
    "antiguedad_laboral", "creditos_activos", "monto_solicitado",
    "atrasos_previos", "dependientes_economicos", "utilizacion_credito"
]

HIPERPARAMETROS_DEFAULT = {
    "n_arboles": 100,
    "profundidad_maxima": 10,
    "hojas_maximas": 50,
}


class ModelManager:
    def __init__(self):
        self.model = None
        self.metricas = None
        self.hiperparams = None
        self.matriz_confusion = None
        self.distribucion_predicciones = None
        self.cargar_modelo()

    def normalizar_hiperparametros(self, hiperparametros=None):
        hp = dict(HIPERPARAMETROS_DEFAULT)

        if hiperparametros:
            n = int(hiperparametros.get("n_arboles", hp["n_arboles"]))
            hp["n_arboles"] = max(10, min(n, 1000))

            p = int(hiperparametros.get("profundidad_maxima", hp["profundidad_maxima"]))
            hp["profundidad_maxima"] = max(2, min(p, 100))

            h = int(hiperparametros.get("hojas_maximas", hp["hojas_maximas"]))
            hp["hojas_maximas"] = max(2, min(h, 500))

        return hp

    def construir_modelo(self, hiperparametros=None) -> Tuple[dict, RandomForestClassifier]:
        hp = self.normalizar_hiperparametros(hiperparametros)
        modelo = RandomForestClassifier(
            n_estimators=hp["n_arboles"],
            max_depth=hp["profundidad_maxima"],
            max_leaf_nodes=hp["hojas_maximas"],
            random_state=42,
            n_jobs=-1,
            class_weight="balanced",
        )
        return hp, modelo

    def evaluar(self, y_test, y_pred):
        metricas = {
            "exactitud": round(float(accuracy_score(y_test, y_pred)), 4),
            "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
            "f1_score": round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
        }

        cm = confusion_matrix(y_test, y_pred)
        if cm.size == 1:
            if int(np.sum(y_test)) == 0:
                tn, fp, fn, tp = cm[0][0], 0, 0, 0
            else:
                tn, fp, fn, tp = 0, 0, 0, cm[0][0]
        else:
            tn, fp, fn, tp = cm.ravel()

        matriz_confusion = {
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp),
        }

        dist_predicciones = {
            "sin_riesgo": int(np.sum(y_pred == 0)),
            "en_riesgo": int(np.sum(y_pred == 1)),
        }

        return {
            "metricas": metricas,
            "matriz_confusion": matriz_confusion,
            "distribucion_predicciones": dist_predicciones,
        }

    def guardar_modelo(self, model=None):
        modelo_a_guardar = model or self.model
        if modelo_a_guardar is None:
            return None

        os.makedirs(STORAGE_DIR, exist_ok=True)
        filepath = os.path.join(STORAGE_DIR, "modelo.pkl")
        with open(filepath, "wb") as f:
            pickle.dump(modelo_a_guardar, f)
        return filepath

    def cargar_modelo(self):
        filepath = os.path.join(STORAGE_DIR, "modelo.pkl")
        if not os.path.exists(filepath):
            return None

        with open(filepath, "rb") as f:
            self.model = pickle.load(f)
        return self.model

    def entrenar(self, df, hiperparametros=None):
        if df is None:
            raise ValueError("No hay datos limpios. Ejecuta primero la limpieza de datos.")

        hp, modelo = self.construir_modelo(hiperparametros)

        X = df[COLUMNAS_FEATURES]
        y = df["en_riesgo"]

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
            stratify=y,
        )

        modelo.fit(X_train, y_train)
        y_pred = modelo.predict(X_test)
        evaluacion = self.evaluar(y_test, y_pred)

        self.model = modelo
        self.metricas = evaluacion["metricas"]
        self.hiperparams = hp
        self.matriz_confusion = evaluacion["matriz_confusion"]
        self.distribucion_predicciones = evaluacion["distribucion_predicciones"]
        self.guardar_modelo(modelo)

        return {
            "metricas": self.metricas,
            "matriz_confusion": self.matriz_confusion,
            "distribucion_predicciones": self.distribucion_predicciones,
            "hiperparametros": {
                "n_arboles": hp["n_arboles"],
                "profundidad_maxima": hp["profundidad_maxima"],
                "hojas_maximas": hp["hojas_maximas"],
            },
            "filas_entrenamiento": int(len(X_train)),
            "filas_prueba": int(len(X_test)),
            "mensaje": (
                f"Modelo entrenado con {len(X_train)} registros. "
                f"Exactitud: {self.metricas['exactitud'] * 100:.1f}%, "
                f"F1: {self.metricas['f1_score'] * 100:.1f}%."
            ),
        }

    def predecir(self, input_data):
        if self.model is None:
            self.cargar_modelo()

        if self.model is None:
            raise ValueError("No hay un modelo entrenado o cargado disponible.")

        return self.model.predict(input_data)

    def obtener_modelo(self):
        if self.model is None:
            self.cargar_modelo()
        return self.model

    def obtener_metricas(self):
        return self.metricas

    def obtener_hiperparametros(self):
        return self.hiperparams

    # Alias de compatibilidad para el código existente.
    def get_modelo(self):
        return self.obtener_modelo()

    def get_metricas(self):
        return self.obtener_metricas()

    def get_hiperparametros(self):
        return self.obtener_hiperparametros()

    def train(self, df, hiperparametros=None):
        return self.entrenar(df, hiperparametros)

    def predict(self, input_data):
        return self.predecir(input_data)

    def save_model(self, model=None):
        return self.guardar_modelo(model)

    def load_model(self):
        return self.cargar_modelo()

    def evaluate(self, y_test, y_pred):
        return self.evaluar(y_test, y_pred)


model_manager = ModelManager()
