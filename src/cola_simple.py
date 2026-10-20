"""Cola simple (FIFO) con punteros a frente y final."""
from nodo_simple import NodoSimple


class ColaSimple:
    def __init__(self):
        self.frente = None
        self.final = None
        self._tamano = 0

    def enqueue(self, valor):
        nuevo = NodoSimple(valor)
        if self.final is None:
            self.frente = nuevo
        else:
            self.final.siguiente = nuevo
        self.final = nuevo
        self._tamano += 1

    def dequeue(self):
        if self.is_empty():
            raise IndexError("Cola vacía: no se puede hacer dequeue")
        valor = self.frente.valor
        self.frente = self.frente.siguiente
        if self.frente is None:
            self.final = None
        self._tamano -= 1
        return valor

    def front(self):
        if self.is_empty():
            raise IndexError("Cola vacía: no se puede consultar front")
        return self.frente.valor

    def insertar_al_frente(self, valor):
        """Reinserta al frente (lo usa DESHACER)."""
        nuevo = NodoSimple(valor, self.frente)
        self.frente = nuevo
        if self.final is None:
            self.final = nuevo
        self._tamano += 1

    def eliminar(self, condicion):
        """Elimina el primer elemento que cumpla la condición. Retorna valor o None."""
        previo, actual = None, self.frente
        while actual:
            if condicion(actual.valor):
                if previo is None:
                    self.frente = actual.siguiente
                else:
                    previo.siguiente = actual.siguiente
                if actual is self.final:
                    self.final = previo
                self._tamano -= 1
                return actual.valor
            previo, actual = actual, actual.siguiente
        return None

    def is_empty(self):
        return self.frente is None

    def size(self):
        return self._tamano

    def a_lista(self):
        res, actual = [], self.frente
        while actual:
            res.append(actual.valor)
            actual = actual.siguiente
        return res

    def mostrar(self, formato=str):
        txt = " -> ".join(formato(v) for v in self.a_lista()) or "(vacía)"
        print(f"Cola simple: {txt}")

    def __len__(self):
        return self._tamano
