"Análisis de datos de proyectos de investigación y producción de profesores CCYT-UACM."

from math import pi
from collections import defaultdict
import pandas as pd
import numpy as np
from bokeh.palettes import interp_palette as myPalette, Set3_12 as modif
from bokeh.plotting import figure, show
from bokeh.transform import cumsum
from bokeh.layouts import gridplot
from pyparsing import Any

def lee_excel(nombre, hoja, encabezados=1):
    "Lee la hoja de un archivo Excel con encabezados dados."
    return pd.read_excel(nombre, sheet_name=hoja, header=encabezados)

# recorta cadenas, y la prepara para aplicarla a un array
def _recorta(s, length):
    return s[:length]
recorta = np.vectorize(_recorta, otypes=[np.str])

def histogramas(archivo, hoja=0, encabezados=1, etiqueta='proyectos',
                accion: defaultdict[Any, str]=None):
    "Grafica histogramas tipo pastel de las columnas de una tabla."
    tabla = lee_excel(archivo, hoja, encabezados=encabezados)

    print(tabla.columns)
    # Todas las columnas de la tabla de proyectos
    cols = tabla.columns
    lista_figs = []

    for col in cols:
        # Se brinca columnas no interesantes
        if col in accion['elimina']:
            continue

        table = tabla[pd.notna(tabla[col])].copy()
        tcol = table[col].to_numpy().astype(str)

        if len(tcol) == 0:
            continue

        # Recorta a n caracteres ciertas columnas (bins mas grandes)
        if col in accion['recorta7']:
            table[col] = recorta(tcol, 7)

         # Recorta a n caracteres ciertas columnas (bins mas grandes)
        elif col in accion['recorta4']:
            table[col] = recorta(tcol, 4)

        # Recorta a n caracteres ciertas columnas (bins mas grandes)
        elif col in accion['recorta3']:
            table[col] = recorta(tcol, 3)

        # crea nueva tabla con frecuencias
        data = table[col].value_counts().reset_index(
            name=etiqueta).rename(columns={'index': col})

        # Calcula porcentajes
        data['pct'] = 100 * data[etiqueta] / \
            data[etiqueta].sum()

        # Calcula tamaño de rebanada
        data['angulo'] = data['pct'] * 2 * pi / 100

        # Asigna color
        data['color'] = myPalette(modif, len(data))

        # Ordena si es preciso
        if col in accion['ordena']:
            data[col] = data[col].astype(str)
            data = data.sort_values(by=col)  # de menor a mayor

        if col in accion['rordena']:
            data = data.sort_values(by=col, ascending=False)  # de mayor a menor


        # recorta textos (demasiado largos) para la 'leyenda'
        data['legend'] = recorta(data[col].to_numpy().astype(str), 20)

        fig = figure(height=350, title=col, toolbar_location=None,
                tools="hover",
                tooltips=[(f"{col}", f"@{{{col}}}"), 
                            (f"{etiqueta}", f"@{{{etiqueta}}}"),
                            ("pct", "@pct%")], x_range=(-0.5, 1.0))

        fig.wedge(x=0, y=1, radius=0.4,
                start_angle=cumsum('angulo', include_zero=True), end_angle=cumsum('angulo'),
                line_color="white", fill_color='color', legend_field='legend', source=data)

        fig.axis.axis_label = None
        fig.axis.visible = False
        fig.grid.grid_line_color = None
        lista_figs.append(fig)

    grid = gridplot(lista_figs, ncols=2)
    show(grid)
