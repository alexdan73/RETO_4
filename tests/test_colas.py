"""Pruebas unitarias para ColaSimple, ColaCircular y ColaPrioridad."""
import unittest

try:
    from . import _bootstrap  # noqa: F401  (python -m unittest tests.test_xxx)
except ImportError:
    import _bootstrap  # noqa: F401  (discover -s tests / ejecución directa)
from cola_simple import ColaSimple
from cola_circular import ColaCircular
from cola_prioridad import ColaPrioridad


class TestColaSimple(unittest.TestCase):

    def setUp(self):
        self.cola = ColaSimple()

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

    def test_insertar_al_frente(self):
        self.cola.enqueue(1)
        self.cola.enqueue(2)
        self.cola.insertar_al_frente(0)
        self.assertEqual([self.cola.dequeue() for _ in range(3)], [0, 1, 2])

    def test_insertar_al_frente_en_vacia_actualiza_final(self):
        self.cola.insertar_al_frente(1)
        self.cola.enqueue(2)
        self.assertEqual(self.cola.a_lista(), [1, 2])

    def test_reutilizable_tras_vaciarse(self):
        self.cola.enqueue(1)
        self.cola.dequeue()
        self.cola.enqueue(2)
        self.assertEqual(self.cola.a_lista(), [2])

    def test_eliminar_inicio_medio_fin(self):
        for v in (1, 2, 3, 4):
            self.cola.enqueue(v)
        self.assertEqual(self.cola.eliminar(lambda x: x == 1), 1)
        self.assertEqual(self.cola.eliminar(lambda x: x == 3), 3)
        self.assertEqual(self.cola.eliminar(lambda x: x == 4), 4)
        self.cola.enqueue(5)                    # el puntero final debe seguir válido
        self.assertEqual(self.cola.a_lista(), [2, 5])
        self.assertIsNone(self.cola.eliminar(lambda x: x == 99))

    def test_underflow(self):
        with self.assertRaises(IndexError):
            self.cola.dequeue()
        with self.assertRaises(IndexError):
            self.cola.front()


class TestColaCircular(unittest.TestCase):

    def setUp(self):
        self.cola = ColaCircular()

    def test_nueva_esta_vacia(self):
        self.assertTrue(self.cola.is_empty())
        self.assertEqual(self.cola.size(), 0)

    def test_fifo(self):
        for i in range(4):
            self.cola.enqueue(i)
        self.assertEqual([self.cola.dequeue() for _ in range(4)], [0, 1, 2, 3])
        self.assertTrue(self.cola.is_empty())

    # DESPUÉS
    def test_es_circular(self):
        for i in range(3):
            self.cola.enqueue(i)
        self.assertEqual(self.cola.ultimo.siguiente.valor, 0)   # el último apunta al frente

    def test_reutilizable(self):
        self.cola.enqueue(1)
        self.cola.dequeue()
        self.cola.enqueue(2)
        self.cola.enqueue(3)
        self.assertEqual([self.cola.dequeue(), self.cola.dequeue()], [2, 3])

    def test_front_no_elimina(self):
        self.cola.enqueue(7)
        self.assertEqual(self.cola.front(), 7)
        self.assertEqual(self.cola.size(), 1)

    def test_quitar_ultimo(self):
        for v in (10, 20, 30):
            self.cola.enqueue(v)
        self.assertEqual(self.cola.quitar_ultimo(), 30)
        self.assertEqual(self.cola.a_lista(), [10, 20])
        self.cola.enqueue(40)
        self.assertEqual(self.cola.a_lista(), [10, 20, 40])

    def test_quitar_ultimo_unico(self):
        self.cola.enqueue(99)
        self.assertEqual(self.cola.quitar_ultimo(), 99)
        self.assertTrue(self.cola.is_empty())

    def test_insertar_al_frente(self):
        for v in (2, 3):
            self.cola.enqueue(v)
        self.cola.insertar_al_frente(1)
        self.assertEqual([self.cola.dequeue() for _ in range(3)], [1, 2, 3])

    def test_insertar_al_frente_en_vacia(self):
        self.cola.insertar_al_frente(1)
        self.cola.enqueue(2)
        self.assertEqual(self.cola.a_lista(), [1, 2])

    def test_eliminar(self):
        for v in (1, 2, 3, 4):
            self.cola.enqueue(v)
        self.assertEqual(self.cola.eliminar(lambda x: x == 1), 1)   # frente
        self.assertEqual(self.cola.eliminar(lambda x: x == 4), 4)   # último
        self.assertEqual(self.cola.a_lista(), [2, 3])
        self.cola.enqueue(5)
        self.assertEqual(self.cola.a_lista(), [2, 3, 5])
        self.assertIsNone(self.cola.eliminar(lambda x: x == 99))
        self.cola.eliminar(lambda x: x == 2)
        self.cola.eliminar(lambda x: x == 3)
        self.cola.eliminar(lambda x: x == 5)
        self.assertTrue(self.cola.is_empty())

    def test_underflow(self):
        for metodo in (self.cola.dequeue, self.cola.front, self.cola.quitar_ultimo):
            with self.assertRaises(IndexError):
                metodo()


class TestColaPrioridad(unittest.TestCase):

    def setUp(self):
        self.cola = ColaPrioridad()

    def test_nueva_esta_vacia(self):
        self.assertTrue(self.cola.is_empty())
        self.assertEqual(self.cola.size(), 0)

    def test_prioridad_mas_alta_primero(self):
        self.cola.enqueue({'id': 1}, 1)
        self.cola.enqueue({'id': 2}, 5)
        self.cola.enqueue({'id': 3}, 3)
        self.assertEqual([self.cola.dequeue()['id'] for _ in range(3)], [2, 3, 1])

    def test_multiples_criticos_respetan_fifo(self):
        for i in (10, 11, 12):
            self.cola.enqueue({'id': i}, 5)
        self.assertEqual([self.cola.dequeue()['id'] for _ in range(3)], [10, 11, 12])

    def test_front_prioridad_maxima(self):
        self.cola.enqueue({'id': 1}, 2)
        self.cola.enqueue({'id': 2}, 4)
        self.assertEqual(self.cola.front()['id'], 2)
        self.assertEqual(self.cola.size(), 2)

    def test_prioridad_fuera_de_rango_se_normaliza(self):
        self.cola.enqueue({'id': 1}, 99)
        self.assertEqual(self.cola.front()['p'], 5)

    def test_insertar_al_frente(self):
        self.cola.enqueue({'id': 5}, 3)
        self.cola.insertar_al_frente({'id': 9}, 3)
        self.assertEqual(self.cola.dequeue()['id'], 9)

    def test_eliminar(self):
        self.cola.enqueue({'id': 1}, 2)
        self.cola.enqueue({'id': 2}, 5)
        self.assertEqual(self.cola.eliminar(lambda e: e['id'] == 2)['id'], 2)
        self.assertEqual(self.cola.size(), 1)
        self.assertIsNone(self.cola.eliminar(lambda e: e['id'] == 99))

    def test_underflow(self):
        with self.assertRaises(IndexError):
            self.cola.dequeue()
        with self.assertRaises(IndexError):
            self.cola.front()


if __name__ == '__main__':
    unittest.main()
