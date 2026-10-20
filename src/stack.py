from simple_node import SimpleNode

class Stack:
    def __init__(self):
        self.head = None
        self._size = 0

    def push(self, value):
        self.head = SimpleNode(value, self.head)
        self._size +=1

    def pop(self):
        if self.is_empty():
            raise IndexError("Pila vacía: no se puede hacer pop")
        value = self.head.value
        self.head = self.head.next
        self._size -= 1
        return value

    def peek(self):
        if self.is_empty():
            raise IndexError("Pila vacía: no se puede hacer peek")

        return self.head.value

    def is_empty(self):
        return self.head is None

    def size(self):
        return self._size

    def __len__(self):
        return self._size


    