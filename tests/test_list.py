"""Pruebas unitarias para SimpleList y DoubleList.

Métodos asumidos:
  - SimpleList: insert, delete, search, size, a
    * search(cond) → (indice, valor) si encuentra, (-1, None) si no.
      (Así lo usa app.py en _id_system: search(...)[0] >= 0)

  - DoubleList: insert_sort, search, delete, size,
                loop_forward, loop_backward
    * search(cond) → valor (dict) si encuentra, None si no.
      (Así lo usa app.py en add_subject / update_grade)
    * insert_sort(valor, clave) ordena por clave(valor).
"""
"""Pruebas unitarias para SimpleList y DoubleList."""
import unittest

try:
    from . import _bootstrap          # noqa: F401
except ImportError:
    import _bootstrap                 # noqa: F401

from simple_list import SimpleList
from double_list import DoubleList


# ... el resto queda igual ...


# ======================================================================
# SimpleList
# ======================================================================
class TestSimpleList(unittest.TestCase):

    def setUp(self):
        self.lista = SimpleList()

    def test_nueva_esta_vacia(self):
        self.assertTrue(self.lista.is_empty() if hasattr(self.lista, 'is_empty')
                        else self.lista.size() == 0)
        self.assertEqual(self.lista.size(), 0)

    def test_insert_a_list(self):
        for v in (10, 20, 30):
            self.lista.insert(v)
        self.assertEqual(self.lista.a_list(), [10, 20, 30])
        self.assertEqual(self.lista.size(), 3)

    def test_search_existente(self):
        for v in (5, 10, 15):
            self.lista.insert(v)
        idx, valor = self.lista.search(lambda x: x == 10)
        self.assertEqual(idx, 1)
        self.assertEqual(valor, 10)

    def test_search_inexistente(self):
        self.lista.insert(1)
        idx, valor = self.lista.search(lambda x: x == 99)
        self.assertEqual(idx, -1)
        self.assertIsNone(valor)

    def test_delete_inicio(self):
        for v in (1, 2, 3):
            self.lista.insert(v)
        self.assertEqual(self.lista.delete(lambda x: x == 1), 1)
        self.assertEqual(self.lista.a_list(), [2, 3])

    def test_delete_medio(self):
        for v in (1, 2, 3):
            self.lista.insert(v)
        self.assertEqual(self.lista.delete(lambda x: x == 2), 2)
        self.assertEqual(self.lista.a_list(), [1, 3])

    def test_delete_fin(self):
        for v in (1, 2, 3):
            self.lista.insert(v)
        self.assertEqual(self.lista.delete(lambda x: x == 3), 3)
        self.assertEqual(self.lista.a_list(), [1, 2])

    def test_delete_inexistente(self):
        self.lista.insert(1)
        self.assertIsNone(self.lista.delete(lambda x: x == 99))
        self.assertEqual(self.lista.size(), 1)

    def test_delete_unico(self):
        self.lista.insert(42)
        self.lista.delete(lambda x: x == 42)
        self.assertEqual(self.lista.size(), 0)
        self.assertEqual(self.lista.a_list(), [])


# ======================================================================
# DoubleList
# ======================================================================
class TestDoubleList(unittest.TestCase):

    def setUp(self):
        self.lista = DoubleList()

    def test_insert_sort_ordena(self):
        clave = lambda s: (s['anio'], s['term'])
        for s in [(2024, 2), (2023, 1), (2024, 1)]:
            self.lista.insert_sort(
                {'anio': s[0], 'term': s[1], 'materias': []}, clave)
        esperado = [(2023, 1), (2024, 1), (2024, 2)]
        obtenido = [(s['anio'], s['term']) for s in self.lista.loop_forward()]
        self.assertEqual(obtenido, esperado)

    def test_loop_backward(self):
        for v in (1, 2, 3):
            self.lista.insert_sort(v, lambda x: x)
        self.assertEqual(self.lista.loop_backward(), [3, 2, 1])

    def test_loop_forward_y_backward_son_simetricos(self):
        for v in (5, 3, 8, 1, 9):
            self.lista.insert_sort(v, lambda x: x)
        adelante = self.lista.loop_forward()
        atras = self.lista.loop_backward()
        self.assertEqual(adelante, sorted(adelante))
        self.assertEqual(atras, list(reversed(adelante)))

    def test_search_existente(self):
        self.lista.insert_sort(
            {'anio': 2024, 'term': 1, 'materias': []},
            lambda s: (s['anio'], s['term']))
        resultado = self.lista.search(
            lambda s: s['anio'] == 2024 and s['term'] == 1)
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado['anio'], 2024)

    def test_search_inexistente(self):
        self.lista.insert_sort(
            {'anio': 2024, 'term': 1, 'materias': []},
            lambda s: (s['anio'], s['term']))
        resultado = self.lista.search(lambda s: s['anio'] == 9999)
        self.assertIsNone(resultado)

    def test_delete_inicio(self):
        for v in (1, 2, 3):
            self.lista.insert_sort(v, lambda x: x)
        self.assertEqual(self.lista.delete(lambda x: x == 1), 1)
        self.assertEqual(self.lista.loop_forward(), [2, 3])
        # Verifica que loop_backward sigue funcionando tras borrar la cabeza
        self.assertEqual(self.lista.loop_backward(), [3, 2])

    def test_delete_fin(self):
        for v in (1, 2, 3):
            self.lista.insert_sort(v, lambda x: x)
        self.assertEqual(self.lista.delete(lambda x: x == 3), 3)
        self.assertEqual(self.lista.loop_forward(), [1, 2])
        self.assertEqual(self.lista.loop_backward(), [2, 1])

    def test_delete_medio(self):
        for v in (1, 2, 3, 4, 5):
            self.lista.insert_sort(v, lambda x: x)
        self.lista.delete(lambda x: x == 3)
        self.assertEqual(self.lista.loop_forward(), [1, 2, 4, 5])
        self.assertEqual(self.lista.loop_backward(), [5, 4, 2, 1])

    def test_vacia(self):
        self.assertTrue(self.lista.is_empty() if hasattr(self.lista, 'is_empty')
                        else self.lista.size() == 0)
        self.assertEqual(self.lista.loop_forward(), [])
        self.assertEqual(self.lista.loop_backward(), [])


if __name__ == '__main__':
    unittest.main()