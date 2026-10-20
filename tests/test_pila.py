"""Pruebas unitarias para Pila (LIFO)."""
import unittest

try:
    from . import _bootstrap  # noqa: F401  (python -m unittest tests.test_xxx)
except ImportError:
    import _bootstrap  # noqa: F401  (discover -s tests / ejecución directa)
from pila import Pila


class TestPila(unittest.TestCase):

    def setUp(self):
        self.pila = Pila()

    def test_nueva_esta_vacia(self):
        self.assertTrue(self.pila.is_empty())
        self.assertEqual(self.pila.size(), 0)

    def test_push_pop_lifo(self):
        for v in (1, 2, 3):
            self.pila.push(v)
        self.assertEqual([self.pila.pop() for _ in range(3)], [3, 2, 1])
        self.assertTrue(self.pila.is_empty())

    def test_peek_no_elimina(self):
        self.pila.push("a")
        self.pila.push("b")
        self.assertEqual(self.pila.peek(), "b")
        self.assertEqual(self.pila.size(), 2)
        self.assertEqual(self.pila.pop(), "b")

    def test_size(self):
        self.pila.push(10)
        self.pila.push(20)
        self.assertEqual(self.pila.size(), 2)
        self.pila.pop()
        self.assertEqual(self.pila.size(), 1)
        self.assertEqual(len(self.pila), 1)

    def test_underflow_pop(self):
        with self.assertRaises(IndexError):
            self.pila.pop()

    def test_underflow_peek(self):
        with self.assertRaises(IndexError):
            self.pila.peek()

    def test_reutilizable_tras_vaciarse(self):
        self.pila.push(1)
        self.pila.pop()
        self.pila.push(2)
        self.assertEqual(self.pila.peek(), 2)
        self.assertEqual(self.pila.size(), 1)

    def test_a_lista_tope_primero(self):
        for v in (1, 2, 3):
            self.pila.push(v)
        self.assertEqual(self.pila.a_lista(), [3, 2, 1])


if __name__ == '__main__':
    unittest.main()
