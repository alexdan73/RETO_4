from simple_queue import SimpleQueue

class PriorityQueue:
    LEVELS = 5
    def __init__(self):
        self._queue = {i: SimpleQueue() for i in range(1, self.LEVELS +1)}
        self._size = 0

    def _normalize(self, p):
        try:
            p = int(p)
        except (TypeError, ValueError):
            p = 1
        return max(1, min(self.LEVELS, p))

    def enqueue(self, student, priority):
        p = self._normalize(priority)
        student['p'] = p
        self._queues[p].enqueue(student)
        self._size += 1

    def dequeue(self):
        for p in range(self.LEVELS, 0, -1):
            if not self._queues[p].is_empty():
                self._size -= 1
                return self._queues[p].dequeue()
        raise IndexError("Cola de Prioridad vacía")
    
    def front(self):
        for p in range(self.LEVELS, 0, -1):
            if not self._queues[p].is_empty():
                return self._queues[p].front()
        raise IndexError("Cola de prioridad vacía")

    def front_insert(self, student, priority):
        p = self._normalize(priority)
        student['p'] = p
        self._queues[p].front_insert(student)
        self._size += 1

    def is_empty(self):
        return self._size == 0

    def size(self):
        return self._size

    def a_list(self):
        "Devuelve en orden de antención (5→1) para visualización."
        result = []
        for p in range(self.LEVELS, 0, -1):
            result.extend(self._queues[p].a_list())
        return result

    def __len__(self):
        return self._size
    
