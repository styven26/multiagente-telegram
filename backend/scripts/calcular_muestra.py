"""Calculo del tamano muestral para el contraste del Ciclo 3.

Determina cuantos estudiantes por grupo se necesitan para detectar una
diferencia entre ruta adaptativa y secuencia fija, segun el tamano de
efecto que se quiera poder detectar.

Uso:
    python -m scripts.calcular_muestra
"""

from statsmodels.stats.power import TTestIndPower

ALFA = 0.05        # significancia
POTENCIA = 0.80    # 1 - beta, convencion habitual

analisis = TTestIndPower()

print(f"alfa = {ALFA}   potencia = {POTENCIA}   prueba de dos colas\n")
print(f"{'d de Cohen':<14}{'n por grupo':>13}{'n total':>10}")
print("-" * 37)

for d in (0.2, 0.3, 0.5, 0.8):
    n = analisis.solve_power(effect_size=d, alpha=ALFA, power=POTENCIA,
                             alternative="two-sided")
    import math
    n = math.ceil(n)
    print(f"{d:<14}{n:>13}{n * 2:>10}")

# La otra cara: con la muestra que sí tenemos, ¿qué efecto detectaríamos?
print()
for n in (15, 30):
    d = analisis.solve_power(nobs1=n, alpha=ALFA, power=POTENCIA,
                             alternative="two-sided")
    print(f"Con {n} por grupo solo se detectaria un efecto de d >= {d:.2f}")