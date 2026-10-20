"""Análisis comparativo de eficiencia (time.perf_counter, promedio de 5 ejecuciones).

Solo se cronometra la operación medida: la preparación (setup) queda fuera.
"""
import time

from lista_simple import ListaSimple
from lista_doble import ListaDoble
from cola_simple import ColaSimple
from cola_circular import ColaCircular
from cola_prioridad import ColaPrioridad

TAMANOS = (1000, 5000, 10000)
OPERACIONES_COLA = 10000
REPETICIONES = 5


def _medir(operacion, preparar=None, repeticiones=REPETICIONES):
    """Promedio (s) de `operacion(obj)`; `obj = preparar()` se crea fuera del cronómetro."""
    total = 0.0
    for _ in range(repeticiones):
        obj = preparar() if preparar else None
        t0 = time.perf_counter()
        operacion(obj)
        total += time.perf_counter() - t0
    return total / repeticiones


def _lista_simple(n):
    lista = ListaSimple()
    for i in range(n):
        lista.insertar(i)
    return lista


def _lista_doble(n):
    lista = ListaDoble()
    for i in range(n):
        lista.insertar_final(i)
    return lista


def _posiciones(n):
    return (("inicio", 0), ("medio", n // 2), ("fin", n - 1))


def _llenar(cola_cls, n):
    cola = cola_cls()
    for i in range(n):
        if cola_cls is ColaPrioridad:
            cola.enqueue({'v': i}, (i % 5) + 1)
        else:
            cola.enqueue(i)
    return cola


def ejecutar_benchmarks(tamanos=TAMANOS, ops_cola=OPERACIONES_COLA,
                        repeticiones=REPETICIONES):
    """Devuelve una lista de filas (escenario, n, promedio_s)."""
    filas = []

    for n in tamanos:                                           # 1) inserción
        def insertar(_, n=n):
            lista = ListaSimple()
            for i in range(n):
                lista.insertar(i)
        filas.append(("Inserción ListaSimple (final)", n, _medir(insertar, None, repeticiones)))

    for n in tamanos:                                           # 2) búsqueda
        lista = _lista_simple(n)
        for etiqueta, objetivo in _posiciones(n):
            filas.append((f"Búsqueda ListaSimple ({etiqueta})", n,
                          _medir(lambda _, o=objetivo: lista.buscar(lambda v: v == o),
                                 None, repeticiones)))

    for n in tamanos:                                           # 3) eliminación
        for etiqueta, objetivo in _posiciones(n):
            filas.append((f"Eliminación ListaSimple ({etiqueta})", n,
                          _medir(lambda l, o=objetivo: l.eliminar(lambda v: v == o),
                                 lambda n=n: _lista_simple(n), repeticiones)))
            filas.append((f"Eliminación ListaDoble ({etiqueta})", n,
                          _medir(lambda l, o=objetivo: l.eliminar(lambda v: v == o),
                                 lambda n=n: _lista_doble(n), repeticiones)))

    for nombre, cls in (("ColaSimple", ColaSimple), ("ColaCircular", ColaCircular),
                        ("ColaPrioridad", ColaPrioridad)):       # 4) throughput
        def encolar(_, cls=cls):
            _llenar(cls, ops_cola)

        def desencolar(cola):
            for _ in range(ops_cola):
                cola.dequeue()
        filas.append((f"{nombre}: enqueue", ops_cola, _medir(encolar, None, repeticiones)))
        filas.append((f"{nombre}: dequeue", ops_cola,
                      _medir(desencolar, lambda cls=cls: _llenar(cls, ops_cola), repeticiones)))
    return filas


def _t(filas, escenario, n):
    for e, nn, t in filas:
        if e == escenario and nn == n:
            return t
    return None


def generar_insights(filas, tamanos=TAMANOS, ops_cola=OPERACIONES_COLA):
    """Comentarios derivados de los datos medidos (no texto fijo)."""
    chico, grande = tamanos[0], tamanos[-1]
    insights = []

    t_c, t_g = _t(filas, "Inserción ListaSimple (final)", chico), \
        _t(filas, "Inserción ListaSimple (final)", grande)
    if t_c and t_g:
        insights.append(
            f"Inserción: al pasar de n={chico} a n={grande} (x{grande // chico}) el tiempo "
            f"creció x{t_g / t_c:.1f}; es lineal en total, es decir O(1) por inserción "
            f"gracias al puntero a la cola.")

    b_i, b_f = _t(filas, "Búsqueda ListaSimple (inicio)", grande), \
        _t(filas, "Búsqueda ListaSimple (fin)", grande)
    if b_i and b_f:
        insights.append(
            f"Búsqueda: con n={grande}, buscar al fin costó x{b_f / b_i:,.0f} más que al "
            f"inicio: la lista no permite acceso directo, es O(n).")

    es, ed = _t(filas, "Eliminación ListaSimple (medio)", grande), \
        _t(filas, "Eliminación ListaDoble (medio)", grande)
    if es and ed:
        insights.append(
            f"Eliminación (medio, n={grande}): ListaSimple {es:.6f}s vs ListaDoble "
            f"{ed:.6f}s (x{ed / es:.2f}). Ambas deben recorrer hasta el elemento, así "
            f"que son O(n); la doble solo gana si ya se tiene la referencia al nodo, y "
            f"a cambio guarda un puntero extra por nodo.")

    colas = []
    for nombre in ("ColaSimple", "ColaCircular", "ColaPrioridad"):
        te, td = _t(filas, f"{nombre}: enqueue", ops_cola), _t(filas, f"{nombre}: dequeue", ops_cola)
        if te and td:
            colas.append((2 * ops_cola / (te + td), nombre))
    if colas:
        colas.sort(reverse=True)
        insights.append(
            "Throughput de colas (enqueue+dequeue): " +
            ", ".join(f"{n} {ops:,.0f} ops/s" for ops, n in colas) +
            ". Todas son O(1) por operación; la de prioridad paga el recorrido de niveles.")
    return insights


def imprimir_tabla(filas):
    ancho = max(len(f[0]) for f in filas)
    print(f"{'Escenario':<{ancho}} | {'n':>7} | {'promedio (s)':>13}")
    print("-" * (ancho + 26))
    anterior = None
    for escenario, n, t in filas:
        grupo = escenario.split()[0]
        if anterior and grupo != anterior:
            print("-" * (ancho + 26))
        anterior = grupo
        print(f"{escenario:<{ancho}} | {n:>7} | {t:>13.6f}")


def run_benchmarks():
    print("\n" + "=" * 70)
    print(f"BENCHMARKS (promedio de {REPETICIONES} ejecuciones, time.perf_counter)")
    print("=" * 70)
    print("Midiendo... (puede tardar unos segundos)")
    filas = ejecutar_benchmarks()
    imprimir_tabla(filas)
    print("\nInsights:")
    for i, texto in enumerate(generar_insights(filas), 1):
        print(f" {i}) {texto}")
    print("=" * 70)
    return filas


if __name__ == "__main__":
    run_benchmarks()
