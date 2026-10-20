"""Cola circular (FIFO) con un único puntero al último nodo."""
from nodo_simple import NodoSimple


class ColaCircular:
    def __init__(self):
        self.ultimo = None          # ultimo.siguiente es el frente
        self._tamano = 0

    def enqueue(self, valor):
        nuevo = NodoSimple(valor)
        if self.ultimo is None:
            nuevo.siguiente = nuevo
        else:
            nuevo.siguiente = self.ultimo.siguiente
            self.ultimo.siguiente = nuevo
        self.ultimo = nuevo
        self._tamano += 1

    def dequeue(self):
        if self.is_empty():
            raise IndexError("Cola circular vacía: no se puede hacer dequeue")
        frente = self.ultimo.siguiente
        if frente is self.ultimo:
            self.ultimo = None
        else:
            self.ultimo.siguiente = frente.siguiente
        self._tamano -= 1
        return frente.valor

    def front(self):
        if self.is_empty():
            raise IndexError("Cola circular vacía: no se puede consultar front")
        return self.ultimo.siguiente.valor

    def insertar_al_frente(self, valor):
        """Reinserta al frente (lo usa DESHACER de REASIGNAR)."""
        nuevo = NodoSimple(valor)
        if self.ultimo is None:
            nuevo.siguiente = nuevo
            self.ultimo = nuevo
        else:
            nuevo.siguiente = self.ultimo.siguiente
            self.ultimo.siguiente = nuevo
        self._tamano += 1

    def quitar_ultimo(self):
        """Elimina el último encolado (lo usa DESHACER de ENVIAR_A_ESPERA)."""
        if self.is_empty():
            raise IndexError("Cola circular vacía: no se puede quitar el último")
        valor = self.ultimo.valor
        if self._tamano == 1:
            self.ultimo = None
        else:
            penultimo = self.ultimo.siguiente
            while penultimo.siguiente is not self.ultimo:
                penultimo = penultimo.siguiente
            penultimo.siguiente = self.ultimo.siguiente
            self.ultimo = penultimo
        self._tamano -= 1
        return valor

    def eliminar(self, condicion):
        """Elimina el primer elemento que cumpla la condición. Retorna valor o None."""
        if self.is_empty():
            return None
        previo, actual = self.ultimo, self.ultimo.siguiente
        for _ in range(self._tamano):
            if condicion(actual.valor):
                if self._tamano == 1:
                    self.ultimo = None
                else:
                    previo.siguiente = actual.siguiente
                    if actual is self.ultimo:
                        self.ultimo = previo
                self._tamano -= 1
                return actual.valor
            previo, actual = actual, actual.siguiente
        return None

    def is_empty(self):
        return self.ultimo is None

    def size(self):
        return self._tamano

    def a_lista(self):
        if self.ultimo is None:
            return []
        res, actual = [], self.ultimo.siguiente
        for _ in range(self._tamano):
            res.append(actual.valor)
            actual = actual.siguiente
        return res

    def mostrar(self, formato=str):
        txt = " -> ".join(formato(v) for v in self.a_lista())
        print(f"Cola circular: {txt + ' -> (vuelve al frente)' if txt else '(vacía)'}")

    def __len__(self):
        return self._tamano
