import os
import re
import textwrap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

TERRACOTA = "#1EA2C4"
ARCHIVO_DATOS = 'Copia de Base para trabajar Centros de Salud - Villa Gaucho.xlsx'
OUTPUT_DIR = 'graficos_eje_4_barras_verticales'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Mapeo para acortar las respuestas extensas
MAPEO_ETIQUETAS = {
    'come la cantidad que considera adecuada': 'Cantidad adecuada',
    'su compra y preparacion requiere mucho tiempo dificultad por habitos o vida cotidiana': 'Falta de tiempo / dificultad',
    'su compra y preparacion requiere mucho tiempo/dificultad por habitos o vida cotidiana': 'Falta de tiempo / dificultad',
    'pocas opciones de lugares de compra en cercania supermercado verduleria almacen etc': 'Pocas opciones cercanas',
    'pocas opciones de lugares de compra en cercania (supermercado, verduleria, almacen, etc.)': 'Pocas opciones cercanas',
    'son caras': 'Son caras / Precio',
    'no le gustan': 'No le gustan',
    'no le gusta': 'No le gusta',
    'muy saludable': 'Muy saludable',
    'bastante saludable': 'Bastante saludable',
    'poco saludable': 'Poco saludable',
    'nada saludable': 'Nada saludable',
    'ns/nc': 'Ns/Nc',
    'no sabe': 'Ns/Nc'
}

def normalizar_opcion(texto, ancho=18):
    t_clean = re.sub(r'[^\w\s]', '', str(texto)).strip().lower()
    for k, v in MAPEO_ETIQUETAS.items():
        k_clean = re.sub(r'[^\w\s]', '', k).strip().lower()
        if k_clean in t_clean or t_clean in k_clean:
            return textwrap.fill(v, width=ancho)
    return textwrap.fill(str(texto).strip(), width=ancho)

def crear_Barras_Verticales_Eje4(columna, titulo=None, max_categorias=6, color=TERRACOTA, nombre_archivo=None):
    datos = columna.dropna().astype(str).str.strip()
    datos = datos[~datos.isin(['', 'nan', 'None'])]
    datos_transformados = datos.apply(normalizar_opcion)
    
    conteo = datos_transformados.value_counts()
    if conteo.empty:
        print(f"[-] Sin datos para {columna.name}")
        return

    # Agrupar colas largas de respuestas abiertas en 'Otros'
    if len(conteo) > max_categorias:
        principales = conteo.iloc[:max_categorias - 1]
        otros = conteo.iloc[max_categorias - 1:].sum()
        conteo = pd.concat([principales, pd.Series({'Otros': otros})])

    total = conteo.sum()
    categorias = [str(c) for c in conteo.index]

    fig, ax = plt.subplots(figsize=(10, 6.5))

    barras = ax.bar(categorias, conteo.values, color=color,
                    edgecolor='white', linewidth=1.2, alpha=0.9, width=0.55)

    ax.set_xlabel('Opciones declaradas', fontsize=11, labelpad=10)
    ax.set_ylabel('Cantidad de hogares (frecuencia)', fontsize=11)
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    ax.set_axisbelow(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Rotación para que no choquen los textos
    plt.setp(ax.get_xticklabels(), rotation=30, ha='right', fontsize=10)

    # Etiquetas con número y porcentaje sobre cada barra
    max_h = max(conteo.values) if len(conteo.values) > 0 else 1
    ax.set_ylim(0, max_h * 1.25)

    for bar in barras:
        h = bar.get_height()
        pct = (h / total * 100) if total > 0 else 0
        etiqueta = f'{int(h)}\n({pct:.1f}%)' if h > 0 else '0'
        ax.text(bar.get_x() + bar.get_width() / 2, h + (max_h * 0.02),
                etiqueta, ha='center', va='bottom', fontsize=9.5, fontweight='bold')

    nombre_var = titulo or f'Distribución de {columna.name}'
    ax.set_title(f'{nombre_var}\n(Total de respuestas: {total})',
                 fontsize=13, fontweight='bold', pad=15)

    plt.tight_layout()
    if nombre_archivo:
        ruta = os.path.join(OUTPUT_DIR, nombre_archivo)
        plt.savefig(ruta, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"[✓] Guardado: {ruta}")
    else:
        plt.show()


# -------------------------------------------------------------
# Carga de datos y ejecución
# -------------------------------------------------------------
df = pd.read_excel(ARCHIVO_DATOS)
df.columns = [str(c).strip() for c in df.columns]

preguntas_eje_4 = [
    ('4.1', '4_1_barras_vert_frutas_verduras.png', '4.1 Razón principal: consumo de frutas y/o verduras'),
    ('4.2', '4_2_barras_vert_carnes_rojas.png',   '4.2 Razón principal: consumo de carnes rojas'),
    ('4.3', '4_3_barras_vert_carnes_blancas.png', '4.3 Razón principal: consumo de carnes blancas'),
    ('4.4', '4_4_barras_vert_percepcion_dieta.png', '4.4 Autopercepción de qué tan saludable es la dieta familiar')
]

for codigo, nombre_archivo, titulo_personalizado in preguntas_eje_4:
    col_encontrada = [c for c in df.columns if c.startswith(codigo) or f' {codigo}' in c or f'{codigo} ' in c]
    
    if col_encontrada:
        col = col_encontrada[0]
        print(f"[Procesando {codigo}] Columna: {col}")
        crear_Barras_Verticales_Eje4(
            df[col],
            titulo=titulo_personalizado,
            max_categorias=6,
            color=TERRACOTA,
            nombre_archivo=nombre_archivo
        )
    else:
        print(f"[!] No se encontró la columna para la pregunta {codigo}")