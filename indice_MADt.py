"""
Mean Absolute Taxonomic Fragility Deviation (MAD_T)

Calcula la desviación media absoluta de los puntajes ISEC respecto a su
media aritmética, sobre TODAS las filas del archivo de resultados.

Cada fila del Excel representa un cálculo ISEC independiente para un par
(sentence, matched_sentence) en un Match_Rank dado. No se aplica ningún
filtro de deduplicación: todos los valores ISEC son válidos. Esto es
importante porque el top-k semántico utiliza recuperación aproximada (ANN),
y el ISEC final combina distancia semántica + morfológica + frecuencia
mediana empírica. Un par puede tener su ISEC más alto en un Match_Rank
intermedio, no necesariamente en el rank 1.

Fórmula:

            1   M
    MAD_T = - · Σ  | ISEC_k - mu_ISEC |
            M  k=1

Donde:
    - M        : total de filas evaluadas en el Excel (sin deduplicar).
                 Cada fila = un cálculo ISEC independiente.
    - N        : número de categorías únicas (solo referencia informativa).
    - N(N-1)/2 : M teórico de pares únicos no reflexivos (solo referencia,
                 NO se usa en el cálculo de MAD_T).
    - ISEC_k   : puntaje de fragilidad del par k (fila k del Excel).
    - mu_ISEC  : media aritmética de los puntajes ISEC sobre las M filas.

Interpretación:
    MAD_T ≥ 0
      - MAD_T cercano a 0 → paisaje de riesgo plano y uniforme: todos los
        pares categóricos tienen sensibilidad similar, el fallo es predecible
        y cohesivo.
      - MAD_T alto → dispersión de riesgo: existe gran variabilidad entre
        pares, el fallo se concentra en zonas específicas del espacio
        taxonómico, haciendo el sistema menos predecible.

Relación con R_E:
    R_E mide la robustez global (cercanía de la media al máximo), mientras
    que MAD_T mide la dispersión absoluta promedio. Un espacio puede tener
    un R_E alto (media cercana al máximo) pero un MAD_T alto si los valores
    están muy esparcidos. Ambos índices son complementarios.

Uso:
    # Sobre un archivo de resultados de ISEC (Excel)
    python indice_MADt.py resultados/ISEC_provincias_Results.xlsx

    # Especificar archivo de salida
    python indice_MADt.py resultados/ISEC_provincias_Results.xlsx -o reporte_MADt.json

    # Sobre varios archivos a la vez
    python indice_MADt.py resultados/*.xlsx

    # Desde Python
    from indice_MADt import calcular_MADt
    madt = calcular_MADt("resultados/ISEC_provincias_Results.xlsx")
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

ISEC_SCORE_COLUMN = "ISEC_Score"
SENTENCE_COLUMN = "Sentence"
MATCHED_SENTENCE_COLUMN = "Matched_Sentence"
SUPPORTED_EXTENSIONS = {".xlsx", ".xls"}


# ---------------------------------------------------------------------------
# Resultado
# ---------------------------------------------------------------------------


@dataclass
class ResultadoMADt:
    """Contenedor del cálculo del índice MAD_T."""

    archivo: str
    total_pares_evaluados: int  # M — todas las filas del Excel (sin deduplicar)
    n_categorias: int  # número de categorías únicas (N) — solo informativo
    m_teorico: int  # N(N-1)/2 — referencia teórica, NO se usa en el cálculo
    mu_isec: float  # media aritmética de ISEC sobre todas las filas
    mad_t: float  # índice MAD_T = (1/M) · Σ |ISEC_k - mu_ISEC|
    mad_t_normalizado: float  # MAD_T / mu_ISEC (desviación relativa)
    isec_min: float
    isec_max: float
    isec_mediana: float
    isec_desv_std: float

    def to_dict(self) -> dict:
        return asdict(self)

    def resumen_texto(self) -> str:
        """Devuelve un resumen legible del cálculo."""
        return (
            f"Archivo                       : {self.archivo}\n"
            f"M (pares evaluados, todas las filas): {self.total_pares_evaluados}\n"
            f"Categorías únicas (N, ref.)   : {self.n_categorias}\n"
            f"M teórico N(N-1)/2 (ref.)     : {self.m_teorico}\n"
            f"mu_ISEC (media sobre M)       : {self.mu_isec:.6f}\n"
            f"MAD_T                         : {self.mad_t:.6f}\n"
            f"MAD_T normalizado             : {self.mad_t_normalizado:.6f}\n"
            f"---\n"
            f"ISEC mínimo                   : {self.isec_min:.6f}\n"
            f"ISEC máximo                   : {self.isec_max:.6f}\n"
            f"ISEC mediana                  : {self.isec_mediana:.6f}\n"
            f"ISEC desv. estándar           : {self.isec_desv_std:.6f}"
        )


# ---------------------------------------------------------------------------
# Núcleo de cálculo
# ---------------------------------------------------------------------------


def _cargar_datos_isec(archivo: str | Path) -> pd.DataFrame:
    """
    Lee un archivo Excel de resultados de ISEC y devuelve el DataFrame.

    Args:
        archivo: Ruta al archivo Excel (.xlsx) con resultados de ISEC.

    Returns:
        DataFrame de pandas con los resultados.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si el archivo no tiene la columna ISEC_Score.
    """
    ruta = Path(archivo)
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")

    df = pd.read_excel(ruta)

    if ISEC_SCORE_COLUMN not in df.columns:
        disponibles = ", ".join(df.columns)
        raise ValueError(
            f"El archivo '{ruta.name}' no contiene la columna "
            f"'{ISEC_SCORE_COLUMN}'.\n"
            f"Columnas encontradas: {disponibles}"
        )

    # Filtrar filas con puntaje válido
    df = df.dropna(subset=[ISEC_SCORE_COLUMN])

    if df.empty:
        raise ValueError(
            f"El archivo '{ruta.name}' no contiene puntajes ISEC válidos."
        )

    return df


def _contar_categorias_unicas(df: pd.DataFrame) -> int:
    """
    Cuenta el número de categorías únicas (N) a partir de las columnas
    'Sentence' y 'Matched_Sentence'.

    Args:
        df: DataFrame con resultados de ISEC.

    Returns:
        Número de categorías únicas.
    """
    categorias: set[str] = set()

    if SENTENCE_COLUMN in df.columns:
        categorias.update(df[SENTENCE_COLUMN].dropna().unique())

    if MATCHED_SENTENCE_COLUMN in df.columns:
        categorias.update(df[MATCHED_SENTENCE_COLUMN].dropna().unique())

    return len(categorias)


def calcular_MADt(
    archivo: str | Path,
    *,
    columna: str | None = None,
) -> ResultadoMADt:
    """
    Calcula el índice MAD_T a partir de un archivo de resultados de ISEC.

    Fórmula:

        MAD_T = (1 / M) * Σ |ISEC_k - mu_ISEC|

    Args:
        archivo:  Ruta al archivo Excel con resultados de ISEC.
        columna:  Nombre alternativo de la columna de puntajes ISEC.
                  Por defecto usa 'ISEC_Score'.

    Returns:
        ResultadoMADt con todos los valores del cálculo.
    """
    col = columna or ISEC_SCORE_COLUMN
    df = _cargar_datos_isec(archivo)

    if col not in df.columns:
        raise ValueError(
            f"El archivo no contiene la columna '{col}'."
        )

    # Usar TODAS las filas del Excel — cada fila es un cálculo ISEC
    # independiente (sentence × match_rank). No se aplica ningún filtro
    # de deduplicación: todos los valores ISEC son válidos porque el
    # top-k semántico (ANN) recupera vecinos aproximados, y el ISEC final
    # combina distancia semántica + morfológica + frecuencia mediana.
    # Un par puede tener su ISEC más alto en un Match_Rank intermedio,
    # no necesariamente en el rank 1.
    puntajes = df[col].dropna().astype(float)
    M = len(puntajes)  # M = total de filas evaluadas (sin deduplicar)

    mu_isec = float(puntajes.mean())

    # Desviaciones absolutas respecto a la media
    desviaciones_abs = (puntajes - mu_isec).abs()
    mad_t = float(desviaciones_abs.mean())

    # MAD_T normalizado: desviación relativa respecto a la media
    if mu_isec != 0:
        mad_t_norm = mad_t / mu_isec
    else:
        mad_t_norm = 0.0

    # Contar categorías únicas y calcular M teórico
    n_categorias = _contar_categorias_unicas(df)
    m_teorico = n_categorias * (n_categorias - 1) // 2 if n_categorias > 1 else 0

    return ResultadoMADt(
        archivo=str(archivo),
        total_pares_evaluados=M,
        n_categorias=n_categorias,
        m_teorico=m_teorico,
        mu_isec=mu_isec,
        mad_t=mad_t,
        mad_t_normalizado=mad_t_norm,
        isec_min=float(puntajes.min()),
        isec_max=float(puntajes.max()),
        isec_mediana=float(puntajes.median()),
        isec_desv_std=float(puntajes.std(ddof=0)),
    )


def calcular_MADt_multiples(
    archivos: Iterable[str | Path],
    *,
    columna: str | None = None,
) -> list[ResultadoMADt]:
    """
    Calcula MAD_T para múltiples archivos de resultados ISEC.

    Args:
        archivos: Iterable de rutas a archivos Excel.
        columna:  Nombre alternativo de la columna de puntajes.

    Returns:
        Lista de ResultadoMADt, uno por archivo.
    """
    resultados = []
    for archivo in archivos:
        try:
            res = calcular_MADt(archivo, columna=columna)
            resultados.append(res)
        except (FileNotFoundError, ValueError) as e:
            print(f"⚠ {e}", file=sys.stderr)
    return resultados


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _expandir_archivos(args_archivos: list[str]) -> list[Path]:
    """Expande rutas y filtra solo archivos Excel soportados."""
    rutas: list[Path] = []
    for a in args_archivos:
        p = Path(a)
        if p.is_dir():
            rutas.extend(
                f for f in p.iterdir() if f.suffix.lower() in SUPPORTED_EXTENSIONS
            )
        elif p.suffix.lower() in SUPPORTED_EXTENSIONS:
            rutas.append(p)
        else:
            print(f"⚠ Ignorando archivo no soportado: {a}", file=sys.stderr)
    return rutas


def main() -> None:
    """Punto de entrada CLI."""
    parser = argparse.ArgumentParser(
        description=(
            "Calcula el índice MAD_T (Mean Absolute Taxonomic Fragility "
            "Deviation) a partir de resultados ISEC.\n\n"
            "Fórmula: MAD_T = (1/M) * Σ |ISEC_k - mu_ISEC|"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Ejemplos:\n"
            "  python indice_MADt.py resultados/ISEC_provincias_Results.xlsx\n"
            "  python indice_MADt.py resultados/*.xlsx -o reporte.json\n"
            "  python indice_MADt.py resultados/ -o reporte.json"
        ),
    )
    parser.add_argument(
        "archivos",
        nargs="+",
        help="Archivo(s) Excel de resultados ISEC o directorio que los contenga.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Archivo JSON de salida para guardar los resultados.",
    )
    parser.add_argument(
        "-c",
        "--columna",
        default=None,
        help="Nombre alternativo de la columna de puntajes ISEC "
        "(por defecto: 'ISEC_Score').",
    )
    args = parser.parse_args()

    rutas = _expandir_archivos(args.archivos)
    if not rutas:
        print("✗ No se encontraron archivos Excel válidos.", file=sys.stderr)
        sys.exit(1)

    print("=" * 70)
    print("Mean Absolute Taxonomic Fragility Deviation (MAD_T)")
    print("Fórmula: MAD_T = (1/M) · Σ |ISEC_k - mu_ISEC|")
    print("=" * 70)

    resultados = calcular_MADt_multiples(rutas, columna=args.columna)

    if not resultados:
        print("✗ No se pudieron procesar archivos.", file=sys.stderr)
        sys.exit(1)

    for res in resultados:
        print()
        print(res.resumen_texto())
        print("-" * 70)

    # Resumen comparativo si hay múltiples archivos
    if len(resultados) > 1:
        print("\nResumen comparativo:")
        print(
            f"{'Archivo':<50} {'N':>6} {'M':>8} "
            f"{'mu_ISEC':>10} {'MAD_T':>10} {'MAD_T/mu':>10}"
        )
        print("-" * 96)
        for res in resultados:
            nombre = Path(res.archivo).name
            print(
                f"{nombre:<50} {res.n_categorias:>6} {res.m_teorico:>8} "
                f"{res.mu_isec:>10.4f} {res.mad_t:>10.4f} "
                f"{res.mad_t_normalizado:>10.4f}"
            )

    # Guardar JSON si se solicitó
    if args.output:
        salida = Path(args.output)
        datos = [res.to_dict() for res in resultados]
        with open(salida, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Resultados guardados en: {salida}")


if __name__ == "__main__":
    main()
