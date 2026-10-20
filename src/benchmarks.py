import time

from simple_list import SimpleList
from double_list import DoubleList
from simple_queue import SimpleQueue
from circular_queue import CircularQueue
from priority_queue import PriorityQueue

def _measure(fn, repetitions=5):
    times = []
    for _ in range(repetitions):
        t_0 = time.perf_counter()
        fn()
        times.append(time.perf_counter - t_0)
    return sum(times)/len(times)

def run_benchmarks():
    print("\n" + "=" * 60)
    print("BENCHMARKS (promedio de 5 ejecuciones)")
    print("=" * 60)

    # 1) Inserción ListaSimple
    print("\n[1] Inserción en ListaSimple (al final, con tail)")
    print(f"{'n':>8} | {'tiempo (s)':>15}")
    print("-" * 28)
    for n in (1000, 5000, 10000):
        def ins(n=n):
            _list = SimpleList()
            for i in range(n):
                _list.insert(i)
        print(f"{n:>8} | {_measure(ins):>15.6f}")

    # 2) Búsqueda en ListaSimple n=5000
    print("\n[2] Búsqueda en ListaSimple (n=5000)")
    _list = SimpleList()
    for i in range(5000):
        _list.insert(i)
    for label, target in [("inicio", 0), ("medio", 2500), ("fin", 4999)]:
        def search(obj = target):
            _list.search(lambda v: v == obj)
        print(f"  {label:>6}: {_measure(search):.8f} s")

     # 3) Eliminación simple vs doble
    print("\n[3] Eliminación en ListaSimple vs ListaDoble (n=2000)")
    def delete_simple():
        _list = SimpleList()
        for i in range(2000):
            _list.insert({'v': i})
        _list.delete(lambda e: e['v'] == 1000)

    def delete_double():
        _listd = DoubleList()
        for i in range(2000):
            _listd.insert_sort({'v': i}, lambda e: e['v'])
        _listd.delete(lambda e: e['v'] == 1000)
    print(f"  ListaSimple: {_measure(delete_simple):.6f} s")
    print(f"  ListaDoble:  {_measure(delete_double):.6f} s")

      # 4) Throughput colas (10k enq + 10k deq)
    print("\n[4] Throughput enqueue+dequeue (10k cada uno)")

    def th_simple():
        simp_que = SimpleQueue()
        for i in range(10000): simp_que.enqueue(i)
        for _ in range(10000): simp_que.dequeue()

    def th_circular():
        cirp_que = CircularQueue()
        for i in range(10000): cirp_que.enqueue(i)
        for _ in range(10000): cirp_que.dequeue()

    def th_priority():
        priori_que = PriorityQueue()
        for i in range(10000): priori_que.enqueue({'v': i}, (i % 5) + 1)
        for _ in range(10000): priori_que.dequeue()

    for label, fn in [("ColaSimple", th_simple),
                        ("ColaCircular", th_circular),
                        ("ColaPrioridad", th_priority)]:
        t = _measure(fn)
        print(f" {label:>14}: {t:.6f} s ({20000/t:,.0f} ops/s)")

    print("\nInsights:")
    print(" 1) La inserción al final es O(1) por el puntero tail.")
    print(" 2) La búsqueda domina el costo (O(n)); mitad y fin casi iguales.")
    print(" 3) La lista doble agiliza eliminación pero duplica memoria.")
    print("=" * 60)

    if __name__ == "__main__":
        run_benchmarks()