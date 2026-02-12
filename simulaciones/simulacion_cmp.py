import matplotlib.pyplot as plt
import numpy as np

def calcular_cmp(ops, k):
    if not ops: return 0
    cp = sum([c for type, c in ops if type != 'transp']) # Suma Levenshtein
    cm = sum([c for type, c in ops]) / len(ops)         # Promedio Total
    return cm + (k * cp)

# Definimos una secuencia de errores "probables" (un operario cometiendo errores de más a menos comunes)
# 1. Transposición (muy barata)
# 2. Sustitución bajo costo
# 3. Sustitución normal
# 4. Inserción
# 5. Eliminación
escenario_errores = [
    ('transp', 0.5), ('sub_bajo', 0.7), ('sub_std', 1.1), 
    ('ins', 1.3), ('del', 1.3)
]

k_values = [0.1, 0.2, 0.5]
plt.figure(figsize=(10, 6))

for k in k_values:
    y = [1]
    current_ops = []
    for error in escenario_errores:
        current_ops.append(error)
        y.append(calcular_cmp(current_ops, k))
    
    plt.plot(range(len(y)), y, marker='o', label=f'k={k}')

plt.title('Influencia del Costo penalizado en el CPM', fontsize=13)
plt.xlabel('Número de operaciones penalizadas', fontsize=11)
plt.ylabel('Costo Medio Penalizado CPM para un valor inicial de CMP=1', fontsize=11)
plt.xlim(left=0)
plt.ylim(bottom=0)
plt.axhline(y=1.0, color='black', linestyle='--', alpha=0.3)
plt.grid(True, alpha=0.3)
plt.legend()
plt.show()

