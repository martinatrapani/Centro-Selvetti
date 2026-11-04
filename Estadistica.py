import pandas as pd
import matplotlib.pyplot as plt
import textwrap
import numpy as np
from matplotlib.colors import to_rgb

# Paleta
TEAL = "#1EA2C4"
CORAL = "#E751CE"
TERRACOTA = "#FF3700"
AZUL_STEEL = "#001AFF"
CELESTE = "#59EB9B"

COLORES_ESTILO = {
    'Sí': '#3B82F6',        # Azul brillante
    'No': '#EA4335',        # Rojo vibrante
    'No sabe': '#FBBF24',   # Amarillo
    'Ns/Nc': '#FBBF24'
}

#COLORES_ESTILO = {
#    'Mujer': '#3B82F6',        # Azul brillante
#    'Varón': '#EA4335',        # Rojo vibrante
#    'Mujer-Varón': '#FBBF24',   # Amarillo
#    'Se desconoce': "#06D625"
#}


AMARILLO = '#FBBF24'
COLOR_TEXTO = '#1F2937'
COLOR_GRIS = '#6B7280'


def crear_Histograma(columna, escala=10, color=TEAL, color_poligono=CORAL,
                     titulo=None, mostrar_porcentaje=True, mostrar_poligono=True):
    datos = columna.dropna()
    total = len(datos)

    # Si se pasan bordes (lista/range), se extienden para cubrir TODOS los datos
    if not isinstance(escala, (int, np.integer)):
        bins = list(escala)
        paso = bins[1] - bins[0]
        while bins[0] > datos.min():
            bins.insert(0, bins[0] - paso)
        while bins[-1] < datos.max():
            bins.append(bins[-1] + paso)
    else:
        bins = escala   # un entero ya cubre de la edad mínima a la máxima

    fig, ax = plt.subplots(figsize=(11, 6))

    alturas_h, bordes, barras = ax.hist(datos, bins=bins, color=color,
                                        edgecolor='black', linewidth=1.2,
                                        alpha=0.9)

    centros = (bordes[:-1] + bordes[1:]) / 2
    ancho = bordes[1] - bordes[0]

    # Polígono de frecuencias
    if mostrar_poligono:
        x_pol = np.concatenate(([bordes[0] - ancho / 2], centros,
                                [bordes[-1] + ancho / 2]))
        y_pol = np.concatenate(([0], alturas_h, [0]))
        ax.plot(x_pol, y_pol, color=color_poligono, linewidth=2.5,
                marker='o', markersize=6, markeredgecolor='white', zorder=4,
                label='Polígono de frecuencias')

    # Etiquetas arriba de cada punto del polígono (fondo transparente)
    for x, n in zip(centros, alturas_h):
        n = int(n)
        if n == 0:
            continue
        texto = f'{n} ({n / total * 100:.1f}%)' if mostrar_porcentaje else str(n)
        ax.annotate(texto, xy=(x, n), xytext=(0, 12),
                    textcoords='offset points',
                    ha='center', va='bottom', fontsize=10, zorder=7)

    # Eje X: un número en cada borde de barra
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
    ax.margins(y=0.15)
    ax.set_ylim(bottom=0)
    ax.legend(frameon=False, fontsize=11)

    plt.tight_layout()
    plt.show()


def crear_grafico_torta(columna, titulo=None, colores=COLORES_ESTILO,
                        color_defecto=AMARILLO, orden=None, angulo_inicio=90):
    conteo = columna.dropna().value_counts()
    if orden is not None:
        conteo = conteo.reindex(orden).dropna()

    total = int(conteo.sum())
    categorias = conteo.index.tolist()
    valores = conteo.values

    # Cada categoría usa su color; si no está en el diccionario, va amarillo
    lista_colores = [colores.get(c, color_defecto) for c in categorias]

    fig, ax = plt.subplots(figsize=(8, 6.5))

    # Sin bordes entre porciones, empezando desde arriba y en sentido horario
    wedges, _ = ax.pie(valores, colors=lista_colores, startangle=angulo_inicio,
                       counterclock=False,
                       wedgeprops=dict(edgecolor='white', linewidth=0))

    for w, cat, n in zip(wedges, categorias, valores):
        ang = np.deg2rad((w.theta1 + w.theta2) / 2)
        x, y = np.cos(ang), np.sin(ang)

        # Cantidad dentro de la porción
        ax.text(0.65 * x, 0.65 * y, f'{int(n)}', ha='center', va='center',
                fontsize=13, fontweight='bold', color=COLOR_TEXTO)

        # Línea que sale del borde de la porción hacia el nombre y el porcentaje
        lado = 1 if x >= 0 else -1
        ax.plot([x, 1.2 * x, 1.45 * lado], [y, 1.2 * y, 1.2 * y],
                color='#9CA3AF', linewidth=1.5, clip_on=False)

        ax.text(1.5 * lado, 1.2 * y + 0.04, str(cat),
                ha='left' if lado > 0 else 'right', va='bottom',
                fontsize=14, fontweight='bold', color=COLOR_TEXTO)
        ax.text(1.5 * lado, 1.2 * y - 0.04, f'{n / total * 100:.1f}%'.replace('.', ','),
                ha='left' if lado > 0 else 'right', va='top',
                fontsize=12, color=COLOR_GRIS)

    ax.set_title(titulo or columna.name, fontsize=17, fontweight='bold',
                 color=COLOR_TEXTO, pad=25)
    ax.set_aspect('equal')
    ax.set_xlim(-1.9, 1.9)

    plt.tight_layout()
    plt.show()


def crear_grafico_barras(columna, titulo=None, xlabel=None,
                         ylabel='Cantidad de hogares (frecuencia)',
                         color='#35A9C9', orden=None, ordenar_por_valor=False,
                         ancho_etiqueta=18, rotacion=0):
    conteo = columna.dropna().value_counts()

    if orden is not None:
        conteo = conteo.reindex(orden).dropna()
    elif ordenar_por_valor:
        conteo = conteo.sort_index()   # 1, 2, 3, 4...

    total = int(conteo.sum())
    categorias = conteo.index.tolist()
    valores = conteo.values

    fig, ax = plt.subplots(figsize=(10, 5.5))

    posiciones = range(len(categorias))
    barras = ax.bar(posiciones, valores, color=color, width=0.55)

    etiquetas = [f'{int(n)}\n({n / total * 100:.1f}%)' for n in valores]
    ax.bar_label(barras, labels=etiquetas, padding=3,
                 fontsize=9, fontweight='bold', linespacing=1.1)

    # Etiquetas del eje X alineadas con cada barra
    ax.set_xticks(list(posiciones))
    ax.set_xticklabels([textwrap.fill(str(c), ancho_etiqueta) for c in categorias],
                       rotation=rotacion,
                       ha='right' if rotacion else 'center', fontsize=10)

    ax.set_title(f'{titulo or columna.name}\n(Total de respuestas: {total})',
                 fontsize=12, fontweight='bold', pad=12)
    ax.set_xlabel(xlabel or columna.name, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)

    ax.set_ylim(0, max(valores) * 1.2)
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    ax.set_axisbelow(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

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

#URL Original
#url = 'https://docs.google.com/spreadsheets/d/1m5YCNWVu3Is4A9U3UVfEltZTOWYMZqwzd1S0fLX0kfg/export?format=csv&gid=1872966122'
# URL Edades eje 0
url = 'https://docs.google.com/spreadsheets/d/1m5YCNWVu3Is4A9U3UVfEltZTOWYMZqwzd1S0fLX0kfg/export?format=csv&gid=295516045'
df = pd.read_csv(url)

crear_Histograma(df['Edad de hogares'], escala=np.arange(15, 80, 5))

#crear_grafico_barras(df['1.6 De las comidas de la última semana, ¿cuántas fueron preparadas en el hogar?'],
#                     titulo='Cantidad de comidas preparadas en el hogar en la última semana',
#                     xlabel='Cantidad de comidas preparadas en el hogar',
#                     ordenar_por_valor=True)

#crear_grafico_barras(df['Cantidad de integrantes del hogar'])


#crear_grafico_torta(df['1.7 Habitualmente cuando se cocina en el hogar, ¿se le agrega sal a las comidas durante la cocción?'], titulo='¿Se le agrega sal a la comida durante la cocción?')


#crear_Torta(df['1.1.2 Género de quién/es definen qué se cocina'])
