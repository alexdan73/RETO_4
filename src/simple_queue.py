from simple_node import SimpleNode

class SimpleQueue:
    def __init__(self):
        self.head = None
        self._queue = None
        self._size = 0

    def enqueue(self, value):
        new_node = SimpleNode(value)
        if self._queue is None:
            self.head = new_node
            self._queue = new_node          # FIX: era self.las
        else:
            self._queue.next = new_node
            self._queue = new_node
        self._size += 1

    def is_empty(self):
        return self.head is None

    def dequeue(self):
        if self.is_empty():
            raise IndexError("Cola vacía: no se puede hacer dequeue")
        value = self.head.value
        self.head = self.head.next
        if self.head is None:
            self._queue = None
        self._size -= 1
        return value

    def front(self):
        if self.is_empty():
            raise IndexError("Cola vacía: no se puede consultar front")  # FIX
        return self.head.value

    def front_insert(self, value):
        """Reinsertar al frente (usado por deshacer)."""           # FIX: docstring
        new_node = SimpleNode(value, self.head)
        self.head = new_node
        if self._queue is None:
            self._queue = new_node
        self._size += 1

    def size(self):
        return self._size

    def a_list(self):
        result = []
        current = self.head
        while current:
            result.append(current.value)
            current = current.next
        return result

    def __len__(self):
        return self._size