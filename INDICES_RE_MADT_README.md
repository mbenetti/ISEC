# Aggregate Taxonomic Fragility Indices: R_E and MAD_T

This document describes two aggregate indices computed from the pairwise ISEC (Índice de Sensibilidad al Error Categórico) scores produced by `ISEC.py`. These indices summarize the overall robustness and dispersion of the categorical risk landscape across an entire taxonomy.

---

## Input Files

Both indices consume the Excel files exported by `ISEC.py` via the `export_to_excel` method. Each file contains one row per sentence–match pair.

### Input File Columns

| Column | Type | Description |
|---|---|---|
| `Sentence` | str | Source sentence / category identifier |
| `Sentence_Group` | str | Group classification of the source sentence |
| `Frequency` | int | Frequency of the source sentence in the dataset |
| `FMN` | float | Frequency Median Normalized value |
| `Match_Rank` | int | Rank of the match (1st, 2nd, … closest semantic neighbor) |
| `Matched_Sentence` | str | Matched sentence / category identifier |
| `Matched_Sentence_Group` | str | Group classification of the matched sentence |
| `Matched_Frequency` | int | Frequency of the matched sentence in the dataset |
| `Semantic_Distance` | float | Semantic distance (0.0–1.0) between the pair |
| `Cost_Distance` | float | Penalized morphological edit distance between the pair |
| `ISEC_Score` | float | Individual ISEC score for this sentence–match pair |

### Files Used in This Analysis

| File | Rows (pairs evaluated) | Unique categories (N) |
|---|---|---|
| `resultados/ISEC_provincias_Results.xlsx` | 2,590 | 259 |
| `resultados/ISEC_catalog_Results.xlsx` | 66,760 | 6,676 |
| `resultados/ISEC_insertos1000_Results.xlsx` | 10,000 | 1,000 |

---

## Index 1: R_E — Índice de Robustez del Espacio Categórico

### Formula

$$R_E = 1 - \frac{y_m - \mu_{\text{ISEC}}}{y_m} = \frac{\mu_{\text{ISEC}}}{y_m}$$

Where:

- $y_m$ is the **maximum calculated ISEC score** (representing the poorest-performing category pair in the taxonomy's active namespace).
- $\mu_{\text{ISEC}}$ is the **arithmetic mean** of all ISEC scores across the active category pairs.

### Interpretation

$R_E \in (0, 1]$

| $R_E$ value | Meaning |
|---|---|
| **Near 1** | **Robust space**: the mean approaches the maximum — most pairs are equally sensitive, leaving little room for a single pair to be confused. |
| **Near 0** | **Fragile space**: at least one pair is far more sensitive than the average, concentrating the categorical error risk. |

### Script

```bash
python indice_RE.py resultados/ISEC_provincias_Results.xlsx
python indice_RE.py resultados/*.xlsx -o resultados/reporte_RE.json
```

### Python API

```python
from indice_RE import calcular_RE
res = calcular_RE("resultados/ISEC_provincias_Results.xlsx")
print(f"R_E = {res.re:.4f}")
```

---

## Index 2: MAD_T — Mean Absolute Taxonomic Fragility Deviation

### Formula

$$\text{MAD\_T} = \frac{1}{M} \sum_{k=1}^{M} |\text{ISEC}_k - \mu_{\text{ISEC}}|$$

Where:

- $M$ is the **total number of evaluated pairs** (rows in the Excel file). Every row is an independent ISEC calculation and all are used without deduplication.
- $N$ is the number of **unique categories** in the taxonomy (union of `Sentence` and `Matched_Sentence`).
- $N(N-1)/2$ is the theoretical total population of unique non-reflexive category pairs (provided as a reference, but not used in the calculation).
- $\text{ISEC}_k$ is the calculated fragility index for pair $k$ (row $k$).
- $\mu_{\text{ISEC}}$ is the **arithmetic mean** of all ISEC scores across the $M$ rows.

### Why all rows are used (No deduplication)

The ISEC calculation pipeline uses an Approximate Nearest Neighbor (ANN) search to find the top-K semantic matches, followed by an exact morphological distance calculation. The final ISEC score combines semantic distance, morphological distance, and empirical median frequency. Because of this multi-step process, a pair's highest ISEC score might occur at an intermediate `Match_Rank` rather than rank 1. Therefore, every row represents a valid, independent pairwise evaluation and is included in the MAD_T calculation.

### Absolute vs. Normalized MAD_T

A **normalized variant** is also computed for cross-dataset comparability:

$$\text{MAD\_T}_{\text{norm}} = \frac{\text{MAD\_T}}{\mu_{\text{ISEC}}}$$

- **MAD_T (Absolute)**: Measures the average absolute distance of each ISEC score from the mean, expressed in the **same units as ISEC**. It tells you *how much* the scores deviate in absolute terms.
- **MAD_T$_{\text{norm}}$ (Relative)**: Expresses the deviation as a fraction of the mean. It is **unitless**, which removes the scale effect and allows you to compare the dispersion of datasets that have completely different ISEC score ranges.

#### Why Normalize? (The Scale Effect)

Even though ISEC is a score, different datasets have different "average heights." For example:
- **Provincias** has a mean of **3.71**. A deviation of **0.5** is only **13%** of the mean.
- **Catalog** has a mean of **0.58**. A deviation of **0.5** is nearly **86%** of the mean (a massive outlier).

Without normalization, you cannot tell if a landscape is "flat" or "rough" relative to its own average risk. $MAD\_T_{\text{norm}}$ allows you to say that **Insertos 1000** (0.10) is "flatter" and more uniform than **Provincias** (0.28), regardless of their absolute ISEC values.

### Interpretation

$\text{MAD\_T} \geq 0$

| MAD_T value | Meaning |
|---|---|
| **Near 0** | **Flat, uniform risk landscape**: all pairs have similar sensitivity — failure is predictable and cohesive across the taxonomy. |
| **High** | **Dispersed risk**: large variability between pairs — failure concentrates in specific zones of the taxonomic space, making the system less predictable. |

### Relationship with R_E

$R_E$ and MAD_T are **complementary**:

- $R_E$ measures how close the mean is to the peak (global robustness).
- MAD_T measures how spread out the entire landscape is (local dispersion).

A space can have a high $R_E$ (mean near the maximum) but also a high MAD_T if scores are widely scattered. Together they provide a complete picture of the risk landscape's shape.

### Script

```bash
python indice_MADt.py resultados/ISEC_provincias_Results.xlsx
python indice_MADt.py resultados/*.xlsx -o resultados/reporte_MADt.json
```

### Python API

```python
from indice_MADt import calcular_MADt
madt = calcular_MADt("resultados/ISEC_provincias_Results.xlsx")
print(f"MAD_T = {madt.mad_t:.4f}")
```

---

## Results Summary

### R_E Results

| Dataset | Pairs | $y_m$ | $\mu_{\text{ISEC}}$ | $R_E$ | ISEC min | ISEC max | ISEC median | ISEC std |
|---|---|---|---|---|---|---|---|---|
| Provincias | 2,590 | 10.2287 | 3.7148 | **0.3632** | 1.0654 | 10.2287 | 3.6028 | 1.3052 |
| Catalog | 66,760 | 5.6695 | 0.5796 | **0.1022** | 0.2467 | 5.6695 | 0.5571 | 0.1450 |
| Insertos 1000 | 10,000 | 3.7345 | 1.4485 | **0.3879** | 1.0095 | 3.7345 | 1.3921 | 0.2099 |

### MAD_T Results

| Dataset | $N$ | $M$ (theoretical) | $\mu_{\text{ISEC}}$ | MAD_T | MAD_T$_{\text{norm}}$ | ISEC min | ISEC max | ISEC median | ISEC std |
|---|---|---|---|---|---|---|---|---|---|
| Provincias | 259 | 33,411 | 3.7148 | **1.0628** | 0.2861 | 1.0654 | 10.2287 | 3.6028 | 1.3052 |
| Catalog | 6,676 | 22,281,150 | 0.5796 | **0.1048** | 0.1809 | 0.2467 | 5.6695 | 0.5571 | 0.1450 |
| Insertos 1000 | 1,000 | 499,500 | 1.4485 | **0.1527** | 0.1054 | 1.0095 | 3.7345 | 1.3921 | 0.2099 |

---

## Comparative Analysis

### Combined View

| Dataset | $R_E$ | MAD_T$_{\text{norm}}$ | Interpretation |
|---|---|---|---|
| **Provincias** | 0.3632 | 0.2861 | Moderate robustness with high dispersion — risk is concentrated in specific vulnerable pairs. |
| **Catalog** | 0.1022 | 0.1809 | Very fragile — the mean is far below the peak, indicating extreme concentration of risk in a few pairs. |
| **Insertos 1000** | 0.3879 | 0.1054 | Most robust and most uniform — the risk landscape is flat and predictable. |

### Key Observations

1. **Insertos 1000** is the healthiest dataset: highest $R_E$ (0.39) and lowest normalized MAD_T (0.11), meaning the risk is evenly distributed and no single pair dominates.

2. **Catalog** is the most fragile: $R_E$ of 0.10 means the average pair is only 10% as sensitive as the worst pair — the risk is heavily concentrated in a small number of extreme pairs.

3. **Provincias** sits in between: moderate $R_E$ (0.36) but the highest normalized MAD_T (0.29), indicating that while the mean is reasonably close to the peak, the landscape is uneven with significant scatter around the average.

---

## Output Files

| File | Script | Format |
|---|---|---|
| `resultados/reporte_RE.json` | `indice_RE.py` | JSON array with R_E results per dataset |
| `resultados/reporte_MADt.json` | `indice_MADt.py` | JSON array with MAD_T results per dataset |

### JSON Structure — `reporte_RE.json`

```json
[
  {
    "archivo": "resultados/ISEC_provincias_Results.xlsx",
    "total_pares": 2590,
    "y_m": 10.2287,
    "mu_isec": 3.7147662548262548,
    "re": 0.36317090684312325,
    "isec_min": 1.0654,
    "isec_max": 10.2287,
    "isec_mediana": 3.6028,
    "isec_desv_std": 1.3051785127613789
  }
]
```

### JSON Structure — `reporte_MADt.json`

```json
[
  {
    "archivo": "resultados/ISEC_provincias_Results.xlsx",
    "total_pares_evaluados": 2590,
    "n_categorias": 259,
    "m_teorico": 33411,
    "mu_isec": 3.7147662548262548,
    "mad_t": 1.062765790849868,
    "mad_t_normalizado": 0.28609223782764637,
    "isec_min": 1.0654,
    "isec_max": 10.2287,
    "isec_mediana": 3.6028,
    "isec_desv_std": 1.3051785127613789
  }
]
```

---

## Reproducibility

To regenerate all results:

```bash
# R_E index
python indice_RE.py \
  resultados/ISEC_provincias_Results.xlsx \
  resultados/ISEC_catalog_Results.xlsx \
  resultados/ISEC_insertos1000_Results.xlsx \
  -o resultados/reporte_RE.json

# MAD_T index
python indice_MADt.py \
  resultados/ISEC_provincias_Results.xlsx \
  resultados/ISEC_catalog_Results.xlsx \
  resultados/ISEC_insertos1000_Results.xlsx \
  -o resultados/reporte_MADt.json
```

---

## Citation

If you use these indices in academic research, please cite:

```bibtex
@software{isec2026,
  title={ISEC: Índice de Sensibilidad al Error Categórico},
  author={Mauro A. Benetti},
  year={2026},
  url={https://github.com/mbenetti/ISEC}
}
```
