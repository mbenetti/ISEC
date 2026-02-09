# %%
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

# Rango de DS y DM
DS_vals = np.linspace(0.01, 1, 100)
DM_vals = np.linspace(0.1, 3, 100)  # DM ya incluye k*ediciones
DS_grid, DM_grid = np.meshgrid(DS_vals, DM_vals)

# Parámetros
FMN_log = 1
alpha = 1

# ISEC geométrica ponderada
ISEC_geom_grid = FMN_log / (DS_grid**alpha * DM_grid ** (1 - alpha))

# Plot 3D
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection="3d")
surf = ax.plot_surface(DS_grid, DM_grid, ISEC_geom_grid, cmap="viridis")
ax.set_xlabel("Distancia Semantica")
ax.set_ylabel("Distancia Morfologica")
ax.set_zlabel("ISEC")
ax.zaxis.labelpad = -205
ax.set_title("ISEC con media geométrica ponderada: superficie DS vs DM")
fig.colorbar(surf, shrink=0.5, aspect=10)
plt.show()
