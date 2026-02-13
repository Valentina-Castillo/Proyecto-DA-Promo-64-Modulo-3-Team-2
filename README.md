# Vertex Digital Solutions — HR Attrition Analytics

## End-to-End Data Pipeline, Relational Modelling & Predictive Analytics

Proyecto académico desarrollado por **Next Level People** como caso práctico de consultoría para Vertex Digital Solutions, en el marco de un programa formativo en Data Analytics.

---

### 1. Contexto de Negocio

Vertex Digital Solutions detecta un aumento en la rotación de empleados (attrition) y necesita entender los factores que están impulsando la salida del talento. El objetivo no es únicamente analizar los datos existentes, sino construir una solución estructurada, reproducible y escalable que permita transformar información dispersa en conocimiento accionable.

La compañía solicita:

- Diagnóstico de los drivers de rotación.
- Estandarización y limpieza del dataset.
- Diseño de una base de datos relacional normalizada.
- Preparación para modelado predictivo.
- Recomendaciones estratégicas basadas en evidencia.

---

### 2. Objetivos del Proyecto

- Garantizar calidad y consistencia de datos.
- Diseñar un modelo relacional en Tercera Forma Normal (3FN).
- Construir un pipeline ETL reproducible en Python.
- Generar un dataset analíticamente robusto.
- Desarrollar un modelo predictivo de riesgo de attrition (en progreso).

---

### 3. Descripción del Dataset

Archivo original: data/raw/hr.csv  
Filas originales: 1474  
Columnas originales: 35  

Tras el proceso de limpieza:

Archivo procesado: data/processed/hr_processed.csv  
Filas finales: 1470  
Columnas finales: 31  
Variable objetivo: attrition (clasificación binaria: Yes/No)

El identificador original (employee_number) se conserva como source_employee_id en la base de datos para mantener trazabilidad.

---

### 4. Arquitectura de la Solución

Flujo completo del proyecto:

RAW CSV  
→ Data Cleaning & Feature Engineering (Python)  
→ Processed CSV  
→ MySQL Database (3FN)  
→ Exploratory Analysis  
→ Predictive Modelling  

La arquitectura separa claramente las fases de ingesta, transformación, almacenamiento y análisis.

---

### 5. Estructura del Repositorio

```text
.
├── data/
│   ├── raw/hr.csv
│   └── processed/hr_processed.csv
│
├── notebooks/
│   ├── 00_EDA.ipynb
│   ├── 01_Limpieza.ipynb
│   ├── 02_Analisis_Descriptivo.ipynb
│   └── 03_Modelo_Predictivo.ipynb
│
├── reports/
│   ├── figures/
│   └── slides/Vertex_HR_Attrition_Presentation.pdf
│
├── sql/
│   ├── 01_create_schema_nextlevel_people.sql
│   └── 02_eda_load_validation.sql
│
├── src/
│   ├── cleaning_core.py
│   ├── imputation.py
│   ├── ordinal_mapping.py
│   ├── pipeline.py
│   ├── load_mysql.py
│   └── main.py
│
├── requirements.txt
└── README.md
```

---

### 6. Limpieza y Preparación de Datos

El pipeline implementa:

- Normalización de nombres de columnas a snake_case.
- Corrección de inconsistencias en valores categóricos.
- Estandarización de escalas ordinales (satisfacción, educación, job level, stock options, performance rating).
- Tratamiento de valores nulos según tipología de variable.
- Conversión explícita de tipos para asegurar consistencia en la carga a SQL.
- Preparación del dataset para análisis descriptivo y modelado predictivo.

La lógica de transformación se encuentra modularizada en src/cleaning_core.py, src/imputation.py y src/ordinal_mapping.py.

---

### 7. Diseño de Base de Datos (MySQL — 3FN)

Base de datos: nextlevel_people

Tablas dimensión:

- departments
- job_roles
- education_fields
- business_travel_types
- marital_statuses
- genders

Tabla principal:

employees

Incluye:

- employee_id (Primary Key autoincrement)
- source_employee_id (único para trazabilidad)
- Foreign Keys a tablas dimensión
- Variables numéricas y flags
- Restricciones CHECK para garantizar integridad de datos

El diseño en Tercera Forma Normal elimina redundancia y asegura consistencia relacional.

#### Diagrama Entidad-Relación (ERD)

![ERD NextLevel People](docs/erd_nextlevel_people.png)

---

### 8. Pipeline ETL (Python)

El archivo src/main.py orquesta el flujo completo:

1. Lectura del CSV raw.
2. Ejecución del pipeline de limpieza.
3. Generación del CSV procesado.
4. Carga estructurada a MySQL mediante SQLAlchemy.

El sistema permite ejecutar el flujo completo de manera reproducible desde la raíz del proyecto.  
El diseño modular facilita la mantenibilidad, escalabilidad y reutilización del pipeline.

---

### 9. Análisis Exploratorio (In Progress)

Notebook: notebooks/02_Analisis_Descriptivo.ipynb

Se integrarán:

- Identificación de principales drivers de attrition.
- Segmentación por departamento y rol.
- Impacto de satisfacción, overtime y salario.
- Insights estratégicos para reducción de rotación.

---

### 10. Modelado Predictivo (In Progress)

Notebook: notebooks/03_Modelo_Predictivo.ipynb

Se integrarán:

- Modelo seleccionado.
- Métricas (Accuracy, Precision, Recall, F1-score, ROC AUC).
- Variables con mayor importancia predictiva.
- Interpretación del impacto en negocio.

---

### 11. Impacto en el Negocio (In Progress)

Esta sección se completará una vez finalizado el análisis descriptivo y el modelo predictivo.

El objetivo es traducir los hallazgos técnicos en impacto estratégico para el negocio, incluyendo:

- Identificación de perfiles con mayor riesgo de rotación.
- Factores organizativos con mayor influencia en la attrition.
- Estimación del impacto económico potencial de la rotación.
- Recomendaciones accionables para reducir la fuga de talento.
- Priorización de iniciativas basadas en evidencia cuantitativa.

Cuando el análisis esté cerrado, aquí se integrarán:

- Métricas clave de negocio.
- Escenarios de reducción de rotación.
- Estimaciones de ahorro potencial.
- Propuesta de roadmap estratégico.

Estado actual: En progreso.

---

### 12. Tecnologías Utilizadas

#### Programming & Data Processing

- Python 3.x
- Pandas
- NumPy

#### Data Visualization

- Matplotlib
- Seaborn

#### Machine Learning (in progress)

- Scikit-learn

#### Database & Data Modelling

- MySQL 8.x
- MySQL Workbench
- SQLAlchemy

#### Development & Version Control

- Jupyter Notebook
- Git
- GitHub

---

### 13. Limitaciones y Mejoras Futuras

Aunque el proyecto implementa un pipeline completo end-to-end, existen mejoras que podrían reforzar su robustez, escalabilidad y preparación para entornos productivos:

- Implementación de validaciones automáticas de calidad de datos previas a la carga.
- Uso de variables de entorno (.env) para la gestión segura de credenciales.
- Integración de logging estructurado para monitorización del pipeline.
- Incorporación de tests unitarios en las funciones principales de transformación.
- Parametrización del pipeline para facilitar su reutilización en otros datasets.
- Mejora del modelo predictivo mediante validación cruzada y optimización de hiperparámetros.

Estas mejoras permitirían aumentar la mantenibilidad, reproducibilidad y madurez técnica del proyecto.

---

### 14. Cómo Reproducir el Proyecto

1. Crear entorno virtual:

    python -m venv .venv

    Activación:

    Windows:
    .venv\Scripts\Activate.ps1

    Mac/Linux:
    source .venv/bin/activate

2. Instalar dependencias:

    pip install -r requirements.txt

3. Crear esquema MySQL ejecutando:

    sql/01_create_schema_nextlevel_people.sql

4. Ejecutar pipeline completo desde la raíz del proyecto:

    python src/main.py

Esto generará data/processed/hr_processed.csv y cargará las dimensiones y la tabla employees en la base de datos nextlevel_people.

Validación opcional:

sql/02_eda_load_validation.sql

---

### 15. Equipo — Next Level People

Scrum Master  
Valentina Castillo  
Coordinación & Metodología Ágil  
Planificación de sprints, organización del equipo y seguimiento estratégico del proyecto.  
[LinkedIn](https://www.linkedin.com/in/valentina-castillo-escobar-191863202/) | [GitHub](https://github.com/Valentina-Castillo)

Data Team  
Arantxa Barea  
Análisis & Modelado  
Exploración de datos, generación de insights, análisis exploratorio y predictivo.  
[LinkedIn](https://www.linkedin.com/in/arantxa-barea/) | [GitHub](https://github.com/arantxa-90)

Data Team  
Nieves Sánchez  
Arquitectura & Automatización  
Diseño de base de datos, estructuración del repositorio, desarrollo de la ETL y documentación.  
[LinkedIn](https://www.linkedin.com/in/nieves-sanchez-data) | [GitHub](https://github.com/nieves-sanchez)

---

### 16. Estado del Proyecto

Pipeline de datos: Completado  
Modelado de base de datos: Completado  
Análisis exploratorio: En progreso  
Modelado predictivo: En progreso  
Presentación final: Pendiente de integración  

---

### 17. Aviso Legal

Proyecto desarrollado con fines educativos y de portfolio.  
No contiene datos reales de empleados ni información sensible empresarial.
