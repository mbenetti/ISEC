import numpy as np


class AnalizadorMorfologicoCMP:
    def __init__(self, k=0.1):
        self.k = k  # Constante de penalización (rigidez del "resorte")

        # 1. Definición de Costos Base (Priors)
        self.costos_base = {
            "transposicion": 0.6,
            "adicion": 1.5,
            "eliminacion": 1.5,
            "sustitucion_std": 0.7,
            "sustitucion_teclado": 0.5,  # Bajo costo por cercanía física
        }

        # 2. Matriz de Proximidad de Teclado (Simplificada)
        # Aquí defines qué pares de letras tienen "bajo costo"
        self.teclado_proximidad = {
            ("a", "s"): True,
            ("s", "a"): True,
            ("w", "e"): True,
            ("e", "w"): True,
            ("t", "g"): True,
            ("g", "t"): True,
            ("s", "z"): True,
            ("z", "s"): True,
            # Puedes expandir esta matriz según tu archivo de configuración
        }

    def calcular_cmp(self, s1, s2):
        """
        Calcula el Costo Medio Penalizado (CMP) entre dos cadenas.
        Implementa una variante de Damerau-Levenshtein con pesos.
        """
        if s1 == s2:
            return 0.0

        n, m = len(s1), len(s2)
        # Matriz de distancias para programación dinámica
        dp = np.zeros((n + 1, m + 1))
        # Diccionario para rastrear qué operaciones se usaron
        # Esto es vital para calcular el MC (Costo Medio) al final
        ops_realizadas = []

        # Inicialización de costos de inserción/borrado
        for i in range(n + 1):
            dp[i][0] = i * self.costos_base["eliminacion"]
        for j in range(m + 1):
            dp[0][j] = j * self.costos_base["adicion"]

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                # Caso: Los caracteres son iguales
                if s1[i - 1] == s2[j - 1]:
                    costo_sust = 0
                else:
                    # Caso: Sustitución (Verificar matriz de teclado)
                    par = (s1[i - 1], s2[j - 1])
                    costo_sust = (
                        self.costos_base["sustitucion_teclado"]
                        if par in self.teclado_proximidad
                        else self.costos_base["sustitucion_std"]
                    )

                # Operaciones Levenshtein básicas
                costo_del = self.costos_base["eliminacion"]
                costo_ins = self.costos_base["adicion"]

                dp[i][j] = min(
                    dp[i - 1][j] + costo_del,  # Eliminación
                    dp[i][j - 1] + costo_ins,  # Inserción
                    dp[i - 1][j - 1] + costo_sust,  # Sustitución
                )

                # Operación Damerau: Transposición (si aplica)
                if (
                    i > 1
                    and j > 1
                    and s1[i - 1] == s2[j - 2]
                    and s1[i - 2] == s2[j - 1]
                ):
                    dp[i][j] = min(
                        dp[i][j], dp[i - 2][j - 2] + self.costos_base["transposicion"]
                    )

        # --- EXTRACCIÓN DE METRICAS PARA LA FÓRMULA ---
        # En una implementación real, se debe hacer backtrack en la matriz dp
        # para obtener la lista exacta de costos aplicados.
        # Aquí simulamos el conteo de la ruta óptima para fines ilustrativos:

        # Ejemplo de recolección de costos de la ruta ganadora (Backtracking simplificado)
        costos_lista = self._obtener_lista_costos(s1, s2, dp)

        # CM (Costo Medio): El ancla. Incluye TODO.
        cm = np.mean(costos_lista) if costos_lista else 1.0

        # CP (Costos Penalizados): Excluye transposiciones (0.7)
        cp = sum([c for c in costos_lista if c != self.costos_base["transposicion"]])

        # --- FÓRMULA FINAL ---
        cmp = cm + (self.k * cp)

        return round(cmp, 4), cm, cp

    def _obtener_lista_costos(self, s1, s2, dp):
        """
        Función auxiliar de backtracking para recuperar los costos individuales
        de las operaciones realizadas en la ruta mínima.
        """
        i, j = len(s1), len(s2)
        costos = []
        while i > 0 or j > 0:
            actual = dp[i][j]
            # Lógica para identificar qué operación nos trajo aquí comparando costos
            if i > 0 and j > 0 and s1[i - 1] == s2[j - 1]:
                i -= 1
                j -= 1
            elif (
                i > 0
                and j > 0
                and actual
                == dp[i - 1][j - 1]
                + (
                    self.costos_base["sustitucion_teclado"]
                    if (s1[i - 1], s2[j - 1]) in self.teclado_proximidad
                    else self.costos_base["sustitucion_std"]
                )
            ):
                costos.append(
                    self.costos_base["sustitucion_teclado"]
                    if (s1[i - 1], s2[j - 1]) in self.teclado_proximidad
                    else self.costos_base["sustitucion_std"]
                )
                i -= 1
                j -= 1
            elif i > 0 and actual == dp[i - 1][j] + self.costos_base["eliminacion"]:
                costos.append(self.costos_base["eliminacion"])
                i -= 1
            elif j > 0 and actual == dp[i][j - 1] + self.costos_base["adicion"]:
                costos.append(self.costos_base["adicion"])
                j -= 1
            else:  # Transposición
                costos.append(self.costos_base["transposicion"])
                i -= 2
                j -= 2
        return costos


# --- PRUEBA DEL MODELO ---
analizador = AnalizadorMorfologicoCMP(k=0.1)

palabras = [
    ("XDKT11T3", "XDKG11T3"),  # Caso 1: Bajo costo (Sustitución teclado)
    ("XDKT11T3", "LDKT11T3"),  # Caso 2: Costo Estándar
    ("XDKT11T3", "LDKT11T3QET"),  # Caso 3: Divergencia alta
]

print(f"{'Palabra A':<15} | {'Palabra B':<15} | {'CM':<6} | {'CP':<6} | {'CMP':<8}")
print("-" * 65)
for p1, p2 in palabras:
    cmp, cm, cp = analizador.calcular_cmp(p1, p2)
    print(f"{p1:<15} | {p2:<15} | {cm:<6.2f} | {cp:<6.2f} | {cmp:<8.2f}")
