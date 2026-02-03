# Proyecto-Optimizacion-de-Talento

📊 Employee Retention & Job Satisfaction Analysis
Proyecto de Análisis de Datos — ABC Corporation

📄 Descripción
En el entorno empresarial altamente competitivo de hoy en día, la retención de empleados y la satisfacción en el trabajo son cuestiones críticas para cualquier organización. Este proyecto fue desarrollado en colaboración con ABC Corporation con el objetivo de identificar los factores clave que influyen en la satisfacción laboral y, en última instancia, en la retención de empleados.
A través de un análisis exploratorio de datos, transformaciones, visualizaciones y la creación de una base de datos estructurada, proporcionamos a ABC Corporation información valiosa para informar sus decisiones estratégicas.

🏢 Sobre ABC Corporation
ABC Corporation, fundada en 1980 en California, es una consultora tecnológica especializada en soluciones de Inteligencia Artificial (IA) y Machine Learning. Su objetivo principal es automatizar y optimizar procesos empresariales mediante tecnologías de vanguardia.
Se distingue por su equipo multidisciplinario compuesto por expertos en UX/UI, marketing, analistas, científicos de datos y otros campos relevantes, lo que permite ofrecer soluciones personalizadas adaptadas a cada cliente.


🗂️ Estructura del Proyecto [PENDIENTE]


📌 Fases del Proyecto

ºFase 1 — Análisis Exploratorio de Datos (EDA)
Exploración detallada del dataset hr.csv para comprender su estructura, tipos de datos, valores nulos, distribuciones y relaciones entre variables.

ºFase 2 — Transformación de los Datos
Limpieza, normalización, conversión de tipos de datos y aplicación de reglas empresariales mediante funciones en Python para garantizar la calidad e integridad de los datos.

ºFase 3 — Visualización de los Datos
Generación de visualizaciones descriptivas en Python que resaltan tendencias, áreas de mejora y fortalezas dentro de la empresa, acompañadas de análisis descriptivos.

ºFase 4 — Diseño de BBDD e Inserción de Datos
Definición de la estructura de la base de datos relacional (tablas, claves primarias, claves foráneas), su creación y la inserción inicial de datos de empleados.

ºFase 5 — Creación de una ETL (Bonus)
Automatización del proceso completo de Extracción → Transformación → Carga en un archivo .py, garantizando actualizaciones consistentes y de calidad en la base de datos.

🛠️ Tecnologías Utilizadas

Tecnología              Uso

-------------------------------------------------------------------
Python                   Análisis de datos, transformaciones y ETL.

-------------------------------------------------------------------
Pandas                   Manipulación y análisis de datos.

-------------------------------------------------------------------
Numpy

-------------------------------------------------------------------
Matplotlib/Seaborn     Visualización de datos

-------------------------------------------------------------------                                                     
MySQL Workbench       Diseño y gestión de la base de datos

-------------------------------------------------------------------
Jupyter Notebook      Desarrollo interactivo y EDAGit / GitHubControl de versiones y            
                      colaboración
                   
--------------------------------------------------------------------

📦 Dataset
El archivo hr.csv contiene la información de los empleados de ABC Corporation. Incluye variables relacionadas con datos personales, laborales y de satisfacción que permitirán realizar el análisis y modelado.

Tamaño: 237 KB

🎯 Objetivos del Proyecto

Consolidar conocimientos de librerias Python, análisis de datos,  y SQL.
Utilizar control de versiones en equipo (Git/GitHub).
Implementar Scrum como marco de referencia, basándonos en los valores de Agile.
Mejorar la comunicación entre miembros del equipo.
Desarrollar habilidades de comunicación pública al exponer el proyecto.

📅 Planificación — Sprints
El proyecto se desarrolla en 2 sprints siguiendo principios ágiles:

Sprint  |   Contenido
-----------------------------------------------------------------------

Sprint 1    Planning → Desarrollo (Fases 1, 2 y 3) → Review + Retro

Sprint 2    Planning → Desarrollo (Fases 4 y 5) → Review final + Demo

-----------------------------------------------------------------------




----------------------------

## Setup del entorno 🟦 Windows — PowerShell

1. Crear entorno virtual

    ```powershell
    python -m venv .venv
    ```

2. Activar entorno

    ```powershell
    .\.venv\Scripts\Activate.ps1
    ```

3. Instalar dependencias

    ```powershell
    pip install -r requirements.txt
    ```

📌 Si PowerShell bloquea la activación, ejecutar una sola vez:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Luego repetir el paso 2

## Setup del entorno 🟨 Windows — Git Bash

1. Crear entorno virtual

    ```bash
    python -m venv .venv
    ```

2. Activar entorno

    ```bash
    source .venv/Scripts/activate
    ```

3. Instalar dependencias

    ```bash
    pip install -r requirements.txt
    ```

## Setup del entorno 🟩 Linux / macOS (Terminal)

1. Crear entorno virtual

    ```bash
    python3 -m venv .venv
    ```

2. Activar entorno

    ```bash
    source .venv/bin/activate
    ```

3. Instalar dependencias

    ```bash
    pip install -r requirements.txt
    ```

✅ Comprobación rápida (opcional)

```bash
python -c "import pandas, numpy, seaborn, matplotlib, sklearn; print('Entorno OK')"
```
