"""Pila (LIFO) sobre nodos enlazados."""
from nodo_simple import NodoSimple


class Pila:
    def __init__(self):
        self.tope = None
        self._tamano = 0

    def push(self, valor):
        self.tope = NodoSimple(valor, self.tope)
        self._tamano += 1

    def pop(self):
        if self.is_empty():
            raise IndexError("Pila vacía: no se puede hacer pop")
        valor = self.tope.valor
        self.tope = self.tope.siguiente
        self._tamano -= 1
        return valor

    def peek(self):
        if self.is_empty():
            raise IndexError("Pila vacía: no se puede hacer peek")
        return self.tope.valor

    def is_empty(self):
        return self.tope is None

    def size(self):
        return self._tamano

    def a_lista(self):
        """De tope a fondo (solo para visualización/pruebas)."""
        res, actual = [], self.tope
        while actual:
            res.append(actual.valor)
            actual = actual.siguiente
        return res

    def mostrar(self, formato=str):
        txt = " -> ".join(formato(v) for v in self.a_lista()) or "(vacía)"
        print(f"Pila (tope primero): {txt}")

    def __len__(self):
        return self._tamano
