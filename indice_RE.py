"""
Índice de Robustez del Espacio Categórico (R_E)

Calcula un índice de robustez agregado a partir de los puntajes ISEC
individuales producidos por ISEC.py.

Fórmula:

    R_E = 1 - (y_m - mu_ISEC) / y_m = mu_ISEC / y_m

Donde:
    - y_m       : puntaje ISEC máximo (par categórico más vulnerable).
    - mu_ISEC   : media aritmética de los puntajes ISEC del espacio activo.

Interpretación:
    R_E ∈ (0, 1]
      - R_E cercano a 1  → espacio robusto: la media se acerca al máximo,
        es decir, la mayoría de los pares son igualmente sensibles
        (poco margen para que un par destacado sea confundido).
      - R_E cercano a 0  → espacio frágil: existe al menos un par
        categórico mucho más sensible que el promedio, concentrando
        el riesgo de error categórico.

Uso:
    # Sobre un archivo de resultados de ISEC (Excel)
    python indice_RE.py resultados/ISEC_provincias_Results.xlsx

    # Especificar archivo de salida
    python indice_RE.py resultados/ISEC_provincias_Results.xlsx -o reporte_RE.json

    # Sobre varios archivos a la vez
    python indice_RE.py resultados/*.xlsx

    # Desde Python
    from indice_RE import calcular_RE
    re = calcular_RE("resultados/ISEC_provincias_Results.xlsx")
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

import pandas as pd


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

ISEC_SCORE_COLUMN = "ISEC_Score"
SUPPORTED_EXTENSIONS = {".xlsx", ".xls"}


# ---------------------------------------------------------------------------
# Resultado
# ---------------------------------------------------------------------------


@dataclass
class ResultadoRE:
    """Contenedor del cálculo del índice R_E."""

    archivo: str
    total_pares: int
    y_m: float  # puntaje ISEC máximo
    mu_isec: float  # media aritmética de puntajes ISEC
    re: float  # índice de robustez R_E
    isec_min: float
    isec_max: float
    isec_mediana: float
    isec_desv_std: float

    def to_dict(self) -> dict:
        return asdict(self)

    def resumen_texto(self) -> str:
        """Devuelve un resumen legible del cálculo."""
        return (
            f"Archivo            : {self.archivo}\n"
            f"Pares analizados   : {self.total_pares}\n"
            f"y_m  (ISEC máximo) : {self.y_m:.6f}\n"
            f"mu   (ISEC medio)  : {self.mu_isec:.6f}\n"
            f"R_E                : {self.re:.6f}\n"
            f"---\n"
            f"ISEC mínimo        : {self.isec_min:.6f}\n"
            f"ISEC máximo        : {self.isec_max:.6f}\n"
            f"ISEC mediana       : {self.isec_mediana:.6f}\n"
            f"ISEC desv. estándar: {self.isec_desv_std:.6f}"
        )


# ---------------------------------------------------------------------------
# Núcleo de cálculo
# ---------------------------------------------------------------------------


def _cargar_puntajes_isec(archivo: str | Path) -> pd.Series:
    """
    Lee un archivo Excel de resultados de ISEC y devuelve la columna
    de puntajes ISEC como una Serie de pandas.

    Args:
        archivo: Ruta al archivo Excel (.xlsx) con resultados de ISEC.

    Returns:
        Serie de pandas con los puntajes ISEC individuales.

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

    puntajes = df[ISEC_SCORE_COLUMN].dropna()

    if puntajes.empty:
        raise ValueError(
            f"El archivo '{ruta.name}' no contiene puntajes ISEC válidos."
        )

    return puntajes


def calcular_RE(
    archivo: str | Path,
    *,
    columna: str | None = None,
) -> ResultadoRE:
    """
    Calcula el índice de robustez R_E a partir de un archivo de
    resultados de ISEC.

    Fórmula:

        R_E = mu_ISEC / y_m

    Args:
        archivo:  Ruta al archivo Excel con resultados de ISEC.
        columna:  Nombre alternativo de la columna de puntajes ISEC.
                  Por defecto usa 'ISEC_Score'.

    Returns:
        ResultadoRE con todos los valores del cálculo.
    """
    col = columna or ISEC_SCORE_COLUMN
    puntajes = _cargar_puntajes_isec(archivo) if col == ISEC_SCORE_COLUMN else None

    if puntajes is None:
        ruta = Path(archivo)
        df = pd.read_excel(ruta)
        if col not in df.columns:
            raise ValueError(
                f"El archivo no contiene la columna '{col}'."
            )
        puntajes = df[col].dropna()

    y_m = float(puntajes.max())
    mu_isec = float(puntajes.mean())

    # Caso límite: si y_m es 0 (todos los puntajes son 0), R_E se define como 1
    # (no hay sensibilidad detectada → espacio perfectamente robusto).
    if y_m == 0:
        re = 1.0
    else:
        re = mu_isec / y_m

    return ResultadoRE(
        archivo=str(archivo),
        total_pares=len(puntajes),
        y_m=y_m,
        mu_isec=mu_isec,
        re=re,
        isec_min=float(puntajes.min()),
        isec_max=y_m,
        isec_mediana=float(puntajes.median()),
        isec_desv_std=float(puntajes.std(ddof=0)),
    )


def calcular_RE_multiples(
    archivos: Iterable[str | Path],
    *,
    columna: str | None = None,
) -> list[ResultadoRE]:
    """
    Calcula R_E para múltiples archivos de resultados ISEC.

    Args:
        archivos: Iterable de rutas a archivos Excel.
        columna:  Nombre alternativo de la columna de puntajes.

    Returns:
        Lista de ResultadoRE, uno por archivo.
    """
    resultados = []
    for archivo in archivos:
        try:
            res = calcular_RE(archivo, columna=columna)
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
            "Calcula el índice de robustez R_E a partir de resultados ISEC.\n\n"
            "Fórmula: R_E = mu_ISEC / y_m"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Ejemplos:\n"
            "  python indice_RE.py resultados/ISEC_provincias_Results.xlsx\n"
            "  python indice_RE.py resultados/*.xlsx -o reporte.json\n"
            "  python indice_RE.py resultados/ -o reporte.json"
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
    print("Índice de Robustez del Espacio Categórico (R_E)")
    print("Fórmula: R_E = mu_ISEC / y_m")
    print("=" * 70)

    resultados = calcular_RE_multiples(rutas, columna=args.columna)

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
        print(f"{'Archivo':<50} {'R_E':>10}")
        print("-" * 62)
        for res in resultados:
            nombre = Path(res.archivo).name
            print(f"{nombre:<50} {res.re:>10.6f}")

    # Guardar JSON si se solicitó
    if args.output:
        salida = Path(args.output)
        datos = [res.to_dict() for res in resultados]
        with open(salida, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Resultados guardados en: {salida}")


if __name__ == "__main__":
    main()
