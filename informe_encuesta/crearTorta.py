import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'

ARCHIVO_DATOS = 'Copia de Base para trabajar Centros de Salud - Villa Gaucho.xlsx'
OUTPUT_DIR = 'graficos_eje_2_tortas_estilo'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Paleta de colores de referencia
COLORES_ESTILO = {
    'Si': '#3B82F6',        # Azul brillante
    'No': '#EA4335',        # Rojo vibrante
    'No sabe': '#FBBF24',   # Amarillo
    'Ns/Nc': '#FBBF24'
}

def graficar_torta_estilo_referencia(serie_sino, titulo, nombre_archivo, codigo_pregunta='2.1'):
    serie = serie_sino[serie_sino > 0]
    total = serie.sum()
    if total == 0:
        return

    fig, ax = plt.subplots(figsize=(8.5, 6), subplot_kw=dict(aspect="equal"))
    colores = [COLORES_ESTILO.get(cat, '#9CA3AF') for cat in serie.index]

    # Determinación automática del artículo ("el" o "la")
    art = 'la' if titulo.lower() in ['merienda', 'cena'] else 'el'
    pregunta_titulo = f'¿Realiza habitualmente {art} {titulo.lower()}?'

    # Título principal únicamente (sin subtítulo)
    fig.suptitle(
        pregunta_titulo,
        fontsize=15,
        fontweight='bold',
        color='#111827',
        y=0.95
    )

    # Dibujo de la torta
    wedges, _ = ax.pie(
        serie.values,
        startangle=90,
        counterclock=False,
        colors=colores,
        wedgeprops=dict(width=1.0, edgecolor='none')
    )

    # Anotaciones, conectores y etiquetas externas
    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1) / 2. + p.theta1
        rad = np.deg2rad(ang)
        y = np.sin(rad)
        x = np.cos(rad)

        val = int(serie.values[i])
        pct = (val / total) * 100
        pct_str = f"{pct:.1f}%".replace('.', ',')
        cat_nombre = serie.index[i]

        # Número absoluto en el borde interno de la porción[cite: 2]
        ax.text(
            0.82 * x, 0.82 * y, f"{val}",
            ha="center", va="center",
            fontsize=11, color="#1F2937", fontweight="bold"
        )

        # Orientación horizontal de las etiquetas[cite: 2]
        ha = "left" if x >= 0 else "right"
        x_ext = 1.35 if x >= 0 else -1.35
        y_ext = y * 1.05

        # Conector y nombre de categoría[cite: 2]
        ax.annotate(
            cat_nombre,
            xy=(x * 0.98, y * 0.98),
            xytext=(x_ext, y_ext + 0.05),
            ha=ha, va="center",
            fontsize=12, fontweight="bold", color="#111827",
            arrowprops=dict(
                arrowstyle="-",
                color="#9CA3AF",
                lw=1.1,
                connectionstyle=f"angle,angleA=0,angleB={ang:.1f},rad=0"
            )
        )

        # Porcentaje en gris debajo de la categoría[cite: 2]
        ax.text(
            x_ext, y_ext - 0.09, pct_str,
            ha=ha, va="center",
            fontsize=11, color="#6B7280"
        )

    ax.set_xlim(-1.9, 1.9)
    ax.set_ylim(-1.3, 1.3)
    ax.axis('off')

    ruta = os.path.join(OUTPUT_DIR, nombre_archivo)
    plt.savefig(ruta, dpi=300, bbox_inches='tight', transparent=False, facecolor='white')
    plt.close()
    print(f"[✓] Gráfico generado: {ruta}")


def procesar_comida_eje2(df, codigo_pregunta, nombre_comida, nombre_archivo):
    # 1. Cantidades Sí: días 1 al 7
    total_si = 0
    for dia in range(1, 8):
        cols_dia = [c for c in df.columns if codigo_pregunta in c and f'[{dia}]' in c and 'cant' in c.lower()]
        if cols_dia:
            total_si += int(pd.to_numeric(df[cols_dia[0]], errors='coerce').fillna(0).sum())

    # 2. Cantidades No: 0 días
    total_no = 0
    cols_cero = [c for c in df.columns if codigo_pregunta in c and ('[0]' in c or ' 0' in c) and 'cant' in c.lower()]
    if cols_cero:
        total_no += int(pd.to_numeric(df[cols_cero[0]], errors='coerce').fillna(0).sum())

    # 3. No sabe / NsNc (si existiera columna explícita)
    total_nsnc = 0
    cols_ns = [c for c in df.columns if codigo_pregunta in c and ('no sabe' in c.lower() or 'ns' in c.lower()) and 'cant' in c.lower()]
    if cols_ns:
        total_nsnc += int(pd.to_numeric(df[cols_ns[0]], errors='coerce').fillna(0).sum())

    datos = {'Si': total_si, 'No': total_no}
    if total_nsnc > 0:
        datos['No sabe'] = total_nsnc

    serie_sino = pd.Series(datos)
    graficar_torta_estilo_referencia(
        serie_sino,
        titulo=nombre_comida,
        nombre_archivo=nombre_archivo,
        codigo_pregunta=codigo_pregunta
    )


# -------------------------------------------------------------
# Carga de datos y ejecución para el Eje 2
# -------------------------------------------------------------
if __name__ == '__main__':
    df = pd.read_excel(ARCHIVO_DATOS)
    df.columns = [str(c).strip() for c in df.columns]

    comidas = {
        '2.1': ('Desayuno', 'pie_chart_estilo_desayuno_2_1.png'),
        '2.2': ('Almuerzo', 'pie_chart_estilo_almuerzo_2_2.png'),
        '2.3': ('Merienda', 'pie_chart_estilo_merienda_2_3.png'),
        '2.4': ('Cena',     'pie_chart_estilo_cena_2_4.png')
    }

    for cod, (nombre, archivo_salida) in comidas.items():
        procesar_comida_eje2(df, cod, nombre, archivo_salida)