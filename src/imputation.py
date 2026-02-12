# ============================================================================
# IMPORTACIÓN DE LIBRERÍAS
# ============================================================================

import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.preprocessing import StandardScaler


def imputar_categoricas(df, columnas, umbral_nulos_alto=0.20, umbral_nulos_bajo=0.05,
                        umbral_moda_bajo=0.50, umbral_moda_medio=0.60, umbral_ventaja=0.20,
                        etiqueta_unknown="Unknown"):
    """
    Imputa valores nulos en variables categóricas siguiendo reglas justificables estadísticamente.
    """
    total = len(df)

    for col in columnas:
        print(f"\n📌 Analizando columna: {col}")
        
        if col not in df.columns:
            print(f"❌ La columna {col} no existe en el DataFrame. Se omite.")
            continue

        nulos = df[col].isnull().sum()
        porcentaje_nulos = nulos / total if total > 0 else 0
        print(f"   → Nulos: {nulos} de {total} ({porcentaje_nulos:.2%})")

        if porcentaje_nulos > umbral_nulos_alto:
            print(f"   🔴 Porcentaje de nulos > {umbral_nulos_alto:.0%} → se crea la categoría '{etiqueta_unknown}'")
            df[col] = df[col].fillna(etiqueta_unknown)
            continue
        
        valores = df[col].value_counts(dropna=True)

        if len(valores) == 0:
            print(f"   🔴 No hay valores no nulos → se crea la categoría '{etiqueta_unknown}'")
            df[col] = df[col].fillna(etiqueta_unknown)
            continue

        primero = valores.iloc[0]
        pct_primero = primero / total

        if len(valores) > 1:
            segundo = valores.iloc[1]
            pct_segundo = segundo / total
        else:
            pct_segundo = 0.0

        ventaja = pct_primero - pct_segundo

        print(f"   → Moda: {valores.index[0]} ({pct_primero:.2%})")
        print(f"   → 2ª categoría: {valores.index[1] if len(valores) > 1 else 'No existe'} ({pct_segundo:.2%})")
        print(f"   → Ventaja de la moda: {ventaja:.2%}")

        if porcentaje_nulos <= umbral_nulos_bajo:
            umbral_moda = umbral_moda_bajo
        else:
            umbral_moda = umbral_moda_medio
        
        if (pct_primero >= umbral_moda) and (ventaja >= umbral_ventaja):
            moda = df[col].mode(dropna=True)[0]
            df[col] = df[col].fillna(moda)
        else:
            df[col] = df[col].fillna(etiqueta_unknown)

    return df


def imputar_numericas(df, columnas, umbral_nulos_bajo=0.05, umbral_nulos_alto=0.20,
                      n_neighbors=5, crear_indicador_missing=True, usar_knn_en_alto=False):
    """
    Imputa valores nulos en variables numéricas con estrategias robustas.
    """
    
    dtypes_originales = df.dtypes.copy()
    total = len(df)

    columnas_validas = df[columnas].select_dtypes(include=[np.number]).columns.tolist()
    columnas_no_encontradas = [c for c in columnas if c not in df.columns]
    
    for c in columnas_no_encontradas:
        print(f"{c} no existe en el DataFrame. Se omite.")

    cols_num_df = df.select_dtypes(include=[np.number]).columns.tolist()
    columnas_validas = [c for c in columnas_validas if c in cols_num_df]

    if len(columnas_validas) == 0:
        print("No hay columnas numéricas válidas para imputar.")
        return df

    imputer_mediana = SimpleImputer(strategy="median")
    cols_num_contexto = cols_num_df

    for col in columnas_validas:
        print(f"\n📌 Analizando columna numérica: {col}")

        nulos = df[col].isnull().sum()
        porcentaje_nulos = nulos / total if total > 0 else 0

        if porcentaje_nulos <= umbral_nulos_bajo:
            df[[col]] = imputer_mediana.fit_transform(df[[col]])
            continue

        if porcentaje_nulos <= umbral_nulos_alto:

            X = df[cols_num_contexto].copy()
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            knn = KNNImputer(n_neighbors=n_neighbors)
            X_imputed_scaled = knn.fit_transform(X_scaled)

            X_imputed = scaler.inverse_transform(X_imputed_scaled)
            X_imputed = pd.DataFrame(X_imputed, columns=cols_num_contexto, index=df.index)

            df[col] = X_imputed[col]
            continue

        if crear_indicador_missing:
            indicador = f"{col}_missing"
            df[indicador] = df[col].isnull().astype(int)

        if usar_knn_en_alto:

            X = df[cols_num_contexto].copy()
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            knn = KNNImputer(n_neighbors=n_neighbors)
            X_imputed_scaled = knn.fit_transform(X_scaled)

            X_imputed = scaler.inverse_transform(X_imputed_scaled)
            X_imputed = pd.DataFrame(X_imputed, columns=cols_num_contexto, index=df.index)

            df[col] = X_imputed[col]

        else:
            df[[col]] = imputer_mediana.fit_transform(df[[col]])

    for col in columnas_validas:
        if col in dtypes_originales:
            if pd.api.types.is_integer_dtype(dtypes_originales[col]):
                df[col] = (
                    df[col]
                    .round()
                    .astype("Int64")
                )

    return df
