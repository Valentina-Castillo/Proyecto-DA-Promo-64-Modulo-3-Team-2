"""
ETL: Carga del dataset HR (procesado) a MySQL (nextlevel_people) en 3FN.

Qué hace:
1) Lee el CSV procesado (data/processed/hr_processed.csv)
2) Prepara el dataframe "db_ready" con:
   - Tipos compatibles con SQL (int, 0/1, etc.)
   - Conversión de textos a niveles numéricos (education_level, job_level, stock_option_level)
3) Inserta valores únicos en tablas dimensión (departments, job_roles, etc.)
4) Mapea categorías a IDs (FKs) y carga employees

Requisitos:
- pandas
- sqlalchemy
- pymysql

Ejecución recomendada desde la raíz del repo:
python -m src.etl_load_hr_mysql
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text


# =========================
# CONFIGURACIÓN
# =========================
DB_USER = "root"
DB_PASSWORD = "1234"
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "nextlevel_people"

# Ruta del CSV (según tu estructura)
# OJO: esta ruta asume que ejecutas el script desde una carpeta "madre"
# donde existe el directorio "Proyecto-DA-Promo-64-Modulo-3-Team-2".
CSV_PATH = Path("Proyecto-DA-Promo-64-Modulo-3-Team-2") / "data" / "processed" / "hr_processed.csv"


# =========================
# CONEXIÓN
# =========================
def build_engine():
    """
    Crea el engine de SQLAlchemy para MySQL usando PyMySQL.
    """
    url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(url)


# =========================
# FUNCIONES DE LIMPIEZA / MAPEO
# =========================
def normalize_string_series(s: pd.Series) -> pd.Series:
    """
    Normaliza strings:
    - convierte a string
    - strip()
    - reemplaza placeholders típicos a 'Unknown'
    """
    s = s.astype(str).str.strip()
    s = s.replace(
        {
            "": "Unknown",
            "None": "Unknown",
            "nan": "Unknown",
            "NaN": "Unknown",
            "NULL": "Unknown",
            "null": "Unknown",
        }
    )
    return s


def yes_no_to_bool01(s: pd.Series) -> pd.Series:
    """
    Convierte Yes/No a 1/0.
    """
    s = normalize_string_series(s).str.lower()
    return s.map({"yes": 1, "no": 0}).fillna(0).astype(int)


def map_stock_option_level(s: pd.Series) -> pd.Series:
    """
    Convierte stock_option_level (Basic/Intermediate/Executive/Unknown) a 0..3.
    - Unknown -> 0
    - Basic -> 1
    - Intermediate -> 2
    - Executive -> 3

    También arregla el caso en el que vengan "NaN" como texto.
    """
    s = normalize_string_series(s).str.lower()

    mapping = {
        "unknown": 0,
        "basic": 1,
        "intermediate": 2,
        "executive": 3,
    }

    out = s.map(mapping).fillna(0).astype(int)
    return out


def map_education_to_level(s: pd.Series) -> pd.Series:
    """
    Convierte education (texto) a education_level (1..5).

    IMPORTANTE: Ajusta el diccionario si tus etiquetas exactas difieren.
    """
    s = normalize_string_series(s).str.lower()

    mapping = {
        "no formal education": 1,
        "basic education": 2,
        "high school": 3,
        "associate degree": 3,   # decisión razonable si existe
        "bachelor's degree": 4,
        "master's degree": 5,
        "phd": 5,
        "unknown": 3,
    }

    out = s.map(mapping).fillna(3).astype(int)
    return out


def map_job_level_to_int(s: pd.Series) -> pd.Series:
    """
    Convierte job_level a 1..5.

    En algunos datasets viene ya numérico (1..5).
    En otros viene como texto (Junior, Senior, etc.).
    Esta función soporta ambos casos.
    """
    # Si ya es numérico, lo forzamos a int y ya
    if pd.api.types.is_numeric_dtype(s):
        return s.fillna(3).astype(int)

    s = normalize_string_series(s).str.lower()

    mapping = {
        "entry level": 1,
        "junior": 2,
        "senior": 3,
        "manager": 4,
        "executive": 5,
        "unknown": 3,
    }

    out = s.map(mapping)

    # Si vienen números como texto ("1", "2"...), intentamos convertir
    out = out.fillna(pd.to_numeric(s, errors="coerce"))

    out = out.fillna(3).astype(int)
    return out


def map_satisfaction_labels_to_numbers(s: pd.Series) -> pd.Series:
    """
    Convierte columnas de encuestas/satisfacción a números 1..4.

    Soporta:
    - Ya numérico -> se queda
    - Texto -> lo intenta mapear o convertir

    Si vuestras etiquetas exactas son diferentes, ajustad el diccionario.
    """
    if pd.api.types.is_numeric_dtype(s):
        return s.fillna(0).astype(int)

    s_norm = normalize_string_series(s).str.lower()

    mapping = {
        "nada satisfecho": 1,
        "muy insatisfecho": 1,
        "poco satisfecho": 2,
        "insatisfecho": 2,
        "satisfecho": 3,
        "muy satisfecho": 4,
        "unknown": 0,
    }

    out = s_norm.map(mapping)
    out = out.fillna(pd.to_numeric(s_norm, errors="coerce"))
    out = out.fillna(0).astype(int)
    return out


# =========================
# DIMENSIONES (INSERT + MAP)
# =========================
def insert_dimension_values(conn, table: str, name_col: str, values: list[str]) -> None:
    """
    Inserta valores en tabla dimensión sin duplicar.
    INSERT IGNORE aprovecha el UNIQUE en name_col.
    """
    stmt = text(f"INSERT IGNORE INTO {table} ({name_col}) VALUES (:val)")
    for v in values:
        conn.execute(stmt, {"val": v})


def fetch_dimension_map(conn, table: str, id_col: str, name_col: str) -> dict[str, int]:
    """
    Devuelve un diccionario {nombre: id} de la tabla dimensión.
    """
    rows = conn.execute(text(f"SELECT {id_col}, {name_col} FROM {table}")).fetchall()
    return {r[1]: int(r[0]) for r in rows}


# =========================
# ETL PRINCIPAL
# =========================
def load_hr_to_mysql() -> None:
    print("🔎 1) Leyendo CSV...")
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"No existe el archivo CSV en: {CSV_PATH.resolve()}")

    df = pd.read_csv(CSV_PATH)
    print(f"✅ CSV leído: {df.shape[0]} filas x {df.shape[1]} columnas")

    # ---- Validación mínima de columnas clave ----
    required_cols = [
        "id",
        "department",
        "job_role",
        "education_field",
        "business_travel",
        "marital_status",
        "gender",
        "attrition",
        "over_time",
        "education",  # texto
        "job_level",  # puede ser texto o número
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"❌ Faltan columnas requeridas en el CSV: {missing}")

    print("🧹 2) Normalizando categóricas y booleans...")
    # Categóricas de dimensiones
    df["department"] = normalize_string_series(df["department"])
    df["job_role"] = normalize_string_series(df["job_role"])
    df["education_field"] = normalize_string_series(df["education_field"])
    df["business_travel"] = normalize_string_series(df["business_travel"])
    df["marital_status"] = normalize_string_series(df["marital_status"])
    df["gender"] = normalize_string_series(df["gender"])

    # Booleans
    df["attrition"] = yes_no_to_bool01(df["attrition"])
    df["over_time"] = yes_no_to_bool01(df["over_time"])

    # Stock option level
    if "stock_option_level" in df.columns:
        df["stock_option_level"] = map_stock_option_level(df["stock_option_level"])
    else:
        df["stock_option_level"] = 0

    # Encuestas (si existen)
    survey_cols = [
        "environment_satisfaction",
        "job_involvement",
        "job_satisfaction",
        "performance_rating",
        "relationship_satisfaction",
        "work_life_balance",
    ]
    for c in survey_cols:
        if c in df.columns:
            df[c] = map_satisfaction_labels_to_numbers(df[c])
        else:
            # Si no existen en el CSV, creamos 0 (pero OJO: tu SQL las tiene NOT NULL).
            # Ideal: que existan en el CSV. Si no, se insertará 0.
            df[c] = 0

    print("🔁 3) Renombrando columnas para SQL + mapeando niveles...")
    rename_map = {
        "id": "source_employee_id",
        "education": "education_level",
        "total_working_years": "total_years_worked",
        "training_times_last_year": "training_last_year",
        "percent_salary_hike": "salary_hike_pct",
        "years_with_curr_manager": "years_with_current_manager",
    }
    df = df.rename(columns=rename_map)

    # education_level: texto -> 1..5
    df["education_level"] = map_education_to_level(df["education_level"])

    # job_level: texto o número -> 1..5
    df["job_level"] = map_job_level_to_int(df["job_level"])

    print("✅ 4) Validando tipos básicos...")
    # Columnas que deben ser enteros sí o sí
    int_cols = [
        "source_employee_id",
        "age",
        "education_level",
        "environment_satisfaction",
        "job_involvement",
        "job_level",
        "job_satisfaction",
        "performance_rating",
        "relationship_satisfaction",
        "work_life_balance",
        "num_companies_worked",
        "total_years_worked",
        "training_last_year",
        "distance_from_home",
        "monthly_income",
        "daily_rate",
        "hourly_rate",
        "salary_hike_pct",
        "stock_option_level",
        "years_at_company",
        "years_in_current_role",
        "years_since_last_promotion",
        "years_with_current_manager",
        "over_time",
        "attrition",
    ]

    for c in int_cols:
        if c not in df.columns:
            raise ValueError(f"❌ Falta la columna requerida para SQL: {c}")
        if df[c].isna().any():
            raise ValueError(f"❌ Hay nulos en columna crítica: {c}")
        df[c] = pd.to_numeric(df[c], errors="raise").astype(int)

    print("🔌 5) Conectando a MySQL...")
    engine = build_engine()

    with engine.begin() as conn:
        print("📥 6) Insertando DIMENSIONES (sin duplicar)...")
        insert_dimension_values(conn, "departments", "department_name", sorted(df["department"].unique().tolist()))
        insert_dimension_values(conn, "job_roles", "job_role_name", sorted(df["job_role"].unique().tolist()))
        insert_dimension_values(conn, "education_fields", "education_field_name", sorted(df["education_field"].unique().tolist()))
        insert_dimension_values(conn, "business_travel_types", "business_travel_name", sorted(df["business_travel"].unique().tolist()))
        insert_dimension_values(conn, "marital_statuses", "marital_status_name", sorted(df["marital_status"].unique().tolist()))
        insert_dimension_values(conn, "genders", "gender_name", sorted(df["gender"].unique().tolist()))

        print("🗺️ 7) Creando mapas nombre -> id (FKs)...")
        dep_map = fetch_dimension_map(conn, "departments", "department_id", "department_name")
        role_map = fetch_dimension_map(conn, "job_roles", "job_role_id", "job_role_name")
        edu_map = fetch_dimension_map(conn, "education_fields", "education_field_id", "education_field_name")
        travel_map = fetch_dimension_map(conn, "business_travel_types", "business_travel_id", "business_travel_name")
        mar_map = fetch_dimension_map(conn, "marital_statuses", "marital_status_id", "marital_status_name")
        gen_map = fetch_dimension_map(conn, "genders", "gender_id", "gender_name")

        print("🔗 8) Mapeando IDs en el dataframe...")
        df["department_id"] = df["department"].map(dep_map).astype(int)
        df["job_role_id"] = df["job_role"].map(role_map).astype(int)
        df["education_field_id"] = df["education_field"].map(edu_map).astype(int)
        df["business_travel_id"] = df["business_travel"].map(travel_map).astype(int)
        df["marital_status_id"] = df["marital_status"].map(mar_map).astype(int)
        df["gender_id"] = df["gender"].map(gen_map).astype(int)

        print("🧾 9) Preparando tabla employees (solo columnas del esquema)...")
        employees_cols = [
            "source_employee_id",
            "department_id", "job_role_id", "education_field_id", "business_travel_id", "marital_status_id", "gender_id",
            "age", "education_level",
            "environment_satisfaction", "job_involvement", "job_level", "job_satisfaction", "performance_rating",
            "relationship_satisfaction", "work_life_balance",
            "num_companies_worked", "total_years_worked",
            "training_last_year", "distance_from_home",
            "monthly_income", "daily_rate", "hourly_rate",
            "salary_hike_pct", "stock_option_level",
            "years_at_company", "years_in_current_role", "years_since_last_promotion", "years_with_current_manager",
            "over_time", "attrition",
        ]
        df_employees = df[employees_cols].copy()

        print(f"🚀 10) Insertando employees: {df_employees.shape[0]} filas...")
        df_employees.to_sql("employees", con=conn, if_exists="append", index=False)

    print("✅ Carga completada correctamente.")
    print(f"📌 Filas insertadas en employees: {len(df)}")


if __name__ == "__main__":
    load_hr_to_mysql()
