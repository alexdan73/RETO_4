"""Nodo para listas doblemente enlazadas."""


class NodoDoble:
    def __init__(self, valor, anterior=None, siguiente=None):
        self.valor = valor
        self.anterior = anterior
        self.siguiente = siguiente
