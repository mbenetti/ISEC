import random

import matplotlib.pyplot as plt
import numpy as np

random.seed(42)

# =================================================================
# CONFIGURACIÓN DE PARÁMETROS (Basado en tu propuesta de tesis)
# =================================================================
K_PENALIZACION = 0.1  # Constante k para controlar la pendiente
N_SIMULACIONES = 100000  # Número de iteraciones para rigor estadístico

# Costos definidos
COSTO_BAJO = 0.55  # Teclas cercanas / Errores probables
COSTO_TRANS = 0.6  # Transposiciones (Excluidas de CP)
COSTO_STD = 0.7  # Sustitución estándar
COSTO_ESTRUCT = 1.5  # Adiciones y Eliminaciones


def calcular_cmp(lista_operaciones, k=K_PENALIZACION):
    """
    Calcula el CMP según la fórmula: CMP = CM + (k * CP)
    Donde CM es el promedio de todo y CP es la suma de todo menos transposiciones.
    """
    if not lista_operaciones:
        return 0.0

    # 1. CM (Costo Medio): Promedio de todas las operaciones detectadas
    cm = np.mean(lista_operaciones)

    # 2. CP (Costos Penalizados): Suma de ops Levenshtein (excluye 0.7)
    cp = sum([op for op in lista_operaciones if op != COSTO_TRANS])

    # 3. Fórmula final
    return cm + (k * cp)


# =================================================================
# EJECUCIÓN DEL EXPERIMENTO DE MONTECARLO
# =================================================================
resultados_error = []  # Población: Errores tipográficos probables
resultados_divergencia = []  # Población: Categorías realmente diferentes

for _ in range(N_SIMULACIONES):
    # --- ESCENARIO A: ERRORES DE INGRESO (Compresión) ---
    # Pocas operaciones (1-2) con alta probabilidad de ser bajo costo o transposición
    n_ops_a = random.randint(1, 2)
    # Definimos pesos: 45% bajo costo, 45% transposición, 10% estándar
    ops_a = random.choices(
        [COSTO_BAJO, COSTO_TRANS, COSTO_STD], weights=[45, 45, 10], k=n_ops_a
    )
    resultados_error.append(calcular_cmp(ops_a))

    # --- ESCENARIO B: DIVERGENCIA REAL (Expansión) ---
    # Más operaciones (3-6) con alta probabilidad de ser adiciones/eliminaciones
    n_ops_b = random.randint(3, 6)
    # Definimos pesos: 80% estructural, 16% estándar, 4% bajo costo
    ops_b = random.choices(
        [COSTO_ESTRUCT, COSTO_STD, COSTO_BAJO], weights=[80, 16, 4], k=n_ops_b
    )
    resultados_divergencia.append(calcular_cmp(ops_b))

# =================================================================
# GENERACIÓN DEL GRÁFICO ACADÉMICO
# =================================================================
plt.figure(figsize=(12, 7))

# Histogramas de ambas poblaciones
plt.hist(
    resultados_error,
    bins=30,
    alpha=0.6,
    color="#2ecc71",
    edgecolor="black",
    label="Errores Probables (Costo Bajo 0 Transp.)",
)

plt.hist(
    resultados_divergencia,
    bins=50,
    alpha=0.6,
    color="#e74c3c",
    edgecolor="black",
    label="Divergencia Real (Estructural)",
)

# Línea de umbral crítico en 1.0
plt.axvline(
    1.0, color="black", linestyle="--", linewidth=2.5, label="Umbral Crítico (1.0)"
)

# Anotaciones explicativas
plt.text(
    0.75,
    plt.gca().get_ylim()[1] * 0.8,
    "ZONA DE COMPRESIÓN\n(CMP < 1.0)",
    color="green",
    fontweight="bold",
    ha="center",
    bbox=dict(facecolor="white", alpha=0.5),
)

plt.text(
    1.3,
    plt.gca().get_ylim()[1] * 0.8,
    "ZONA DE EXPANSIÓN\n(CMP > 1.0)",
    color="red",
    fontweight="bold",
    ha="center",
    bbox=dict(facecolor="white", alpha=0.5),
)

# Etiquetas y títulos
plt.title(
    "Comportamiento del CMP: Validación del comportamiento Afinidad vs Divergencia \ncon Simulación de Montecarlo)",
    fontsize=14,
)
plt.xlabel("Valor del CMP (Modulador del Denominador en ISEC)", fontsize=12)

# More detailed x-axis ticks
plt.xticks(np.arange(0.4, 3.0, 0.1))
plt.ylabel("Frecuencia de Ocurrencias ($N=10,000$)", fontsize=12)
plt.legend(loc="upper right")
plt.grid(axis="y", alpha=0.3)

plt.tight_layout()
plt.show()

# Resumen estadístico para el texto de la tesis
print(f"--- ESTADÍSTICAS DE VALIDACIÓN ---")
print(f"Media CMP (Errores): {np.mean(resultados_error):.4f}")
print(f"Media CMP (Divergencia): {np.mean(resultados_divergencia):.4f}")
print(f"Desviación Estándar (Divergencia): {np.std(resultados_divergencia):.4f}")
