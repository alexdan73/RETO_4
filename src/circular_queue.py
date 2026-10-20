from simple_node import SimpleNode

class CircularQueue:
    def __init__(self):
        self._queue = None
        self._size = 0

    def enqueue(self, value):
        new_node = SimpleNode(value)
        if self._queue is None:
            new_node.next = new_node
            self._queue = new_node
        else:
            new_node.next = self._queue.next
            self._queue.next = new_node
            self._queue = new_node
        self._size += 1

    def is_empty(self):
        return self._queue is None

    def dequeue(self):
        if self.is_empty():
            raise IndexError("Cola circular vacía: no se puede dequeue")
        head = self._queue.next
        value = head.value
        if self._queue == head:
            self._queue = None
        else:
            self._queue.next = head.next
        self._size -= 1
        return value

    def front(self):
        if self.is_empty():
            raise IndexError("Cola circular vacía")
        return self._queue.next.value

    def front_insert(self, value):
        new_node = SimpleNode(value)
        if self._queue is None:
            new_node.next = new_node
            self._queue = new_node
        else:
            new_node.next = self._queue.next
            self._queue.next = new_node
        self._size += 1

    def last_remove(self):
        """Elimina el último enqueued. Usado por deshacer ENVIAR_A_ESPERA."""
        if self.is_empty():
            raise IndexError("Cola circular vacía")

        # FIX: caso de un solo nodo
        if self._size == 1:
            value = self._queue.value          # era self._queue.next
            self._queue = None
            self._size = 0
            return value

        # FIX: el loop debe comparar penultimate.next con _queue
        penultimate = self._queue.next
        while penultimate.next != self._queue:   # era penultimate != self._queue
            penultimate = penultimate.next

        value = self._queue.value
        penultimate.next = self._queue.next
        self._queue = penultimate
        self._size -= 1
        return value

    def size(self):
        return self._size

    def a_list(self):
        if self._queue is None:
            return []
        result = []
        current = self._queue.next
        for _ in range(self._size):
            result.append(current.value)
            current = current.next
        return result

    def __len__(self):
        return self._size