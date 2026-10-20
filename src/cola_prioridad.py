"""Cola de prioridad: 5 = crítico (sale primero) ... 1 = más bajo.

Un nivel = una ColaSimple, así que dentro de un mismo nivel se respeta FIFO.
Los elementos deben ser diccionarios: se les añade la clave 'p'.
"""
from cola_simple import ColaSimple


class ColaPrioridad:
    NIVELES = 5

    def __init__(self):
        self._niveles = {p: ColaSimple() for p in range(1, self.NIVELES + 1)}
        self._tamano = 0

    def _normalizar(self, p):
        try:
            p = int(p)
        except (TypeError, ValueError):
            p = 1
        return max(1, min(self.NIVELES, p))

    def enqueue(self, valor, prioridad):
        p = self._normalizar(prioridad)
        valor['p'] = p
        self._niveles[p].enqueue(valor)
        self._tamano += 1

    def dequeue(self):
        for p in range(self.NIVELES, 0, -1):
            if not self._niveles[p].is_empty():
                self._tamano -= 1
                return self._niveles[p].dequeue()
        raise IndexError("Cola de prioridad vacía: no se puede hacer dequeue")

    def front(self):
        for p in range(self.NIVELES, 0, -1):
            if not self._niveles[p].is_empty():
                return self._niveles[p].front()
        raise IndexError("Cola de prioridad vacía: no se puede consultar front")

    def insertar_al_frente(self, valor, prioridad):
        """Reinserta al frente de su nivel (lo usa DESHACER)."""
        p = self._normalizar(prioridad)
        valor['p'] = p
        self._niveles[p].insertar_al_frente(valor)
        self._tamano += 1

    def eliminar(self, condicion):
        for p in range(self.NIVELES, 0, -1):
            valor = self._niveles[p].eliminar(condicion)
            if valor is not None:
                self._tamano -= 1
                return valor
        return None

    def is_empty(self):
        return self._tamano == 0

    def size(self):
        return self._tamano

    def a_lista(self):
        """En orden de atención (5 -> 1)."""
        res = []
        for p in range(self.NIVELES, 0, -1):
            res.extend(self._niveles[p].a_lista())
        return res

    def mostrar(self, formato=str):
        txt = " -> ".join(formato(v) for v in self.a_lista()) or "(vacía)"
        print(f"Cola de prioridad: {txt}")

    def __len__(self):
        return self._tamano
