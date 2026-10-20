"""Nodo para estructuras enlazadas simples (listas, pilas, colas)."""


class NodoSimple:
    def __init__(self, valor, siguiente=None):
        self.valor = valor
        self.siguiente = siguiente
