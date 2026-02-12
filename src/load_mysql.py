"""
ETL: Carga del dataset HR (procesado) a MySQL (nextlevel_people) en 3FN.

Qué hace:
1) Lee el CSV procesado
2) Normaliza/convierte tipos a lo que espera SQL (int, 0/1, escalas)
3) Inserta valores únicos en tablas dimensión (departments, job_roles, etc.)
4) Mapea categorías a IDs (FKs) y carga employees

Requisitos:
- pandas
- sqlalchemy
- pymysql
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

# Ruta del CSV 
# Ruta absoluta al CSV procesado (independiente del directorio desde el que se ejecute)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = PROJECT_ROOT / "data" / "processed" / "hr_processed.csv"


# Encuestas / escalas 1..4 (según CHECKs típicos del dataset HR)
SURVEY_COLS_1_4 = [
    "environment_satisfaction",
    "job_involvement",
    "job_satisfaction",
    "relationship_satisfaction",
    "work_life_balance",
]

# Escala 1...4
PERFORMANCE_RANGE = (1, 4)


# =========================
# CONEXIÓN
# =========================
def build_engine():
    """Crea el engine de SQLAlchemy para MySQL usando PyMySQL."""
    url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(url)


# =========================
# UTILIDADES
# =========================
def normalize_string_series(s: pd.Series) -> pd.Series:
    """
    Normaliza strings para evitar nulos raros:
    - convierte a string
    - strip()
    - reemplaza placeholders típicos por 'Unknown'
    """
    s = s.astype(str).str.strip()
    return s.replace(
        {
            "": "Unknown",
            "None": "Unknown",
            "nan": "Unknown",
            "NaN": "Unknown",
            "NULL": "Unknown",
            "null": "Unknown",
        }
    )


def yes_no_to_bool01(s: pd.Series) -> pd.Series:
    """Convierte Yes/No a 1/0."""
    s = normalize_string_series(s).str.lower()
    return s.map({"yes": 1, "no": 0}).fillna(0).astype(int)


def force_int_no_na(s: pd.Series, default: int = 0) -> pd.Series:
    """
    Fuerza a int una serie numérica que puede venir como texto / con nulos.
    - si no puede convertir => NaN
    - NaN => default
    """
    out = pd.to_numeric(s, errors="coerce")
    out = out.fillna(default).astype(int)
    return out


# =========================
# MAPEOS ESPECÍFICOS
# =========================
def map_stock_option_level(s: pd.Series) -> pd.Series:
    """
    Convierte stock_option_level (Basic/Intermediate/Executive/Unknown) a 0..3.
    - Unknown -> 0
    - Basic -> 1
    - Intermediate -> 2
    - Executive -> 3
    """
    s = normalize_string_series(s).str.lower()
    mapping = {
        "unknown": 0,
        "basic": 1,
        "intermediate": 2,
        "executive": 3,
    }
    return s.map(mapping).fillna(0).astype(int)


def map_education_to_level(s: pd.Series) -> pd.Series:
    """
    Convierte education (texto) a education_level (1..5).
    Si algo no coincide => 3 (neutral/intermedio).
    """
    s = normalize_string_series(s).str.lower()
    mapping = {
        "no formal education": 1,
        "basic education": 2,
        "high school": 3,
        "associate degree": 3,
        "bachelor's degree": 4,
        "master's degree": 5,
        "phd": 5,
        "unknown": 3,
    }
    return s.map(mapping).fillna(3).astype(int)


def map_job_level_to_int(s: pd.Series) -> pd.Series:
    """
    Convierte job_level a 1..5.
    Soporta:
    - ya numérico
    - texto (Junior, Senior, etc.)
    """
    if pd.api.types.is_numeric_dtype(s):
        return force_int_no_na(s, default=3).clip(1, 5)

    s_norm = normalize_string_series(s).str.lower()
    mapping = {
        "entry level": 1,
        "junior": 2,
        "senior": 3,
        "manager": 4,
        "executive": 5,
        "unknown": 3,
    }
    out = s_norm.map(mapping)

    out = out.fillna(pd.to_numeric(s_norm, errors="coerce"))

    out = out.fillna(3).astype(int)
    out = out.clip(1, 5)
    return out


def map_survey_to_1_4(s: pd.Series) -> pd.Series:
    """
    Convierte columnas de encuestas a escala 1..4 (para cumplir CHECKs).
    Regla:
    - Si ya es numérico => convertir, NaN -> 3, clip 1..4
    - Si es texto => mapear si coincide; si no => 3
    """
    # Si ya es numérico:
    if pd.api.types.is_numeric_dtype(s):
        out = pd.to_numeric(s, errors="coerce").fillna(3).astype(int)
        return out.clip(1, 4)

    s_norm = normalize_string_series(s).str.lower()

    mapping = {
        "very low": 1,
        "low": 2,
        "medium": 3,
        "high": 4,
    }

    out = s_norm.map(mapping)

    out = out.fillna(pd.to_numeric(s_norm, errors="coerce"))

    out = out.fillna(3).astype(int)
    return out.clip(1, 4)


def map_performance_rating(s: pd.Series) -> pd.Series:
    """
    Normaliza performance_rating para cumplir CHECK.
    Por defecto lo dejamos en 1..4 (cámbialo arriba si tu CHECK es 1..5).
    """
    lo, hi = PERFORMANCE_RANGE

    if pd.api.types.is_numeric_dtype(s):
        out = pd.to_numeric(s, errors="coerce").fillna(hi).astype(int)  # suele ser 3/4 en HR
        return out.clip(lo, hi)

    s_norm = normalize_string_series(s).str.lower()
    out = pd.to_numeric(s_norm, errors="coerce").fillna(hi).astype(int)
    return out.clip(lo, hi)


# =========================
# DIMENSIONES (INSERT + MAP)
# =========================
def insert_dimension_values(conn, table: str, name_col: str, values: list[str]) -> None:
    """Inserta valores en dimensión sin duplicar (usa UNIQUE + INSERT IGNORE)."""
    stmt = text(f"INSERT IGNORE INTO {table} ({name_col}) VALUES (:val)")
    for v in values:
        conn.execute(stmt, {"val": v})


def fetch_dimension_map(conn, table: str, id_col: str, name_col: str) -> dict[str, int]:
    """Devuelve dict {nombre: id} de una dimensión."""
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

    # Columnas mínimas que necesitamos
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
        "education",
        "job_level",
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"❌ Faltan columnas requeridas en el CSV: {missing}")

    print("🧹 2) Normalizando categóricas y booleans...")
    # Dimensiones
    df["department"] = normalize_string_series(df["department"])
    df["job_role"] = normalize_string_series(df["job_role"])
    df["education_field"] = normalize_string_series(df["education_field"])
    df["business_travel"] = normalize_string_series(df["business_travel"])
    df["marital_status"] = normalize_string_series(df["marital_status"])
    df["gender"] = normalize_string_series(df["gender"])

    # Flags
    df["attrition"] = yes_no_to_bool01(df["attrition"])
    df["over_time"] = yes_no_to_bool01(df["over_time"])

    # Stock option (si no existe, lo ponemos 0)
    if "stock_option_level" in df.columns:
        df["stock_option_level"] = map_stock_option_level(df["stock_option_level"])
    else:
        df["stock_option_level"] = 0

    # Encuestas 1..4 (CLAVE para no violar CHECKs)
    for c in SURVEY_COLS_1_4:
        if c in df.columns:
            df[c] = map_survey_to_1_4(df[c])
        else:
            # si faltase, ponemos neutral 3 (cumple CHECK)
            df[c] = 3

    # Performance rating (según tu CHECK)
    if "performance_rating" in df.columns:
        df["performance_rating"] = map_performance_rating(df["performance_rating"])
    else:
        # si falta, ponemos el máximo permitido (suele ser 4)
        df["performance_rating"] = PERFORMANCE_RANGE[1]

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

    # education_level (texto -> 1..5)
    df["education_level"] = map_education_to_level(df["education_level"]).clip(1, 5)

    # job_level (texto/num -> 1..5)
    df["job_level"] = map_job_level_to_int(df["job_level"]).clip(1, 5)

    print("✅ 4) Validando y forzando tipos numéricos...")
    # Estas columnas deben ser numéricas e ir sin nulos (NOT NULL en SQL)
    must_int_cols_default0 = [
        "source_employee_id",
        "age",
        "education_level",
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
        # encuestas:
        *SURVEY_COLS_1_4,
        "performance_rating",
        "job_level",
    ]

    for c in must_int_cols_default0:
        if c not in df.columns:
            raise ValueError(f"❌ Falta columna requerida para SQL: {c}")
        df[c] = force_int_no_na(df[c], default=0)

    # Ajustes finales para CHECKs (blindaje)
    for c in SURVEY_COLS_1_4:
        df[c] = df[c].clip(1, 4)

    df["performance_rating"] = df["performance_rating"].clip(PERFORMANCE_RANGE[0], PERFORMANCE_RANGE[1])
    df["education_level"] = df["education_level"].clip(1, 5)
    df["job_level"] = df["job_level"].clip(1, 5)

    # salary_hike_pct suele ser 0..100
    df["salary_hike_pct"] = df["salary_hike_pct"].clip(0, 100)

    print("🔌 5) Conectando a MySQL...")
    engine = build_engine()

    with engine.begin() as conn:
        # Para evitar duplicados / ejecuciones repetidas:
        print("🧨 5.1) Limpiando tabla employees (TRUNCATE)...")
        conn.execute(text("SET FOREIGN_KEY_CHECKS=0;"))
        conn.execute(text("TRUNCATE TABLE employees;"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS=1;"))

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

        # Si alguna FK quedase NaN, es que hay una categoría que no se insertó en dimensión
        fk_cols = ["department_id", "job_role_id", "education_field_id", "business_travel_id", "marital_status_id", "gender_id"]
        if df[fk_cols].isna().any().any():
            bad = df.loc[df[fk_cols].isna().any(axis=1), ["source_employee_id", "department", "job_role", "education_field", "business_travel", "marital_status", "gender"]].head(10)
            raise ValueError(f"❌ Hay filas con FKs sin mapear. Ejemplos:\n{bad}")

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

        # Último blindaje por si acaso
        df_employees["environment_satisfaction"] = df_employees["environment_satisfaction"].clip(1, 4)
        df_employees["job_involvement"] = df_employees["job_involvement"].clip(1, 4)
        df_employees["job_satisfaction"] = df_employees["job_satisfaction"].clip(1, 4)
        df_employees["relationship_satisfaction"] = df_employees["relationship_satisfaction"].clip(1, 4)
        df_employees["work_life_balance"] = df_employees["work_life_balance"].clip(1, 4)
        df_employees["performance_rating"] = df_employees["performance_rating"].clip(PERFORMANCE_RANGE[0], PERFORMANCE_RANGE[1])

        print(f"🚀 10) Insertando employees: {df_employees.shape[0]} filas...")
        df_employees.to_sql("employees", con=conn, if_exists="append", index=False)

    print("✅ Carga completada correctamente.")
    print(f"📌 Filas insertadas en employees: {df.shape[0]}")


if __name__ == "__main__":
    load_hr_to_mysql()