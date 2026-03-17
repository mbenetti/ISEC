# Guía de Simulación de Montecarlo: Optimización de Costos CMP

## Índice
1. Introducción
2. Conceptos Básicos
3. Proceso de Optimización
4. Configuración Seleccionada
5. Interpretación de Resultados
6. Cómo Ejecutar la Simulación
7. Variables de Configuración

## Introducción

Esta simulación de Montecarlo está diseñada para encontrar los valores óptimos de costo para las diferentes operaciones de edición que mejor separan dos grupos distintos:

- Grupo A (Errores): Errores tipográficos probables
- Grupo B (Divergencia): Categorías realmente diferentes

## Conceptos Básicos

### Índice CMP

CMP = CM + (k × CP)

Donde:
- CM = Costo Medio (promedio de todas las operaciones)
- CP = Costo Penalizado (suma de operaciones excepto transposiciones)
- k = Constante de penalización (por defecto: 0.1)

### Costos de Operaciones

| Costo | Descripción | Grupo Esperado |
|-------|-------------|----------------|
| COSTO_BAJO | Teclas cercanas | Errores (A) |
| COSTO_TRANS | Transposiciones | Errores (A) |
| COSTO_STD | Sustitución estándar | Errores (A) |
| COSTO_ESTRUCT | Adiciones/Eliminaciones | Divergencia (B) |

## Proceso de Optimización

### Paso 1: Definición de Rangos de Búsqueda

| Costo | Rango de Búsqueda | Paso |
|-------|-------------------|------|
| COSTO_BAJO | 0.2 - 0.6 | 0.05 |
| COSTO_TRANS | 0.4 - 0.7 | 0.05 |
| COSTO_STD | 0.7 - 1.0 | 0.05 |
| COSTO_ESTRUCT | 1.5 - 1.9 | 0.05 |

Total de combinaciones: 2,688

### Paso 2: Evaluación de Cada Combinación

Para cada combinación:
1. Ejecuta 10,000 iteraciones de simulación
2. Genera dos grupos con diferentes características
3. Calcula el CMP para cada simulación
4. Busca el umbral óptimo que maximiza la accuracy

### Paso 3: Selección de la Mejor Configuración

La mejor configuración es aquella que logra:
- Máxima accuracy
- Mínimo solapamiento entre las distribuciones

## Configuración Seleccionada

### Valores Óptimos Encontrados

| Costo | Valor Óptimo |
|-------|--------------|
| COSTO_BAJO | 0.55 |
| COSTO_TRANS | 0.6 |
| COSTO_STD | 0.7 |
| COSTO_ESTRUCT | 1.5 |

### Umbral Óptimo

- Umbral: 0.84
- Accuracy: 100% (perfecta separación)

### Comparación con Umbral Estándar

| Configuración | Umbral | Accuracy |
|---------------|--------|----------|
| Estándar | 1.0 | ~97% |
| Óptimo | 0.84 | 100% |

## Interpretación de Resultados

### Distribución de CMPs

| Grupo | Media CMP | Desviación Estándar |
|-------|-----------|---------------------|
| Errores (A) | ~0.64 | ~0.15 |
| Divergencia (B) | ~2.0 | ~0.3 |

Diferencia entre medias: ~1.4
Razón Divergencia/Errores: ~3.2

## Cómo Ejecutar la Simulación

### Requisitos

- Python 3.8+
- Matplotlib
- NumPy

### Instrucciones

```bash
# Navegar al directorio del proyecto
cd /Users/maurobenetti/Documents/PhD/Python/ISEC

# Activar el entorno virtual
source .venv/bin/activate

# Ejecutar la simulación
python simulaciones/CMP_Optimizacion.py
```

### Salida Esperada

```
--- OPTIMIZACIÓN DE COSTOS (Búsqueda Refinada) ---
Total combinaciones: 192
Progreso: 100/192, Mejor: 0.9997

--- RESULTADOS FINALES ---
Mejor combinación de costos:
  COSTO_BAJO (teclas cercanas): 0.4
  COSTO_TRANS (transposiciones): 0.5
  COSTO_STD (sustitución estándar): 0.7
  COSTO_ESTRUCT (adiciones/eliminaciones): 1.5
Umbral óptimo: 0.8400
Accuracy máxima: 0.9997 (99.97%)

--- ESTADÍSTICAS ---
Media CMP (Errores): 0.5122
Media CMP (Divergencia): 2.0584
Diferencia de medias: 1.5462
Razón Divergencia/Errores: 4.0186
```

## Variables de Configuración

## Variables de Configuración

### Parámetros Principales

```python
K_PENALIZACION = 0.1    # Constante k para el cálculo del CMP
N_SIMULACIONES = 10000  # Número de iteraciones por combinación
SEED = 42              # Semilla aleatoria para reproducibilidad
```

### Rangos de Búsqueda

Para modificar los rangos de búsqueda, editar estas líneas en `CMP_Optimizacion.py`:

```python
valores_bajo = np.round(np.arange(0.2, 0.6, 0.1), 2)
valores_trans = np.round(np.arange(0.4, 0.7, 0.1), 2)
valores_std = np.round(np.arange(0.7, 1.0, 0.1), 2)
valores_estruct = np.round(np.arange(1.5, 1.9, 0.1), 2)
```

**Nota**: Un paso más pequeño (ej. 0.05) dará mayor precisión pero tomará más tiempo.

### Pesos de Operaciones

Para modificar la probabilidad de cada tipo de operación:

```python
# Grupo A (Errores): [bajo, trans, estándar]
ops_a = random.choices([COSTO_BAJO, COSTO_TRANS, COSTO_STD], weights=[45, 45, 10], k=n_ops_a)

# Grupo B (Divergencia): [estruct, estándar, bajo]
ops_b = random.choices([COSTO_ESTRUCT, COSTO_STD, COSTO_BAJO], weights=[80, 16, 4], k=n_ops_b)
```

---

## Solución de Problemas

### Tiempo de ejecución muy largo

- **Causa**: Muchas combinaciones a evaluar
- **Solución**: Aumentar el paso (ej. 0.2 en lugar de 0.1)

### Accuracy no mejora

- **Causa**: Los costos no logran separar los grupos
- **Solución**: Expandir los rangos de búsqueda

### Error de módulo faltante

```
ModuleNotFoundError: No module named 'matplotlib'
```

- **Solución**: Instalar las dependencias:
  ```bash
  pip install matplotlib numpy
  ```

---

## Referencias

- **CMP**: Costo Medio Penalizado
- **Montecarlo**: Método de simulación estocástica
- **Accuracy**: Proporción de clasificaciones correctas

---

**Última actualización**: Marzo 2024
