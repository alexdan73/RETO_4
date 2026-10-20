"""Pruebas unitarias para Stack (Pila LIFO).

Métodos asumidos: push, pop, peek, is_empty, size.
Si tu implementación usa otros nombres (p. ej. `top` en lugar de `peek`),
ajusta solo las llamadas correspondientes.
"""
"""Pruebas unitarias para Stack (Pila LIFO)."""
import unittest

try:
    from . import _bootstrap          # noqa: F401
except ImportError:
    import _bootstrap                 # noqa: F401

from stack import Stack



class TestStack(unittest.TestCase):

    def setUp(self):
        self._stack = Stack()

    def test_nueva_esta_vacia(self):
        self.assertTrue(self._stack.is_empty())
        self.assertEqual(self._stack.size(), 0)

    def test_push_pop_lifo(self):
        self._stack.push(1)
        self._stack.push(2)
        self._stack.push(3)
        self.assertEqual(self._stack.pop(), 3)
        self.assertEqual(self._stack.pop(), 2)
        self.assertEqual(self._stack.pop(), 1)
        self.assertTrue(self._stack.is_empty())

    def test_peek_no_elimina(self):
        self._stack.push("a")
        self._stack.push("b")
        self.assertEqual(self._stack.peek(), "b")
        self.assertEqual(self._stack.size(), 2)   # peek NO debe eliminar
        self.assertEqual(self._stack.pop(), "b")

    def test_size(self):
        self.assertEqual(self._stack.size(), 0)
        self._stack.push(10)
        self._stack.push(20)
        self.assertEqual(self._stack.size(), 2)
        self._stack.pop()
        self.assertEqual(self._stack.size(), 1)

    def test_underflow_pop(self):
        """pop en _stack vacía debe lanzar IndexError.

        Si tu implementación devuelve None en lugar de lanzar excepción,
        reemplaza assertRaises(IndexError) por self.assertIsNone(...).
        """
        with self.assertRaises(IndexError):
            self._stack.pop()

    def test_underflow_peek(self):
        with self.assertRaises(IndexError):
            self._stack.peek()


if __name__ == '__main__':
    unittest.main()