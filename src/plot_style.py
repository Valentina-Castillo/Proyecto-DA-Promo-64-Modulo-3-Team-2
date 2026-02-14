"""
plot_style.py

Configuración centralizada de estilo para visualizaciones del proyecto
Next Level People — Vertex Digital Solutions.

Este módulo:
- Registra la tipografía Inter desde assets/fonts
- Configura Matplotlib con estilo corporativo
- Permite aplicar el mismo diseño en todos los notebooks

Uso:
from src.plot_style import apply_presentation_style
apply_presentation_style()
"""

import os
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm


def _register_inter_font():
    """
    Registra la tipografía Inter desde la carpeta assets/fonts.
    """
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    font_path = os.path.join(
        base_path,
        "assets",
        "fonts",
        "static",
        "Inter-VariableFont_opsz,wght.ttf",
    )

    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)
        plt.rcParams["font.family"] = "Inter"
    else:
        print("⚠ No se encontró la fuente Inter. Se usará la fuente por defecto.")


def apply_presentation_style():
    """
    Aplica el estilo corporativo de Next Level People a las gráficas.

    Colores:
    - Fondo oscuro corporativo
    - Texto en beige y turquesa
    - Líneas y elementos coherentes con la presentación
    """

    _register_inter_font()

    # Fondo general
    plt.rcParams["figure.facecolor"] = "#191919"
    plt.rcParams["axes.facecolor"] = "#191919"

    # Texto
    plt.rcParams["text.color"] = "#F1E0C6"
    plt.rcParams["axes.labelcolor"] = "#F1E0C6"
    plt.rcParams["xtick.color"] = "#F1E0C6"
    plt.rcParams["ytick.color"] = "#F1E0C6"
    plt.rcParams["axes.titleweight"] = "bold"

    # Títulos
    plt.rcParams["axes.titlesize"] = 18
    plt.rcParams["axes.labelsize"] = 12

    # Grid
    plt.rcParams["axes.grid"] = True
    plt.rcParams["grid.color"] = "#2A2A2A"
    plt.rcParams["grid.linestyle"] = "--"
    plt.rcParams["grid.alpha"] = 0.4

    # Leyenda
    plt.rcParams["legend.facecolor"] = "#191919"
    plt.rcParams["legend.edgecolor"] = "#2A2A2A"
    plt.rcParams["legend.fontsize"] = 10

    print("✅ Estilo corporativo aplicado correctamente.")
