"""Lista doblemente enlazada con inserción ordenada por clave."""
from nodo_doble import NodoDoble


class ListaDoble:
    def __init__(self):
        self.cabeza = None
        self.cola = None
        self._tamano = 0

    def insertar_final(self, valor):
        """Inserción O(1) al final, sin ordenar (útil para cargas masivas/benchmarks)."""
        nuevo = NodoDoble(valor, anterior=self.cola)
        if self.cola is None:
            self.cabeza = nuevo
        else:
            self.cola.siguiente = nuevo
        self.cola = nuevo
        self._tamano += 1

    def insertar_ordenado(self, valor, clave):
        """Inserta manteniendo el orden ascendente de clave(valor).
        Con claves iguales, el nuevo queda después de los existentes."""
        nueva = clave(valor)
        # Atajo: si va al final (caso típico ascendente) es O(1)
        if self.cola is None or clave(self.cola.valor) <= nueva:
            self.insertar_final(valor)
            return
        actual = self.cabeza
        while actual and clave(actual.valor) <= nueva:
            actual = actual.siguiente
        # aquí actual no es None (porque la cola es > nueva)
        nuevo = NodoDoble(valor, anterior=actual.anterior, siguiente=actual)
        if actual.anterior is None:
            self.cabeza = nuevo
        else:
            actual.anterior.siguiente = nuevo
        actual.anterior = nuevo
        self._tamano += 1

    def buscar(self, condicion):
        actual = self.cabeza
        while actual:
            if condicion(actual.valor):
                return actual.valor
            actual = actual.siguiente
        return None

    def eliminar(self, condicion):
        actual = self.cabeza
        while actual:
            if condicion(actual.valor):
                if actual.anterior:
                    actual.anterior.siguiente = actual.siguiente
                else:
                    self.cabeza = actual.siguiente
                if actual.siguiente:
                    actual.siguiente.anterior = actual.anterior
                else:
                    self.cola = actual.anterior
                self._tamano -= 1
                return actual.valor
            actual = actual.siguiente
        return None

    def recorrer_adelante(self):
        res, actual = [], self.cabeza
        while actual:
            res.append(actual.valor)
            actual = actual.siguiente
        return res

    def recorrer_atras(self):
        res, actual = [], self.cola
        while actual:
            res.append(actual.valor)
            actual = actual.anterior
        return res

    def mostrar(self, formato=str):
        txt = " <-> ".join(formato(v) for v in self.recorrer_adelante()) or "(vacía)"
        print(f"Lista doble: {txt}")

    def is_empty(self):
        return self.cabeza is None

    def size(self):
        return self._tamano

    def __len__(self):
        return self._tamano
