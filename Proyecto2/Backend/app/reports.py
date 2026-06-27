"""
Módulo de Reportes.

¿Para qué sirve?
Al finalizar el flujo del usuario (Carga -> Limpieza -> Entrenamiento -> Segmentos -> Evaluación),
el usuario puede decidir exportar los hallazgos.
Este archivo agrupará funciones para generar:
1. Archivos .CSV descargables (con una columna extra indicando el segmento).
2. Reportes visuales PDF usando librerías como matplotlib o fpdf.
"""

import os
import pandas as pd
from fpdf import FPDF
import matplotlib.pyplot as plt
import uuid
import app.ml.clustering as cl
from app.ml.preprocessor import COLUMNAS_NUMERICAS
from app.ml.evaluation import evaluar_modelo
from app.state import global_state

EXPORTS_DIR = "exports"

def asegurar_directorio():
    os.makedirs(EXPORTS_DIR, exist_ok=True)

def _obtener_df_y_artefactos(dataset: str):
    # Intentamos sacar del state o disco, luego cargar artefactos
    from app.api import _cargar_artefactos_modelo, _recuperar_df_segmentado
    
    if dataset == "freelancers":
        df = global_state.df_freelancers_segmentado
        if df is None: df = _recuperar_df_segmentado("freelancers")
    else:
        df = global_state.df_resenas_segmentado
        if df is None: df = _recuperar_df_segmentado("resenas")
        
    if df is None: return None, None, None, None
    
    df = df.reset_index(drop=True)
    labels = df["segmento"].to_numpy()
    
    try:
        artefactos = _cargar_artefactos_modelo(dataset)
    except:
        return df, labels, None, None

    if dataset == "freelancers":
        df_limpio = df.drop(columns=["segmento"])
        X = artefactos["scaler"].transform(df_limpio[COLUMNAS_NUMERICAS])
    else:
        df_entrenamiento = df.drop(columns=["segmento"])
        textos_limpios = df_entrenamiento["texto_reseña"].astype(str).apply(cl.limpiar_texto)
        X = artefactos["vectorizador"].transform(textos_limpios)
        
    return df, labels, artefactos, X

def exportar_freelancers_segmentado() -> str:
    asegurar_directorio()
    df, _, _, _ = _obtener_df_y_artefactos("freelancers")
    if df is not None:
        ruta = os.path.join(EXPORTS_DIR, "freelancers_segmentado.csv")
        df.to_csv(ruta, index=False)
        return "freelancers_segmentado.csv"
    return None

def exportar_resenas_segmentado() -> str:
    asegurar_directorio()
    df, _, _, _ = _obtener_df_y_artefactos("resenas")
    if df is not None:
        ruta = os.path.join(EXPORTS_DIR, "resenas_segmentado.csv")
        df.to_csv(ruta, index=False)
        return "resenas_segmentado.csv"
    return None

def exportar_resumen_estadistico() -> str:
    asegurar_directorio()
    filas = []
    
    df_f, labels_f, _, _ = _obtener_df_y_artefactos("freelancers")
    if df_f is not None:
        perfiles = cl.perfilar_clusters_numerico(df_f.drop(columns=["segmento"]), COLUMNAS_NUMERICAS, labels_f)
        for c_id, info in sorted(perfiles.items()):
            fila = {"Dataset": "Freelancers", "Segmento": c_id, "Nombre": info["nombre_corto"], "Registros": info["cantidad_registros"]}
            for k, v in info["promedios"].items(): fila[k] = v
            filas.append(fila)
            
    df_r, labels_r, art_r, X_r = _obtener_df_y_artefactos("resenas")
    if df_r is not None and art_r is not None:
        perfiles = cl.perfilar_clusters_texto(X_r, art_r["vectorizador"], labels_r)
        for c_id, info in sorted(perfiles.items()):
            fila = {"Dataset": "Reseñas", "Segmento": c_id, "Nombre": info["nombre_corto"], "Registros": info["cantidad_registros"]}
            fila["Terminos_Clave"] = ", ".join([t["termino"] for t in info["terminos_top"]])
            filas.append(fila)

    if filas:
        ruta = os.path.join(EXPORTS_DIR, "resumen_estadistico.csv")
        pd.DataFrame(filas).to_csv(ruta, index=False)
        return "resumen_estadistico.csv"
    return None

def exportar_metricas_evaluacion() -> str:
    asegurar_directorio()
    filas = []
    
    df_f, labels_f, _, X_f = _obtener_df_y_artefactos("freelancers")
    if X_f is not None:
        m = evaluar_modelo(X_f, labels_f)
        filas.append({"Dataset": "Freelancers", **m})
        
    df_r, labels_r, _, X_r = _obtener_df_y_artefactos("resenas")
    if X_r is not None:
        m = evaluar_modelo(X_r, labels_r)
        filas.append({"Dataset": "Reseñas", **m})

    if filas:
        ruta = os.path.join(EXPORTS_DIR, "metricas_evaluacion.csv")
        pd.DataFrame(filas).to_csv(ruta, index=False)
        return "metricas_evaluacion.csv"
    return None

def exportar_reporte_visual() -> str:
    asegurar_directorio()
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    def add_section(dataset_name, df, labels, art, X):
        if df is None or art is None: return
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, f"Reporte Visual - Segmentos de {dataset_name.capitalize()}", ln=True, align="C")
        pdf.ln(5)
        
        # Generar gráfico
        fig, ax = plt.subplots(figsize=(8, 6))
        
        if dataset_name == "freelancers":
            scatter, _ = cl.reducir_dimensiones_numerico(X, labels, pca=art.get("pca"), retornar_reductor=True)
            perfiles = cl.perfilar_clusters_numerico(df.drop(columns=["segmento"]), COLUMNAS_NUMERICAS, labels)
        else:
            scatter, _ = cl.reducir_dimensiones_texto(X, labels, svd=art.get("svd"), retornar_reductor=True)
            perfiles = cl.perfilar_clusters_texto(X, art["vectorizador"], labels)
        
        df_scatter = pd.DataFrame(scatter)
        for cluster in sorted(df_scatter["cluster"].unique()):
            subset = df_scatter[df_scatter["cluster"] == cluster]
            ax.scatter(subset["x"], subset["y"], label=f"Segmento {cluster}", alpha=0.6)
            
        ax.set_title(f"Dispersión de Segmentos ({dataset_name.capitalize()})")
        ax.legend()
        
        img_path = os.path.join(EXPORTS_DIR, f"temp_plot_{dataset_name}_{uuid.uuid4().hex}.png")
        plt.savefig(img_path, bbox_inches="tight")
        plt.close()
        
        pdf.image(img_path, w=170)
        os.remove(img_path)
        
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Interpretación de los Segmentos:", ln=True)
        pdf.set_font("Arial", '', 11)
        
        for c_id, info in sorted(perfiles.items()):
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(0, 8, f"Segmento {c_id}: {info['nombre_corto']} ({info['cantidad_registros']} registros)", ln=True)
            pdf.set_font("Arial", '', 11)
            if dataset_name == "resenas":
                terminos = ", ".join([t["termino"] for t in info["terminos_top"]])
                pdf.multi_cell(0, 6, f"Términos más frecuentes: {terminos}")
            pdf.ln(4)
            
    df_f, labels_f, art_f, X_f = _obtener_df_y_artefactos("freelancers")
    add_section("freelancers", df_f, labels_f, art_f, X_f)
    
    df_r, labels_r, art_r, X_r = _obtener_df_y_artefactos("resenas")
    add_section("resenas", df_r, labels_r, art_r, X_r)
    
    if df_f is None and df_r is None:
        return None
        
    ruta = os.path.join(EXPORTS_DIR, "reporte_visual.pdf")
    pdf.output(ruta)
    return "reporte_visual.pdf"
