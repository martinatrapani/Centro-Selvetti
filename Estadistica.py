import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import to_rgb

# Paleta
TEAL = "#1EA2C4"
CORAL = "#E751CE"
TERRACOTA = "#FF3700"
AZUL_STEEL = "#001AFF"
CELESTE = "#59EB9B"


def crear_Histograma(columna, escala=10, color=TEAL, color_poligono=CORAL,
                     titulo=None, mostrar_porcentaje=True, mostrar_poligono=True):
    datos = columna.dropna()
    total = len(datos)

    fig, ax = plt.subplots(figsize=(10, 6))

    # El histograma devuelve los bordes de cada barra
    alturas_h, bordes, barras = ax.hist(datos, bins=escala, color=color,
                                        edgecolor='black', linewidth=1.2,
                                        alpha=0.9)

    # Polígono de frecuencias: une los puntos medios de cada barra
    if mostrar_poligono:
        centros = (bordes[:-1] + bordes[1:]) / 2
        ancho = bordes[1] - bordes[0]
        x_pol = np.concatenate(([bordes[0] - ancho / 2], centros,
                                [bordes[-1] + ancho / 2]))
        y_pol = np.concatenate(([0], alturas_h, [0]))
        ax.plot(x_pol, y_pol, color=color_poligono, linewidth=2.5,
                marker='o', markersize=6, markeredgecolor='white', zorder=4,
                label='Polígono de frecuencias')

    # Etiquetas con la cantidad y el porcentaje arriba de cada barra
    alturas = [int(b.get_height()) for b in barras]
    if mostrar_porcentaje:
        etiquetas = [f'{n} ({n / total * 100:.1f}%)' if n > 0 else ''
                     for n in alturas]
    else:
        etiquetas = [str(n) if n > 0 else '' for n in alturas]
    ax.bar_label(barras, labels=etiquetas, padding=8, fontsize=10)

    # Los números del eje X quedan justo en los bordes de las barras
    ax.set_xticks(bordes)
    ax.set_xticklabels([f'{b:.0f}' if float(b).is_integer() else f'{b:.1f}'
                        for b in bordes])

    # Media y mediana como puntos sobre el eje X
    media = datos.mean()
    mediana = datos.median()
    ax.scatter(media, 0, s=140, color='#264653', marker='o',
               edgecolor='white', linewidth=1.5, zorder=5, clip_on=False,
               label=f'Media: {media:.1f}')
    ax.scatter(mediana, 0, s=90, color='#E9C46A', marker='D',
               edgecolor='white', linewidth=1.5, zorder=6, clip_on=False,
               label=f'Mediana: {mediana:.1f}')

    ax.set_title(titulo or f'Distribución de {columna.name}',
                 fontsize=16, fontweight='bold', pad=15)
    ax.set_xlabel(columna.name, fontsize=12)
    ax.set_ylabel('Frecuencia', fontsize=12)

    ax.grid(axis='y', linestyle='--', alpha=0.4)
    ax.set_axisbelow(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.margins(y=0.12)
    ax.set_ylim(bottom=0)
    ax.legend(frameon=False, fontsize=11)

    plt.tight_layout()
    plt.show()


def crear_Torta(columna, titulo=None, max_categorias=6, dona=False, colores=None):
    """colores puede ser una lista, o un diccionario {categoría: color}."""
    conteo = columna.dropna().value_counts()

    # Agrupamos las categorías menos frecuentes en "Otros"
    if len(conteo) > max_categorias:
        principales = conteo.iloc[:max_categorias - 1]
        otros = conteo.iloc[max_categorias - 1:].sum()
        conteo = pd.concat([principales, pd.Series({'Otros': otros})])

    if colores is None:
        colores = plt.cm.Set2(np.linspace(0, 1, len(conteo)))
    elif isinstance(colores, dict):
        # Categorías sin color asignado reciben gris
        colores = [colores.get(cat, "#C775AC") for cat in conteo.index]

    fig, ax = plt.subplots(figsize=(9, 7))

    wedges, textos, porcentajes = ax.pie(
        conteo.values,
        colors=colores,
        autopct=lambda p: f'{p:.1f}%' if p >= 3 else '',
        startangle=90,
        counterclock=False,
        pctdistance=0.8 if dona else 0.65,
        wedgeprops=dict(edgecolor='white', linewidth=2,
                        width=0.45 if dona else None),
        textprops=dict(fontsize=11, fontweight='bold'),
    )

    # Texto blanco sobre colores oscuros, oscuro sobre colores claros
    for w, t in zip(wedges, porcentajes):
        r, g, b = to_rgb(w.get_facecolor())
        luminosidad = 0.299 * r + 0.587 * g + 0.114 * b
        t.set_color('white' if luminosidad < 0.6 else '#264653')

    # Leyenda al costado con cantidades
    etiquetas = [f'{cat}  ({n})' for cat, n in zip(conteo.index, conteo.values)]
    ax.legend(wedges, etiquetas, title=columna.name, loc='center left',
              bbox_to_anchor=(1, 0.5), frameon=False, fontsize=11, title_fontsize=12)

    ax.set_title(titulo or f'Distribución de {columna.name}',
                 fontsize=16, fontweight='bold', pad=15)
    ax.axis('equal')

    plt.tight_layout()
    plt.show()


def crear_Barras(columna, titulo=None, max_categorias=10, horizontal=True,
                 ordenar=True, color=TERRACOTA, mostrar_porcentaje=True):
    conteo = columna.dropna().value_counts()

    # Ordenamos de mayor a menor, o por el orden natural de las categorías
    conteo = conteo if ordenar else conteo.sort_index()

    # Agrupamos las categorías menos frecuentes en "Otros"
    if len(conteo) > max_categorias:
        principales = conteo.iloc[:max_categorias - 1]
        otros = conteo.iloc[max_categorias - 1:].sum()
        conteo = pd.concat([principales, pd.Series({'Otros': otros})])

    total = conteo.sum()
    categorias = [str(c) for c in conteo.index]

    fig, ax = plt.subplots(figsize=(10, 6))

    if horizontal:
        barras = ax.barh(categorias, conteo.values, color=color,
                         edgecolor='white', linewidth=1.2, alpha=0.9)
        ax.invert_yaxis()
        ax.set_xlabel('Frecuencia', fontsize=12)
        ax.set_ylabel(columna.name, fontsize=12)
        ax.grid(axis='x', linestyle='--', alpha=0.4)
    else:
        barras = ax.bar(categorias, conteo.values, color=color,
                        edgecolor='white', linewidth=1.2, alpha=0.9)
        ax.set_xlabel(columna.name, fontsize=12)
        ax.set_ylabel('Frecuencia', fontsize=12)
        ax.grid(axis='y', linestyle='--', alpha=0.4)
        if len(categorias) > 5 or max(len(c) for c in categorias) > 10:
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

    # Etiquetas con la cantidad (y el porcentaje) en cada barra
    if mostrar_porcentaje:
        etiquetas = [f'{n} ({n / total * 100:.1f}%)' for n in conteo.values]
    else:
        etiquetas = [str(n) for n in conteo.values]
    ax.bar_label(barras, labels=etiquetas, padding=4, fontsize=10)

    ax.set_title(titulo or f'Distribución de {columna.name}',
                 fontsize=16, fontweight='bold', pad=15)
    ax.set_axisbelow(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    if horizontal:
        ax.margins(x=0.15)
    else:
        ax.margins(y=0.12)

    plt.tight_layout()
    plt.show()


def crear_BoxPlot(columna, agrupar_por=None, titulo=None, horizontal=True,
                  color=TEAL, mostrar_valores=True):
    if agrupar_por is None:
        grupos = {str(columna.name): columna.dropna()}
    else:
        tmp = pd.DataFrame({'v': columna, 'g': agrupar_por}).dropna()
        grupos = {str(g): s['v'] for g, s in tmp.groupby('g')}

    etiquetas = list(grupos.keys())
    datos = list(grupos.values())
    n = len(datos)

    colores = [color] if n == 1 else plt.cm.Set2(np.linspace(0, 1, n))

    alto = 4.5 if (horizontal and n == 1) else 6
    fig, ax = plt.subplots(figsize=(10, alto))

    bp = ax.boxplot(
        datos, vert=not horizontal, patch_artist=True, widths=0.5,
        showmeans=True,
        meanprops=dict(marker='o', markerfacecolor=CORAL,
                       markeredgecolor='white', markeredgewidth=1.5,
                       markersize=10),
        medianprops=dict(color='#264653', linewidth=2.5),
        whiskerprops=dict(color='#555555', linewidth=1.5),
        capprops=dict(color='#555555', linewidth=1.5),
        flierprops=dict(marker='o', markerfacecolor='#999999',
                        markeredgecolor='white', markersize=6, alpha=0.7),
    )

    for caja, c in zip(bp['boxes'], colores if n > 1 else colores * n):
        caja.set(facecolor=c, edgecolor='black', linewidth=1.5, alpha=0.9)

    posiciones = range(1, n + 1)
    if horizontal:
        ax.set_yticks(list(posiciones))
        ax.set_yticklabels(etiquetas)
        ax.set_xlabel(columna.name, fontsize=12)
        ax.grid(axis='x', linestyle='--', alpha=0.4)
    else:
        ax.set_xticks(list(posiciones))
        ax.set_xticklabels(etiquetas)
        ax.set_ylabel(columna.name, fontsize=12)
        ax.grid(axis='y', linestyle='--', alpha=0.4)

    if mostrar_valores:
        for i, d in zip(posiciones, datos):
            q1, med, q3 = d.quantile([0.25, 0.5, 0.75])
            for v in (q1, med, q3):
                if horizontal:
                    ax.text(v, i + 0.33, f'{v:.1f}', ha='center',
                            va='bottom', fontsize=10, color='#333333')
                else:
                    ax.text(i + 0.33, v, f'{v:.1f}', ha='left',
                            va='center', fontsize=10, color='#333333')

    handles = [
        plt.Line2D([], [], marker='o', color='none', markerfacecolor=CORAL,
                   markeredgecolor='white', markersize=10, label='Media'),
        plt.Line2D([], [], color='#264653', linewidth=2.5, label='Mediana'),
    ]
    ax.legend(handles=handles, frameon=False, fontsize=11)

    ax.set_title(titulo or f'Distribución de {columna.name}',
                 fontsize=16, fontweight='bold', pad=15)
    ax.set_axisbelow(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.show()


url = 'https://docs.google.com/spreadsheets/d/1m5YCNWVu3Is4A9U3UVfEltZTOWYMZqwzd1S0fLX0kfg/export?format=csv&gid=1872966122'
df = pd.read_csv(url)

crear_Histograma(df['Edad del encuestado'], escala=np.arange(15, 80, 5))


crear_Barras(df['1.1.1 Cantidad de personas que definen qué se cocina en el hogar'])

crear_Torta(df['1.1.2 Género de quién/es definen qué se cocina'])
