# ============================================================================
# IMPORTACIÓN DE LIBRERÍAS
# ============================================================================

from pathlib import Path

import pandas as pd
import numpy as np

import cleaning_core as cc
import ordinal_mapping as om
import imputation as imp


def run_cleaning_pipeline(input_path: Path, output_path: Path, mostrar_resumen_columnas=True):
    """
    Ejecuta el pipeline completo de limpieza:
    - Carga CSV sucio desde data/raw
    - Aplica limpieza, normalización, mapeos ordinales e imputaciones
    - Exporta CSV limpio a data/processed

    Parámetros:
    -----------
    input_path : Path
        Ruta al CSV original (sucio)
    output_path : Path
        Ruta donde guardar el CSV limpio
    mostrar_resumen_columnas : bool
        Si True, imprime resumen del renombrado de columnas

    Retorna:
    --------
    pd.DataFrame
        DataFrame limpio y procesado
    """

    # ============================================================================
    # CARGA
    # ============================================================================
    df = pd.read_csv(input_path)

    # ============================================================================
    # LIMPIEZA BASE
    # ============================================================================
    df.columns = cc.normalizar_nombres_columnas(df.columns.tolist(), mostrar_resumen=mostrar_resumen_columnas)
    df = cc.usar_columna_como_indice(df, columna_original='employee_number', indice='id')
    df = cc.eliminar_filas_duplicadas(df, keep='first')
    df = cc.eliminar_columnas_sin_aporte_analitico(df, umbral_cardinalidad=0.95)

    mapeos_reemplazo = {
        'marital_status': {'Marreid': 'Married'},
        'business_travel': {
            'Travel_Rarely': 'Rarely',
            'Travel_Frequently': 'Frequently',
            'Non-Travel': 'Non'
        }
    }
    df = cc.normalizar_columnas_texto(df, mapeos_reemplazo=mapeos_reemplazo)

    mapeo_tipos = {
        "age": "Int64",
        "daily_rate": float,
        "hourly_rate": float,
        "training_times_last_year": "Int64",
        "years_with_curr_manager": "Int64",
    }
    df = cc.convertir_tipos_columnas(df, mapeo_tipos)

    # ============================================================================
    # MAPEOS ORDINALES
    # ============================================================================
    satisfaction_map = {
        1: "Not Satisfied at all",
        2: "Dissatisfied",
        3: "Satisfied",
        4: "Delighted",
    }

    education_map = {
        1: "No Formal Education",
        2: "Basic Education",
        3: "Associate Degree",
        4: "Bachelor Degree",
        5: "Postgraduate",
    }

    job_level_map = {
        1: "Entry Level",
        2: "Junior",
        3: "Senior",
        4: "Manager",
        5: "Executive",
    }

    stock_level_map = {
        0: "Unvested",
        1: "Basic",
        2: "Intermediate",
        3: "Executive",
    }

    satisfaction_cols = [
        "environment_satisfaction",
        "job_involvement",
        "job_satisfaction",
        "performance_rating",
        "relationship_satisfaction",
        "work_life_balance",
    ]

    mapeos_ordinales = {col: satisfaction_map for col in satisfaction_cols}
    mapeos_ordinales["education"] = education_map
    mapeos_ordinales["job_level"] = job_level_map
    mapeos_ordinales["stock_option_level"] = stock_level_map

    df = om.mapear_columnas_ordinales(df, mapeos_ordinales)

    # ============================================================================
    # IMPUTACIÓN CATEGÓRICA
    # ============================================================================
    cols_cat = df.select_dtypes(include=["object", "category"]).columns.tolist()
    cols_cat = [c for c in cols_cat if c.lower() != "attrition"]
    df[cols_cat] = df[cols_cat].replace(r'^\s*$', pd.NA, regex=True)
    df = imp.imputar_categoricas(df, cols_cat)
    nulos_restantes_cat = df[cols_cat].isnull().sum().sum()
    print(f"✅ Proceso finalizado. Nulos categóricos restantes: {nulos_restantes_cat}")

    # ============================================================================
    # IMPUTACIÓN NUMÉRICA
    # ============================================================================
    cols_num = df.select_dtypes(include=[np.number]).columns[df.select_dtypes(include=[np.number]).isnull().any()].tolist()
    cols_a_imputar_num = cols_num

    df = imp.imputar_numericas(
        df,
        columnas=cols_a_imputar_num,
        umbral_nulos_bajo=0.05,
        umbral_nulos_alto=0.20,
        n_neighbors=5,
        crear_indicador_missing=True,
        usar_knn_en_alto=False
    )
    nulos_restantes = df[cols_a_imputar_num].isnull().sum().sum()
    print(f"✅ Proceso finalizado. Nulos numéricos restantes: {nulos_restantes}")

    # ============================================================================
    # EXPORTACIÓN
    # ============================================================================
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=True)

    print(f"\n✅ Datos limpios exportados exitosamente a '{output_path}'")
    print(f"📊 Dimensiones finales del dataset: {df.shape[0]} filas x {df.shape[1]} columnas")

    return df

