import os
import pandas as pd
import matplotlib.pyplot as plt

TERRACOTA = "#1EA2C4"
ARCHIVO_DATOS = 'Copia de Base para trabajar Centros de Salud - Villa Gaucho.xlsx'

def graficar_frecuencia_comida(df, codigo_pregunta, titulo=None, color=TERRACOTA, nombre_archivo=None):
    conteo_dias = {}

    for dia in range(1, 8):
        # Busca las columnas que contengan el código (ej. '2.1'), '[dia]' y 'cant'
        col = [c for c in df.columns if codigo_pregunta in c and f'[{dia}]' in c and 'cant' in c.lower()]
        
        if col:
            total_integrantes = pd.to_numeric(df[col[0]], errors='coerce').fillna(0).sum()
            conteo_dias[dia] = int(total_integrantes)
        else:
            conteo_dias[dia] = 0

    serie_resumen = pd.Series(conteo_dias)
    total_personas = serie_resumen.sum()

    # Si no se pasó nombre_archivo, se genera automáticamente según el código
    if nombre_archivo is None:
        codigo_limpio = codigo_pregunta.replace('.', '_')
        nombre_archivo = f'{codigo_limpio}_frecuencia.png'

    if titulo is None:
        titulo = f'Frecuencia semanal ({codigo_pregunta})'

    fig, ax = plt.subplots(figsize=(9, 5.5))
    x_pos = [str(d) for d in serie_resumen.index]
    valores = serie_resumen.values

    barras = ax.bar(x_pos, valores, color=color, edgecolor='white', linewidth=1.2, alpha=0.9)

    ax.set_xlabel('Días a la semana (frecuencia)', fontsize=12)
    ax.set_ylabel('Cantidad total de integrantes', fontsize=12)
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    ax.set_axisbelow(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    max_h = max(valores) if len(valores) > 0 and max(valores) > 0 else 1
    for bar in barras:
        h = bar.get_height()
        pct = (h / total_personas * 100) if total_personas > 0 else 0
        etiqueta = f'{int(h)}\n({pct:.1f}%)' if h > 0 else '0'
        ax.text(bar.get_x() + bar.get_width() / 2, h + (max_h * 0.02),
                etiqueta, ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax.set_ylim(0, max_h * 1.22)
    ax.set_title(f'{titulo}\n(Total de integrantes relevados: {total_personas})',
                 fontsize=14, fontweight='bold', pad=15)

    plt.tight_layout()
    plt.savefig(nombre_archivo, dpi=300)
    plt.close()
    print(f'[✓] Gráfico generado y guardado como: {nombre_archivo}')


# Carga del archivo
df = pd.read_excel(ARCHIVO_DATOS)
df.columns = [str(c).strip() for c in df.columns]

# Si querés generar las cuatro comidas de una sola vez:
comidas = {
    '2.1': ('Desayuno', '2_1_frecuencia_desayuno.png'),
    '2.2': ('Almuerzo', '2_2_frecuencia_almuerzo.png'),
    '2.3': ('Merienda', '2_3_frecuencia_merienda.png'),
    '2.4': ('Cena',     '2_4_frecuencia_cena.png')
}

for cod, (nombre, archivo_salida) in comidas.items():
    graficar_frecuencia_comida(
        df,
        codigo_pregunta=cod,
        titulo=f'{cod} Frecuencia semanal de {nombre.lower()} en los integrantes del hogar',
        color=TERRACOTA,
        nombre_archivo=archivo_salida
    )