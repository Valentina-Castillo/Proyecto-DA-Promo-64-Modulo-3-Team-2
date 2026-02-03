# Proyecto-Optimizacion-de-Talento

Este trabajo analiza la satisfacción y retención de empleados mediante técnicas de análisis de datos. Se identifican factores clave que influyen en el compromiso laboral y se diseña un experimento A/B para validar hipótesis, generando información útil que apoye la toma de decisiones estratégicas de la empresa.

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
