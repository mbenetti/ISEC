import matplotlib.pyplot as plt
import numpy as np

# Typical values based on your cost design
C_medio = 1.1
c_medio_penalizado = 1.3

# Number of penalized operations
n_ops = np.arange(0, 21)

# Different k values
k_values = [0.05, 0.1, 0.2]

plt.figure(figsize=(6,4))

for k in k_values:
    CMP = C_medio + k * c_medio_penalizado * n_ops
    plt.plot(n_ops, CMP, label=f"k = {k}")

plt.xlabel("Costo de las operaciones penalizadas")
plt.ylabel("CMP (Costo Medio Penalizado)")
plt.legend()
plt.tight_layout()
plt.show()