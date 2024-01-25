"Análisis de datos de proyectos de investigación y producción de profesores CCYT-UACM."

from math import pi
from collections import defaultdict
import pandas as pd
import numpy as np
from bokeh.palettes import interp_palette as myPalette, Set3_12 as modif
from bokeh.plotting import figure, show
from bokeh.transform import cumsum
from bokeh.layouts import gridplot
from pyparsing import Any, Dict, List

def lee_excel(nombre, hoja, encabezados=1):
    "Lee la hoja de un archivo Excel con encabezados dados."
    return pd.read_excel(nombre, sheet_name=hoja, header=encabezados)

# recorta cadenas, y la prepara para aplicarla a un array
def _recorta(s, length):
    return s[:length]
recorta = np.vectorize(_recorta, otypes=[str])

def histogramas(archivo, hoja=0, encabezados=1, etiqueta='proyectos',
                accion: defaultdict[Any, str]=None):
    "Grafica histogramas tipo pastel de las columnas de una tabla."
    tabla = Lee(archivo).carga_hoja(devuelve_tabla=True, hoja=hoja, 
                                    encabezados=encabezados)

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


class Lee:
    def __init__(self, archivo):
        self.archivo = archivo
        self.hoja = 0
        self.encabezados = 1
        self.tabla = None

    def carga_hoja(self, devuelve_tabla=False, hoja=None, encabezados=None):
        """
        Ej de uso:
            tabla = Lee_datos("archivo.xlsx").carga_hoja(devuelve_tabla=True, hoja=1)
            procesa_dataframe(tabla)
        o
            datos_obj = Lee_datos("archivo.xlsx").carga_hoja(hoja=1)
            procesa_obj-tipo-Lee(datos_obj)
        """
        if hoja is not None:
            self.hoja = hoja
        if encabezados is not None:
            self.encabezados = encabezados
        else:
            self.encabezados = 1
        self.tabla = self.lee_excel(self.archivo, self.hoja, self.encabezados)
        return self.tabla if devuelve_tabla else self

    def lee_excel(self, nombre, hoja, encabezados):
        "Lee la hoja de un archivo Excel con encabezados dados."
        return pd.read_excel(nombre, sheet_name=hoja, header=encabezados)

    "EN PRUEBA"
    def cambia(self, columna_actual: str, busca_reemplaza: Dict=None):
        """
        columna_actual es la que determina que elementos de busca_reemplaza considerar.
        busca_reemplaza = {"columna0": replace0, ...}
        donde replaceN son duplas de la forma:
            replaceN = ([errorN0, errorN1, ...], reemplazoN)
        donde errorNM y reemplazoN son valores (por ejemplo, cadenas)
        Los valores errorN0, errorN1,... se rremplazarán por el valor reemplazoN
        reemplazoN usualmente es np.nan, pero hay que ponerlo
        replaceN = ([], "positivos") pone NaN en lo que no sean números positivos de columna_actual

        IMPORTANTE: SI modifica y devuelve self.tabla
        TODO
        """
        if busca_reemplaza[columna_actual] == ([], 'positivos'):
            self.tabla[columna_actual] = pd.to_numeric(self.tabla[columna_actual], errors='coerce')
            condicion = (self.tabla[columna_actual] <= 0) | self.tabla[columna_actual].isna()
            self.tabla[columna_actual] = self.tabla[columna_actual].mask(condicion, np.nan)
            return self.tabla
        if busca_reemplaza is None:
            return self.tabla
        for reemplazo, errores in busca_reemplaza.items():
            self.tabla[columna_actual] = self.tabla[columna_actual].replace(errores, reemplazo)
        return self.tabla

    