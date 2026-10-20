class SimpleNode:
    "Nodo para estructuras enlazadas simple (listas, pilas, colas)"
    
    def __init__(self, value, next=None):
        self.value = value
        self.next = next