"""Lista doblemente enlazada con inserción ordenada por clave."""
from double_node import DoubleNode


class DoubleList:
    def __init__(self):
        self.head = None
        self._queue = None      # puntero al último nodo (tail)
        self._size = 0

    def insert_sort(self, value, key):
        new_node = DoubleNode(value)
        new_key = key(value)

        if self.head is None:
            self.head = new_node
            self._queue = new_node
            self._size += 1
            return

        current = self.head
        while current and key(current.value) < new_key:
            current = current.next

        if current is None:                     # insertar al final
            new_node.previous = self._queue
            self._queue.next = new_node
            self._queue = new_node
        elif current == self.head:              # insertar al inicio
            new_node.next = self.head
            self.head.previous = new_node
            self.head = new_node
        else:                                   # insertar en medio
            previous = current.previous
            new_node.previous = previous
            new_node.next = current
            previous.next = new_node
            current.previous = new_node
        self._size += 1

    def search(self, condition):
        current = self.head
        while current:
            if condition(current.value):
                return current.value
            current = current.next
        return None

    def delete(self, condition):
        current = self.head
        while current:
            if condition(current.value):
                if current.previous:
                    current.previous.next = current.next
                else:
                    self.head = current.next
                if current.next:
                    current.next.previous = current.previous
                else:
                    self._queue = current.previous
                self._size -= 1
                return current.value
            current = current.next          # FIX: dentro del while
        return None

    def loop_forward(self):
        res, current = [], self.head
        while current:
            res.append(current.value)
            current = current.next
        return res

    def loop_backward(self):
        res, current = [], self._queue     # FIX: era []. self._queue
        while current:
            res.append(current.value)
            current = current.previous
        return res

    def is_empty(self):
        return self.head is None

    def size(self):
        return self._size

    def __len__(self):
        return self._size