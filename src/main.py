# ============================================================================
# MAIN ETL - EJECUCIÓN COMPLETA (LIMPIEZA + EXPORT + CARGA A MYSQL)
# ============================================================================

from pathlib import Path

import pipeline as pl
import load_mysql as lm


def main():
    """
    Ejecuta el flujo completo del ETL:
    1) Limpieza
    2) Exportación CSV procesado
    3) Carga en MySQL
    """

    project_root = Path(__file__).resolve().parents[1]

    input_path = project_root / "data" / "raw" / "hr.csv"
    output_path = project_root / "data" / "processed" / "hr_processed.csv"

    pl.run_cleaning_pipeline(
        input_path=input_path,
        output_path=output_path,
        mostrar_resumen_columnas=True
    )

    lm.load_hr_to_mysql()


if __name__ == "__main__":
    main()