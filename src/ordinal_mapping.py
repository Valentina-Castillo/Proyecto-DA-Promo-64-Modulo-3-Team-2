# ============================================================================
# IMPORTACIÓN DE LIBRERÍAS
# ============================================================================

import pandas as pd


def mapear_columnas_ordinales(df, mapeos_columnas, mostrar_resumen=True):
    """
    Aplica mapeo semántico a columnas ordinales del DataFrame.
    
    Las variables ordinales son aquellas que tienen un orden natural
    (ej: 1=Bajo, 2=Medio, 3=Alto). Esta función las convierte de códigos
    numéricos a etiquetas textuales más comprensibles.

    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame a modificar
    mapeos_columnas : dict
        Diccionario con nombres de columnas como claves y diccionarios de mapeo como valores
        Formato: {'columna': {valor_numerico: 'etiqueta_texto', ...}, ...}
        Ejemplo:
        {
            "education": {1: "Sin estudios", 2: "Educación básica", ...},
            "job_level": {1: "Becario", 2: "Junior", ...}
        }
    mostrar_resumen : bool, default=True
        Si True, imprime resumen de columnas mapeadas y sus valores únicos

    Retorna:
    --------
    pd.DataFrame
        DataFrame con columnas ordinales mapeadas a etiquetas textuales
    """
    # Crear copia para no modificar el DataFrame original
    df = df.copy()
    
    # Lista para rastrear columnas mapeadas
    columnas_mapeadas = []

    # Aplicar cada mapeo especificado
    for columna, mapa in mapeos_columnas.items():
        # Verificar que la columna existe
        if columna in df.columns:
            # .map() reemplaza cada valor según el diccionario proporcionado
            # Ej: si mapa = {1: "Bajo", 2: "Alto"}, entonces 1 se convierte en "Bajo"
            df[columna] = df[columna].map(mapa)
            columnas_mapeadas.append(columna)

    # Mostrar resumen del proceso
    if mostrar_resumen:
        print("🔹 Mapeo de columnas ordinales finalizado.")
        print(f"Columnas mapeadas: {columnas_mapeadas}")
        # Mostrar valores únicos de cada columna mapeada para verificación
        for col in columnas_mapeadas:
            print(f"{col}: {df[col].unique()}")

    return df
