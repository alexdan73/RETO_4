"""Pruebas unitarias para ListaSimple y ListaDoble."""
import unittest

try:
    from . import _bootstrap  # noqa: F401  (python -m unittest tests.test_xxx)
except ImportError:
    import _bootstrap  # noqa: F401  (discover -s tests / ejecución directa)
from lista_simple import ListaSimple
from lista_doble import ListaDoble

CLAVE_SEM = lambda s: (s['anio'], s['term'])  # noqa: E731


class TestListaSimple(unittest.TestCase):

    def setUp(self):
        self.lista = ListaSimple()

    def test_nueva_esta_vacia(self):
        self.assertTrue(self.lista.is_empty())
        self.assertEqual(self.lista.size(), 0)
        self.assertEqual(self.lista.recorrer(), [])

    def test_insertar_recorrer(self):
        for v in (10, 20, 30):
            self.lista.insertar(v)
        self.assertEqual(self.lista.recorrer(), [10, 20, 30])
        self.assertEqual(self.lista.size(), 3)

    def test_buscar_existente(self):
        for v in (5, 10, 15):
            self.lista.insertar(v)
        self.assertEqual(self.lista.buscar(lambda x: x == 10), (1, 10))

    def test_buscar_inexistente_y_vacia(self):
        self.assertEqual(self.lista.buscar(lambda x: x == 1), (-1, None))
        self.lista.insertar(1)
        self.assertEqual(self.lista.buscar(lambda x: x == 99), (-1, None))

    def test_eliminar_inicio_medio_fin(self):
        for v in (1, 2, 3, 4):
            self.lista.insertar(v)
        self.assertEqual(self.lista.eliminar(lambda x: x == 1), 1)
        self.assertEqual(self.lista.eliminar(lambda x: x == 3), 3)
        self.assertEqual(self.lista.eliminar(lambda x: x == 4), 4)
        self.assertEqual(self.lista.recorrer(), [2])

    def test_insertar_tras_eliminar_el_ultimo(self):
        """El puntero a la cola debe actualizarse al borrar el último nodo."""
        for v in (1, 2, 3):
            self.lista.insertar(v)
        self.lista.eliminar(lambda x: x == 3)
        self.lista.insertar(4)
        self.assertEqual(self.lista.recorrer(), [1, 2, 4])

    def test_eliminar_inexistente(self):
        self.lista.insertar(1)
        self.assertIsNone(self.lista.eliminar(lambda x: x == 99))
        self.assertEqual(self.lista.size(), 1)

    def test_eliminar_unico_y_reutilizar(self):
        self.lista.insertar(42)
        self.lista.eliminar(lambda x: x == 42)
        self.assertEqual(self.lista.size(), 0)
        self.lista.insertar(7)
        self.assertEqual(self.lista.recorrer(), [7])


class TestListaDoble(unittest.TestCase):

    def setUp(self):
        self.lista = ListaDoble()

    def test_vacia(self):
        self.assertTrue(self.lista.is_empty())
        self.assertEqual(self.lista.recorrer_adelante(), [])
        self.assertEqual(self.lista.recorrer_atras(), [])
        self.assertIsNone(self.lista.buscar(lambda s: True))
        self.assertIsNone(self.lista.eliminar(lambda s: True))

    def test_insertar_ordenado_desordenado(self):
        for a, t in [(2024, 2), (2023, 1), (2024, 1), (2022, 2)]:
            self.lista.insertar_ordenado({'anio': a, 'term': t, 'materias': []}, CLAVE_SEM)
        obtenido = [(s['anio'], s['term']) for s in self.lista.recorrer_adelante()]
        self.assertEqual(obtenido, [(2022, 2), (2023, 1), (2024, 1), (2024, 2)])

    def test_recorridos_son_simetricos(self):
        for v in (5, 3, 8, 1, 9):
            self.lista.insertar_ordenado(v, lambda x: x)
        adelante = self.lista.recorrer_adelante()
        self.assertEqual(adelante, [1, 3, 5, 8, 9])
        self.assertEqual(self.lista.recorrer_atras(), list(reversed(adelante)))

    def test_insertar_al_inicio_medio_y_fin(self):
        for v in (10, 30):
            self.lista.insertar_ordenado(v, lambda x: x)
        self.lista.insertar_ordenado(5, lambda x: x)
        self.lista.insertar_ordenado(20, lambda x: x)
        self.lista.insertar_ordenado(40, lambda x: x)
        self.assertEqual(self.lista.recorrer_adelante(), [5, 10, 20, 30, 40])
        self.assertEqual(self.lista.recorrer_atras(), [40, 30, 20, 10, 5])
        self.assertEqual(self.lista.size(), 5)

    def test_buscar(self):
        self.lista.insertar_ordenado({'anio': 2024, 'term': 1, 'materias': []}, CLAVE_SEM)
        self.assertEqual(self.lista.buscar(lambda s: s['anio'] == 2024)['term'], 1)
        self.assertIsNone(self.lista.buscar(lambda s: s['anio'] == 9999))

    def test_eliminar_inicio_medio_fin_mantiene_enlaces(self):
        for v in (1, 2, 3, 4, 5):
            self.lista.insertar_ordenado(v, lambda x: x)
        self.assertEqual(self.lista.eliminar(lambda x: x == 1), 1)
        self.assertEqual(self.lista.eliminar(lambda x: x == 3), 3)
        self.assertEqual(self.lista.eliminar(lambda x: x == 5), 5)
        self.assertEqual(self.lista.recorrer_adelante(), [2, 4])
        self.assertEqual(self.lista.recorrer_atras(), [4, 2])
        self.assertEqual(self.lista.size(), 2)

    def test_eliminar_unico_y_reutilizar(self):
        self.lista.insertar_ordenado(1, lambda x: x)
        self.lista.eliminar(lambda x: x == 1)
        self.assertTrue(self.lista.is_empty())
        self.lista.insertar_ordenado(2, lambda x: x)
        self.assertEqual(self.lista.recorrer_atras(), [2])

    def test_insertar_final(self):
        for v in (3, 1, 2):
            self.lista.insertar_final(v)
        self.assertEqual(self.lista.recorrer_adelante(), [3, 1, 2])
        self.assertEqual(self.lista.recorrer_atras(), [2, 1, 3])


if __name__ == '__main__':
    unittest.main()
