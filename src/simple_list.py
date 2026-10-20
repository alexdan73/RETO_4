"""Lista simple con puntero tail para inserción O(1) al final."""
from simple_node import SimpleNode
class SimpleList:
    def __init__(self):
        self.head = None
        self._queue = None
        self._size = 0

    def insert(self, value):
        new_node = SimpleNode(value)
        if self.head is None:
            self.head = new_node
            self._queue = new_node
        else:
            self._queue.next = new_node
            self._queue = new_node
        self._size += 1

    def search(self, condition):
        """Retorna (indice, valor) o (-1, None)"""
        current = self.head
        idx = 0
        while current:
            if condition(current.value):
                return idx, current.value
            current = current.next
            idx += 1
        return -1, None

    def delete(self, condition):
        """Elimina el primer nodo que cumpla la condición. Retorna valor o None"""
        current = self.head
        previous = None
        while current:
            if condition(current.value):
                if previous is None:
                    self.head = current.next
                else:
                    previous.next = current.next
                if current == self._queue:
                    self._queue = previous
                self._size -= 1
                return current.value
            previous = current
            current = current.next
        return None

    def a_list(self):
        result = []
        current = self.head
        while current:
            result.append(current.value)
            current = current.next
        return result

    def is_empty(self):
        return self.head is None

    def size(self):
        return self._size

    def __len__(self):
        return self._size


    

