import argparse
import math
import random
from pathlib import Path

import matplotlib.pyplot as plt

TOTAL_NUMEROS_RULETA = 37
VALOR_ESPERADO = 18
VARIANZA_TEORICA = 114
DESVIO_TEORICO = math.sqrt(VARIANZA_TEORICA)
FRECUENCIA_TEORICA = 1 / TOTAL_NUMEROS_RULETA


def crear_parser() -> argparse.ArgumentParser:
    """Configura y devuelve el parser de argumentos de la CLI."""
    parser = argparse.ArgumentParser(
        description=(
            'Simulación de ruleta con métricas acumuladas y gráficos comparables '
            'contra valores teóricos.'
        )
    )
    parser.add_argument(
        '--tiradas',
        type=int,
        required=True,
        help='Cantidad de tiradas por corrida.',
    )
    parser.add_argument(
        '--corridas',
        type=int,
        required=True,
        help='Cantidad de corridas independientes.',
    )
    parser.add_argument(
        '--numero',
        type=int,
        required=True,
        help='Número elegido por el jugador (entre 0 y 36).',
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=None,
        help='Semilla opcional para obtener resultados reproducibles.',
    )
    parser.add_argument(
        '--salida',
        type=str,
        default='ruleta_metricas.png',
        help='Ruta del archivo PNG de salida.',
    )
    parser.add_argument(
        '--mostrar',
        action='store_true',
        help='Muestra la figura en pantalla además de guardarla.',
    )
    return parser


def validar_argumentos(cant_tiradas: int, cant_corridas: int, mi_numero: int) -> None:
    """Valida los parámetros de entrada para evitar simulaciones inválidas."""
    if cant_tiradas <= 0:
        raise ValueError('La cantidad de tiradas debe ser mayor que 0.')
    if cant_corridas <= 0:
        raise ValueError('La cantidad de corridas debe ser mayor que 0.')
    if not (0 <= mi_numero <= 36):
        raise ValueError('El número elegido debe estar entre 0 y 36.')


def inicializar_metricas() -> dict[str, list[float]]:
    """Crea la estructura que guarda las series acumuladas de una corrida."""
    return {
        'frecuencia_relativa': [],
        'promedio': [],
        'desvio_estandar': [],
        'varianza': [],
    }


def simular_corrida(cant_tiradas: int, mi_numero: int, generador: random.Random) -> dict[str, list[float]]:
    """Simula una corrida y calcula métricas acumuladas con actualización incremental.

    Se utiliza el algoritmo de Welford para media y varianza muestral, lo que evita
    reconstruir la muestra completa en cada paso. Esto mejora el rendimiento y, al
    mismo tiempo, alinea el cálculo con la interpretación estadística del informe.
    """
    metricas = inicializar_metricas()

    aciertos_numero = 0
    media = 0.0
    suma_cuadrados = 0.0

    for indice in range(1, cant_tiradas + 1):
        valor = generador.randint(0, 36)

        if valor == mi_numero:
            aciertos_numero += 1
        frecuencia_relativa = aciertos_numero / indice
        metricas['frecuencia_relativa'].append(frecuencia_relativa)

        delta = valor - media
        media += delta / indice
        delta_2 = valor - media
        suma_cuadrados += delta * delta_2
        metricas['promedio'].append(media)

        if indice < 2:
            metricas['varianza'].append(float('nan'))
            metricas['desvio_estandar'].append(float('nan'))
        else:
            varianza_muestral = suma_cuadrados / (indice - 1)
            metricas['varianza'].append(varianza_muestral)
            metricas['desvio_estandar'].append(math.sqrt(varianza_muestral))

    return metricas


def simular_ruleta(
    cant_tiradas: int,
    cant_corridas: int,
    mi_numero: int,
    seed: int | None = None,
) -> dict[str, list[list[float]]]:
    """Ejecuta todas las corridas y agrupa las series de cada métrica."""
    generador = random.Random(seed)
    resultados = {
        'frecuencia_relativa': [],
        'promedio': [],
        'desvio_estandar': [],
        'varianza': [],
    }

    for _ in range(cant_corridas):
        corrida = simular_corrida(cant_tiradas, mi_numero, generador)
        for nombre_metrica, serie in corrida.items():
            resultados[nombre_metrica].append(serie)

    return resultados


def promedio_por_tirada(series: list[list[float]]) -> list[float]:
    """Calcula el promedio entre corridas para cada número de tirada."""
    cantidad_tiradas = len(series[0])
    promedios = []

    for indice in range(cantidad_tiradas):
        valores = [serie[indice] for serie in series if not math.isnan(serie[indice])]
        if not valores:
            promedios.append(float('nan'))
            continue
        promedios.append(sum(valores) / len(valores))

    return promedios


def percentiles_por_tirada(series: list[list[float]], percentil: float) -> list[float]:
    """Calcula percentiles simples por tirada para sombrear la dispersión."""
    cantidad_tiradas = len(series[0])
    percentiles = []

    for indice in range(cantidad_tiradas):
        valores = sorted(serie[indice] for serie in series if not math.isnan(serie[indice]))
        if not valores:
            percentiles.append(float('nan'))
            continue

        posicion = (len(valores) - 1) * percentil
        inferior = math.floor(posicion)
        superior = math.ceil(posicion)

        if inferior == superior:
            percentiles.append(valores[inferior])
            continue

        fraccion = posicion - inferior
        valor = valores[inferior] + (valores[superior] - valores[inferior]) * fraccion
        percentiles.append(valor)

    return percentiles


def resumen_final(resultados: dict[str, list[list[float]]]) -> dict[str, float]:
    """Resume la última observación de cada corrida para reportar valores globales."""
    resumen = {}
    for nombre_metrica, series in resultados.items():
        finales = [serie[-1] for serie in series if not math.isnan(serie[-1])]
        resumen[nombre_metrica] = sum(finales) / len(finales)
    return resumen


def configurar_eje(ax, titulo: str, xlabel: str, ylabel: str) -> None:
    """Aplica formato visual consistente a cada subplot."""
    ax.set_title(titulo)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.25)


def graficar_metrica(
    ax,
    x,
    series: list[list[float]],
    titulo: str,
    ylabel: str,
    referencia_teorica: float,
    etiqueta_teorica: str,
) -> None:
    """Grafica todas las corridas, la media por tirada y la banda interpercentil.

    Esta visualización es más útil para el informe que una línea horizontal con el
    promedio global de todos los puntos, porque permite ver convergencia, dispersión
    y comparación con el valor teórico en cada instante de la simulación.
    """
    for serie in series:
        ax.plot(x, serie, color='steelblue', alpha=0.18, linewidth=1)

    promedio = promedio_por_tirada(series)
    p10 = percentiles_por_tirada(series, 0.10)
    p90 = percentiles_por_tirada(series, 0.90)

    ax.plot(x, promedio, color='navy', linewidth=2.2, label='Promedio entre corridas')
    ax.fill_between(x, p10, p90, color='cornflowerblue', alpha=0.2, label='Percentiles 10-90')
    ax.axhline(
        referencia_teorica,
        color='crimson',
        linestyle='--',
        linewidth=1.8,
        label=etiqueta_teorica,
    )

    configurar_eje(ax, titulo, 'Cantidad de tiradas', ylabel)
    ax.legend(loc='best')


def graficar_resultados(
    resultados: dict[str, list[list[float]]],
    cant_tiradas: int,
    mi_numero: int,
    archivo_salida: str,
    mostrar: bool,
) -> None:
    """Genera una figura resumen apta para insertarse en el informe LaTeX."""
    x = list(range(1, cant_tiradas + 1))
    fig, axs = plt.subplots(2, 2, figsize=(14, 9), dpi=150)

    graficar_metrica(
        axs[0, 0],
        x,
        resultados['frecuencia_relativa'],
        f'Frecuencia relativa acumulada del número {mi_numero}',
        'Frecuencia relativa',
        FRECUENCIA_TEORICA,
        'Valor teórico = 1/37',
    )
    graficar_metrica(
        axs[0, 1],
        x,
        resultados['promedio'],
        'Promedio acumulado de las tiradas',
        'Promedio',
        VALOR_ESPERADO,
        'Valor teórico = 18',
    )
    graficar_metrica(
        axs[1, 0],
        x,
        resultados['desvio_estandar'],
        'Desvío estándar muestral acumulado',
        'Desvío estándar',
        DESVIO_TEORICO,
        'Valor teórico = √114',
    )
    graficar_metrica(
        axs[1, 1],
        x,
        resultados['varianza'],
        'Varianza muestral acumulada',
        'Varianza',
        VARIANZA_TEORICA,
        'Valor teórico = 114',
    )

    fig.suptitle('Simulación de ruleta: convergencia empírica vs. valores teóricos', fontsize=14)
    fig.tight_layout()

    ruta_salida = Path(archivo_salida)
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ruta_salida, bbox_inches='tight')

    if mostrar:
        plt.show()
    else:
        plt.close(fig)


def imprimir_resumen(resumen: dict[str, float]) -> None:
    """Imprime un resumen numérico útil para redactar la sección de resultados."""
    print('Resumen final promedio entre corridas:')
    print(f"- Frecuencia relativa: {resumen['frecuencia_relativa']:.4f} (teórico: {FRECUENCIA_TEORICA:.4f})")
    print(f"- Promedio: {resumen['promedio']:.4f} (teórico: {VALOR_ESPERADO:.4f})")
    print(f"- Desvío estándar: {resumen['desvio_estandar']:.4f} (teórico: {DESVIO_TEORICO:.4f})")
    print(f"- Varianza: {resumen['varianza']:.4f} (teórico: {VARIANZA_TEORICA:.4f})")


def main() -> None:
    """Orquesta validación, simulación, graficación y reporte final."""
    parser = crear_parser()
    args = parser.parse_args()

    validar_argumentos(args.tiradas, args.corridas, args.numero)

    resultados = simular_ruleta(
        cant_tiradas=args.tiradas,
        cant_corridas=args.corridas,
        mi_numero=args.numero,
        seed=args.seed,
    )
    resumen = resumen_final(resultados)

    graficar_resultados(
        resultados=resultados,
        cant_tiradas=args.tiradas,
        mi_numero=args.numero,
        archivo_salida=args.salida,
        mostrar=args.mostrar,
    )
    imprimir_resumen(resumen)


if __name__ == '__main__':
    main()
