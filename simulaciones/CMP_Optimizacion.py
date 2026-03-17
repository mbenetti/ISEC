import random
from itertools import product

import matplotlib.pyplot as plt
import numpy as np

random.seed(42)

K_PENALIZACION = 0.1
N_SIMULACIONES = 10000


def calcular_cmp(lista_operaciones, k, costo_trans):
    if not lista_operaciones:
        return 0.0
    cm = np.mean(lista_operaciones)
    cp = sum([op for op in lista_operaciones if op != costo_trans])
    return cm + (k * cp)


def run_simulation(costos, k=K_PENALIZACION, n=N_SIMULACIONES, seed=42):
    COSTO_BAJO, COSTO_TRANS, COSTO_STD, COSTO_ESTRUCT = costos
    random.seed(seed)
    resultados_error = []
    resultados_divergencia = []
    for _ in range(n):
        n_ops_a = random.randint(1, 2)
        ops_a = random.choices(
            [COSTO_BAJO, COSTO_TRANS, COSTO_STD], weights=[45, 45, 10], k=n_ops_a
        )
        resultados_error.append(calcular_cmp(ops_a, k=k, costo_trans=COSTO_TRANS))
        n_ops_b = random.randint(3, 8)
        ops_b = random.choices(
            [COSTO_ESTRUCT, COSTO_STD, COSTO_BAJO], weights=[80, 16, 4], k=n_ops_b
        )
        resultados_divergencia.append(calcular_cmp(ops_b, k=k, costo_trans=COSTO_TRANS))
    rango_min = min(min(resultados_error), min(resultados_divergencia))
    rango_max = max(max(resultados_error), max(resultados_divergencia))
    mejor_accuracy = 0
    umbral_optimo = rango_min
    for umbral in np.arange(rango_min, rango_max + 0.01, 0.01):
        tp = sum(1 for x in resultados_divergencia if x >= umbral)
        tn = sum(1 for x in resultados_error if x < umbral)
        accuracy = (tp + tn) / (len(resultados_error) + len(resultados_divergencia))
        if accuracy > mejor_accuracy:
            mejor_accuracy = accuracy
            umbral_optimo = umbral
    return mejor_accuracy, umbral_optimo, resultados_error, resultados_divergencia


print("--- OPTIMIZACIÓN DE COSTOS (Búsqueda Refinada) ---")
valores_bajo = np.round(np.arange(0.2, 0.6, 0.1), 2)
valores_trans = np.round(np.arange(0.4, 0.7, 0.1), 2)
valores_std = np.round(np.arange(0.7, 1.0, 0.1), 2)
valores_estruct = np.round(np.arange(1.5, 1.9, 0.1), 2)
mejor_costos = None
mejor_accuracy = 0
mejor_umbral = 0
total_combinaciones = (
    len(valores_bajo) * len(valores_trans) * len(valores_std) * len(valores_estruct)
)
print(f"Total combinaciones: {total_combinaciones}")
cont = 0
for costo_bajo, costo_trans, costo_std, costo_estruct in product(
    valores_bajo, valores_trans, valores_std, valores_estruct
):
    cont += 1
    costos = (costo_bajo, costo_trans, costo_std, costo_estruct)
    if (
        costo_bajo >= costo_trans
        or costo_trans >= costo_std
        or costo_std >= costo_estruct
    ):
        continue
    accuracy, umbral, _, _ = run_simulation(costos)
    if accuracy > mejor_accuracy:
        mejor_accuracy = accuracy
        mejor_costos = costos
        mejor_umbral = umbral
    if cont % 100 == 0:
        print(f"Progreso: {cont}/{total_combinaciones}, Mejor: {mejor_accuracy:.4f}")

print("")
print("--- RESULTADOS FINALES ---")
print(f"Mejor combinación de costos:")
print(f"  COSTO_BAJO (teclas cercanas): {mejor_costos[0]}")
print(f"  COSTO_TRANS (transposiciones): {mejor_costos[1]}")
print(f"  COSTO_STD (sustitución estándar): {mejor_costos[2]}")
print(f"  COSTO_ESTRUCT (adiciones/eliminaciones): {mejor_costos[3]}")
print(f"Umbral óptimo: {mejor_umbral:.4f}")
print(f"Accuracy máxima: {mejor_accuracy:.4f} ({mejor_accuracy * 100:.2f}%)")

random.seed(42)
COSTO_BAJO, COSTO_TRANS, COSTO_STD, COSTO_ESTRUCT = mejor_costos
resultados_error = []
resultados_divergencia = []
for _ in range(N_SIMULACIONES):
    n_ops_a = random.randint(1, 2)
    ops_a = random.choices(
        [COSTO_BAJO, COSTO_TRANS, COSTO_STD], weights=[45, 45, 10], k=n_ops_a
    )
    resultados_error.append(
        calcular_cmp(ops_a, k=K_PENALIZACION, costo_trans=COSTO_TRANS)
    )
    n_ops_b = random.randint(3, 8)
    ops_b = random.choices(
        [COSTO_ESTRUCT, COSTO_STD, COSTO_BAJO], weights=[80, 16, 4], k=n_ops_b
    )
    resultados_divergencia.append(
        calcular_cmp(ops_b, k=K_PENALIZACION, costo_trans=COSTO_TRANS)
    )

plt.figure(figsize=(12, 7))
plt.hist(
    resultados_error,
    bins=30,
    alpha=0.6,
    color="#2ecc71",
    edgecolor="black",
    label=f"Errores (μ={np.mean(resultados_error):.4f})",
)
plt.hist(
    resultados_divergencia,
    bins=30,
    alpha=0.6,
    color="#e74c3c",
    edgecolor="black",
    label=f"Divergencia (μ={np.mean(resultados_divergencia):.4f})",
)
plt.axvline(
    mejor_umbral,
    color="blue",
    linestyle="--",
    linewidth=2.5,
    label=f"Umbral Óptimo ({mejor_umbral:.2f})",
)
plt.axvline(
    1.0, color="gray", linestyle="-.", linewidth=1.5, label="Umbral Estándar (1.0)"
)
plt.title(
    f"Optimización de Costos\nBajo={COSTO_BAJO}, Trans={COSTO_TRANS}, Std={COSTO_STD}, Estruct={COSTO_ESTRUCT}"
)
plt.xlabel("Valor del CMP")
plt.ylabel("Frecuencia")
plt.legend()
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.show()

print("")
print("--- ESTADÍSTICAS ---")
print(f"Media CMP (Errores): {np.mean(resultados_error):.4f}")
print(f"Media CMP (Divergencia): {np.mean(resultados_divergencia):.4f}")
print(
    f"Diferencia de medias: {abs(np.mean(resultados_divergencia) - np.mean(resultados_error)):.4f}"
)
print(
    f"Razón Divergencia/Errores: {np.mean(resultados_divergencia) / np.mean(resultados_error):.4f}"
)
