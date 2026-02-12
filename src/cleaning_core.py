# ============================================================================
# INSTALACIÓN E IMPORTACIÓN DE LIBRERÍAS
# ============================================================================

# Librerías para manipulación de datos
import pandas as pd  # Trabajo con DataFrames y análisis de datos
import numpy as np   # Operaciones numéricas y arrays
import re            # Expresiones regulares para procesamiento de texto

# Librerías de scikit-learn para imputación y escalado
from sklearn.impute import SimpleImputer, KNNImputer  # Métodos de imputación de nulos
from sklearn.preprocessing import StandardScaler      # Estandarización de variables numéricas

# Librería del sistema operativo
import os  # Gestión de rutas y archivos del sistema


# ---------------------------------------------------------------------------
# En entornos interactivos como Jupyter Notebook, la función `display()` está
# disponible por defecto para mostrar DataFrames y objetos formateados.
# En scripts .py estándar no existe automáticamente, por lo que se importa
# desde IPython para mantener el mismo comportamiento visual cuando se ejecuta
# el pipeline fuera del notebook.
# ---------------------------------------------------------------------------

try:
    from IPython.display import display  # type: ignore
except Exception:
    def display(x):  # noqa: D401
        print(x)


def normalizar_nombres_columnas(lista_columnas, mostrar_resumen=True):
    """
    Normaliza los nombres de las columnas de un DataFrame a formato snake_case.
    
    El proceso de normalización incluye:
    - Eliminar espacios al inicio y al final
    - Eliminar caracteres especiales (excepto guiones bajos)
    - Convertir de CamelCase o PascalCase a snake_case
    - Convertir todo a minúsculas
    
    Parámetros:
    -----------
    lista_columnas : list
        Lista con los nombres originales de las columnas.
    mostrar_resumen : bool, opcional
        Si True (por defecto), imprime un resumen de los cambios realizados.
    
    Retorna:
    --------
    list
        Lista con los nombres de columnas normalizados.
    """
    columnas_originales = lista_columnas.copy()
    columnas_normalizadas = []

    for col in lista_columnas:
        col_original = col

        # Quitar espacios en extremos
        col = col.strip()

        # Reemplazar caracteres especiales por underscore
        col = re.sub(r"[^\w\s]", "", col)

        # Convertir CamelCase / PascalCase a snake_case
        col = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', col)
        col = re.sub('([a-z0-9])([A-Z])', r'\1_\2', col)

        # Reemplazar espacios múltiples por underscore
        col = re.sub(r"\s+", "_", col)

        # Convertir todo a minúsculas
        col = col.lower()

        columnas_normalizadas.append(col)

    if mostrar_resumen:
        resumen = pd.DataFrame({
            "Original": columnas_originales,
            "Normalizado": columnas_normalizadas
        })
        print("Resumen de normalización de columnas:")
        display(resumen)

    return columnas_normalizadas


def usar_columna_como_indice(df, columna_original, indice="id"):
    """
    Establece una columna existente como índice del DataFrame y renombra el índice.

    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame original.
    columna_original : str
        Nombre de la columna que se quiere usar como índice.
    indice : str, opcional
        Nombre que se asignará al índice una vez establecido. Por defecto "id".

    Retorna:
    --------
    pd.DataFrame
        DataFrame con la columna convertida en índice.
    """
    if columna_original not in df.columns:
        raise ValueError(f"La columna '{columna_original}' no existe en el DataFrame.")

    df = df.set_index(columna_original)
    df.index.name = indice

    return df


def eliminar_filas_duplicadas(df, keep="first"):
    """
    Elimina filas duplicadas en el DataFrame.

    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame original.
    keep : {'first', 'last', False}, opcional
        Define cuál duplicado conservar:
        - 'first': conserva la primera aparición (por defecto)
        - 'last': conserva la última aparición
        - False: elimina todos los duplicados

    Retorna:
    --------
    pd.DataFrame
        DataFrame sin filas duplicadas.
    """
    n_duplicados = df.duplicated(keep=keep).sum()

    print(f"Se han detectado {n_duplicados} filas duplicadas.")

    df = df.drop_duplicates(keep=keep)

    print(f"✅ Duplicados eliminados. Dimensión final: {df.shape}")

    return df


def eliminar_columnas_sin_aporte_analitico(df, umbral_cardinalidad=0.95):
    """
    Elimina columnas que no aportan valor analítico:
    - Columnas constantes (un único valor en todas las filas)
    - Columnas con cardinalidad extremadamente alta (por defecto >95% valores únicos)

    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame original.
    umbral_cardinalidad : float, opcional
        Umbral de porcentaje de valores únicos para considerar una columna como alta cardinalidad.
        Por defecto 0.95 (95%).

    Retorna:
    --------
    pd.DataFrame
        DataFrame sin columnas irrelevantes.
    """
    columnas_a_eliminar = []

    for col in df.columns:
        n_unique = df[col].nunique(dropna=False)
        porcentaje_unique = n_unique / len(df)

        # Columnas constantes
        if n_unique == 1:
            columnas_a_eliminar.append(col)

        # Columnas con demasiados valores únicos
        elif porcentaje_unique > umbral_cardinalidad:
            columnas_a_eliminar.append(col)

    print(f"Columnas a eliminar ({len(columnas_a_eliminar)}): {columnas_a_eliminar}")

    df = df.drop(columns=columnas_a_eliminar)

    print(f"✅ Columnas eliminadas. Dimensión final: {df.shape}")

    return df


def normalizar_columnas_texto(df, mapeos_reemplazo=None):
    """
    Normaliza todas las columnas de texto de un DataFrame:
    - Elimina espacios al inicio y final
    - Convierte a formato Title Case o formato uniforme
    - Aplica reemplazos definidos en mapeos_reemplazo (por ejemplo, corregir typos)

    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame original.
    mapeos_reemplazo : dict, opcional
        Diccionario con estructura:
        {
            "columna": {"valor_original": "valor_nuevo", ...},
            ...
        }

    Retorna:
    --------
    pd.DataFrame
        DataFrame con columnas de texto normalizadas.
    """
    df = df.copy()

    # Detectar columnas de texto
    cols_texto = df.select_dtypes(include=["object"]).columns

    for col in cols_texto:
        # Quitar espacios y normalizar formato (Title Case)
        df[col] = df[col].astype(str).str.strip()

        # Reemplazar valores "nan" en string por np.nan real
        df[col] = df[col].replace("nan", np.nan)

        # Aplicar reemplazos específicos si se proporcionan
        if mapeos_reemplazo and col in mapeos_reemplazo:
            df[col] = df[col].replace(mapeos_reemplazo[col])

    print(f"✅ Columnas de texto normalizadas: {list(cols_texto)}")

    return df


def convertir_tipos_columnas(df, mapeo_tipos, mostrar_resumen=True):
    """
    Convierte el tipo de dato de columnas específicas según un diccionario proporcionado.

    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame original.
    mapeo_tipos : dict
        Diccionario donde las claves son nombres de columnas y los valores son tipos deseados.
        Ejemplo:
        {
            "age": "Int64",
            "daily_rate": float,
            ...
        }
    mostrar_resumen : bool, opcional
        Si True, muestra un resumen de las conversiones realizadas. Por defecto True.

    Retorna:
    --------
    pd.DataFrame
        DataFrame con los tipos convertidos.
    """
    df = df.copy()
    columnas_convertidas = []

    for columna, tipo in mapeo_tipos.items():
        if columna in df.columns:
            try:
                df[columna] = df[columna].astype(tipo)
                columnas_convertidas.append(columna)
            except Exception as e:
                # Si falla, informar del error pero continuar con otras columnas
                print(f"No se pudo convertir la columna '{columna}' a {tipo}: {e}")

    # Mostrar resumen del proceso
    if mostrar_resumen:
        print("Conversión de tipos finalizada.")
        if columnas_convertidas:
            print(f"Columnas convertidas: {columnas_convertidas}")
        else:
            print("No se convirtió ninguna columna.")

        # Mostrar tabla con todos los tipos de datos finales
        print("\nTipos de datos finales por columna:")
        tipos_finales = pd.DataFrame({
            "Columna": df.columns,
            "Tipo de dato": [df[col].dtype for col in df.columns]
        })
        display(tipos_finales)
            
    return df
