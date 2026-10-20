"""Lista simplemente enlazada con puntero al final (inserción O(1))."""
from nodo_simple import NodoSimple


class ListaSimple:
    def __init__(self):
        self.cabeza = None
        self.cola = None
        self._tamano = 0

    def insertar(self, valor):
        nuevo = NodoSimple(valor)
        if self.cabeza is None:
            self.cabeza = nuevo
        else:
            self.cola.siguiente = nuevo
        self.cola = nuevo
        self._tamano += 1

    def buscar(self, condicion):
        """Retorna (indice, valor) o (-1, None)."""
        actual, idx = self.cabeza, 0
        while actual:
            if condicion(actual.valor):
                return idx, actual.valor
            actual = actual.siguiente
            idx += 1
        return -1, None

    def eliminar(self, condicion):
        """Elimina el primer nodo que cumpla la condición. Retorna valor o None."""
        previo, actual = None, self.cabeza
        while actual:
            if condicion(actual.valor):
                if previo is None:
                    self.cabeza = actual.siguiente
                else:
                    previo.siguiente = actual.siguiente
                if actual is self.cola:
                    self.cola = previo
                self._tamano -= 1
                return actual.valor
            previo, actual = actual, actual.siguiente
        return None

    def recorrer(self):
        res, actual = [], self.cabeza
        while actual:
            res.append(actual.valor)
            actual = actual.siguiente
        return res

    def mostrar(self, formato=str):
        txt = " -> ".join(formato(v) for v in self.recorrer()) or "(vacía)"
        print(f"Lista: {txt}")

    def is_empty(self):
        return self.cabeza is None

    def size(self):
        return self._tamano

    def __len__(self):
        return self._tamano
