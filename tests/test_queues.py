"""Pruebas unitarias para SimpleQueue, CircularQueue y PriorityQueue.

Métodos asumidos:
  - SimpleQueue:   enqueue, dequeue, front, is_empty, size, a_list, front_insert
  - CircularQueue: enqueue, dequeue, front, is_empty, size, a_list,
                   front_insert, last_remove
  - PriorityQueue: enqueue, dequeue, front, is_empty, size, a_list, front_insert
    (prioridad 5 = más crítico, 1 = menos)
"""

"""Pruebas unitarias para SimpleQueue, CircularQueue y PriorityQueue."""
import unittest

try:
    from . import _bootstrap          # noqa: F401
except ImportError:
    import _bootstrap                 # noqa: F401

from simple_queue import SimpleQueue
from circular_queue import CircularQueue
from priority_queue import PriorityQueue


# ======================================================================
# SimpleQueue
# ======================================================================
class TestSimpleQueue(unittest.TestCase):

    def setUp(self):
        self.cola = SimpleQueue()

    def test_nueva_esta_vacia(self):
        self.assertTrue(self.cola.is_empty())
        self.assertEqual(self.cola.size(), 0)

    def test_fifo(self):
        for i in range(3):
            self.cola.enqueue(i)
        self.assertEqual([self.cola.dequeue() for _ in range(3)], [0, 1, 2])
        self.assertTrue(self.cola.is_empty())

    def test_front_no_elimina(self):
        self.cola.enqueue("x")
        self.assertEqual(self.cola.front(), "x")
        self.assertEqual(self.cola.size(), 1)

    def test_front_insert_respeta_orden(self):
        """front_insert debe meter al inicio (usado por undo)."""
        self.cola.enqueue(1)
        self.cola.enqueue(2)
        self.cola.front_insert(0)
        self.assertEqual([self.cola.dequeue() for _ in range(3)], [0, 1, 2])

    def test_a_list(self):
        for v in ('a', 'b', 'c'):
            self.cola.enqueue(v)
        self.assertEqual(self.cola.a_list(), ['a', 'b', 'c'])

    def test_underflow_dequeue(self):
        with self.assertRaises(IndexError):
            self.cola.dequeue()

    def test_underflow_front(self):
        with self.assertRaises(IndexError):
            self.cola.front()


# ======================================================================
# CircularQueue
# ======================================================================
class TestCircularQueue(unittest.TestCase):

    def setUp(self):
        self.cola = CircularQueue()

    def test_nueva_esta_vacia(self):
        self.assertTrue(self.cola.is_empty())
        self.assertEqual(self.cola.size(), 0)

    def test_fifo(self):
        for i in range(4):
            self.cola.enqueue(i)
        self.assertEqual([self.cola.dequeue() for _ in range(4)], [0, 1, 2, 3])

    def test_reutilizable(self):
        """Tras vaciarse parcialmente debe seguir funcionando."""
        self.cola.enqueue(1)
        self.cola.dequeue()
        self.cola.enqueue(2)
        self.cola.enqueue(3)
        self.assertEqual(self.cola.dequeue(), 2)
        self.assertEqual(self.cola.dequeue(), 3)

    def test_last_remove(self):
        """last_remove saca el último (usado por undo ENVIAR_A_ESPERA)."""
        for v in (10, 20, 30):
            self.cola.enqueue(v)
        self.assertEqual(self.cola.last_remove(), 30)
        self.assertEqual(self.cola.a_list(), [10, 20])

    def test_last_remove_unico(self):
        self.cola.enqueue(99)
        self.assertEqual(self.cola.last_remove(), 99)
        self.assertTrue(self.cola.is_empty())

    def test_front_insert(self):
        for v in (2, 3):
            self.cola.enqueue(v)
        self.cola.front_insert(1)
        self.assertEqual([self.cola.dequeue() for _ in range(3)], [1, 2, 3])

    def test_underflow_dequeue(self):
        with self.assertRaises(IndexError):
            self.cola.dequeue()

    def test_underflow_last_remove(self):
        with self.assertRaises(IndexError):
            self.cola.last_remove()


# ======================================================================
# PriorityQueue
# ======================================================================
class TestPriorityQueue(unittest.TestCase):

    def setUp(self):
        self.cola = PriorityQueue()

    def test_nueva_esta_vacia(self):
        self.assertTrue(self.cola.is_empty())
        self.assertEqual(self.cola.size(), 0)

    def test_prioridad_mas_alta_primero(self):
        self.cola.enqueue({'id': 1, 'nombre': 'A'}, 1)
        self.cola.enqueue({'id': 2, 'nombre': 'B'}, 5)
        self.cola.enqueue({'id': 3, 'nombre': 'C'}, 3)
        orden = [self.cola.dequeue()['id'] for _ in range(3)]
        self.assertEqual(orden, [2, 3, 1])   # 5 → 3 → 1

    def test_misma_prioridad_respeta_fifo(self):
        """Empate en prioridad → orden de llegada."""
        self.cola.enqueue({'id': 10}, 5)
        self.cola.enqueue({'id': 11}, 5)
        self.cola.enqueue({'id': 12}, 5)
        orden = [self.cola.dequeue()['id'] for _ in range(3)]
        self.assertEqual(orden, [10, 11, 12])

    def test_front_prioridad_maxima(self):
        self.cola.enqueue({'id': 1}, 2)
        self.cola.enqueue({'id': 2}, 4)
        self.assertEqual(self.cola.front()['id'], 2)

    def test_front_insert(self):
        self.cola.enqueue({'id': 5}, 3)
        self.cola.front_insert({'id': 9, 'p': 3}, 3)
        self.assertEqual(self.cola.dequeue()['id'], 9)

    def test_underflow_dequeue(self):
        with self.assertRaises(IndexError):
            self.cola.dequeue()

    def test_underflow_front(self):
        with self.assertRaises(IndexError):
            self.cola.front()


if __name__ == '__main__':
    unittest.main()