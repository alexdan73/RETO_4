"""Pruebas ligeras del módulo de benchmarks (tamaños reducidos)."""
import unittest

try:
    from . import _bootstrap  # noqa: F401  (python -m unittest tests.test_xxx)
except ImportError:
    import _bootstrap  # noqa: F401  (discover -s tests / ejecución directa)
from benchmarks import ejecutar_benchmarks, generar_insights


class TestBenchmarks(unittest.TestCase):

    def test_estructura_de_resultados(self):
        filas = ejecutar_benchmarks(tamanos=(50, 100, 200), ops_cola=200, repeticiones=2)
        escenarios = {f[0] for f in filas}
        for esperado in ("Inserción ListaSimple (final)", "Búsqueda ListaSimple (fin)",
                         "Eliminación ListaSimple (medio)", "Eliminación ListaDoble (medio)",
                         "ColaSimple: enqueue", "ColaCircular: dequeue", "ColaPrioridad: enqueue"):
            self.assertIn(esperado, escenarios)
        self.assertTrue(all(t >= 0 for _, _, t in filas))

    def test_insights_se_generan_de_los_datos(self):
        tam = (50, 100, 200)
        filas = ejecutar_benchmarks(tamanos=tam, ops_cola=200, repeticiones=2)
        insights = generar_insights(filas, tamanos=tam, ops_cola=200)
        self.assertGreaterEqual(len(insights), 3)


if __name__ == '__main__':
    unittest.main()
