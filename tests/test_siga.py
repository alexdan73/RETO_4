"""Pruebas del sistema integrado: inscripciones, deshacer, historial y casos límite."""
import unittest

try:
    from . import _bootstrap  # noqa: F401  (python -m unittest tests.test_xxx)
except ImportError:
    import _bootstrap  # noqa: F401  (discover -s tests / ejecución directa)
from siga import SIGA


def nombres(estructura):
    datos = estructura.recorrer() if hasattr(estructura, 'recorrer') else estructura.a_lista()
    return [e['nombre'] for e in datos]


class TestInscripciones(unittest.TestCase):

    def setUp(self):
        self.s = SIGA("ED", 2)

    def llegan(self, *nombres_, prioridad=None, desde=1):
        for i, n in enumerate(nombres_, desde):
            self.assertTrue(self.s.llegada_estudiante(i, n, prioridad)[0])

    # --- Casos mínimos del enunciado -----------------------------------
    def test_1_saturacion_de_cupos_va_a_cola_circular(self):
        self.llegan("A", "B", "C", "D")
        self.assertEqual(self.s.procesar_turnos(4), 4)
        self.assertEqual(nombres(self.s.inscritos), ["A", "B"])
        self.assertEqual(nombres(self.s.cola_circular), ["C", "D"])

    def test_2_prioritarios_se_atienden_antes_que_la_cola_simple(self):
        self.llegan("A", "B", "C")
        self.s.llegada_estudiante(10, "VIP", 5)
        self.s.procesar_turnos(2)
        self.assertEqual(nombres(self.s.inscritos), ["VIP", "A"])

    def test_3_retiro_reasigna_primero_prioridad_luego_circular(self):
        self.llegan("A", "B", "C")
        self.s.procesar_turnos(3)                        # C en circular
        self.s.llegada_estudiante(10, "VIP", 5)          # prioritario esperando
        self.s.retirar(1)
        self.assertEqual(nombres(self.s.inscritos), ["B", "VIP"])
        self.s.retirar(2)
        self.assertEqual(nombres(self.s.inscritos), ["VIP", "C"])
        self.assertEqual(self.s.verificar_consistencia(), [])

    def test_4_deshacer_inscribir_y_reasignar(self):
        self.llegan("A", "B", "C")
        self.s.procesar_turnos(3)
        self.s.retirar(1)                                 # RETIRAR + REASIGNAR(C)
        self.assertIn("REASIGNAR", self.s.deshacer())
        self.assertEqual(nombres(self.s.cola_circular), ["C"])
        self.assertEqual(nombres(self.s.inscritos), ["B"])
        self.assertIn("RETIRAR", self.s.deshacer())
        self.assertEqual(nombres(self.s.inscritos), ["B", "A"])
        self.assertIn("ENVIAR_A_ESPERA", self.s.deshacer())
        self.assertEqual(nombres(self.s.cola_simple), ["C"])
        self.assertIn("INSCRIBIR", self.s.deshacer())
        self.assertEqual(nombres(self.s.inscritos), ["A"])
        self.assertEqual(nombres(self.s.cola_simple), ["B", "C"])

    # --- Casos límite ---------------------------------------------------
    def test_cupos_cero_nadie_se_inscribe(self):
        s = SIGA("ED", 0)
        s.llegada_estudiante(1, "A")
        s.llegada_estudiante(2, "VIP", 5)
        s.procesar_turnos(5)
        self.assertEqual(s.inscritos.size(), 0)
        self.assertEqual(nombres(s.cola_circular), ["A"])
        self.assertEqual(nombres(s.cola_prioridad), ["VIP"])      # espera con su prioridad
        self.assertEqual(s.procesar_turnos(5), 0)

    def test_cupos_negativos_o_invalidos(self):
        self.assertFalse(self.s.configurar_curso("X", -1)[0])
        self.assertFalse(self.s.configurar_curso("X", "10")[0])
        with self.assertRaises(ValueError):
            SIGA("X", -3)
        self.assertEqual(self.s.cupos, 2)

    def test_multiples_prioritarios_orden_por_nivel_y_fifo(self):
        for id_, nom, p in [(1, "p3a", 3), (2, "p5a", 5), (3, "p5b", 5), (4, "p1", 1), (5, "p3b", 3)]:
            self.s.llegada_estudiante(id_, nom, p)
        self.s.configurar_curso("ED", 5)
        self.s.procesar_turnos(5)
        self.assertEqual(nombres(self.s.inscritos), ["p5a", "p5b", "p3a", "p3b", "p1"])

    def test_prioritario_sin_cupo_conserva_su_prioridad(self):
        self.llegan("A", "B", "C")
        self.s.procesar_turnos(3)                         # C en circular
        self.s.llegada_estudiante(10, "VIP", 5)
        self.assertEqual(self.s.procesar_turnos(3), 0)    # nada que mover
        self.assertEqual(nombres(self.s.cola_prioridad), ["VIP"])
        self.assertEqual(nombres(self.s.cola_circular), ["C"])

    def test_retiros_masivos_vacian_y_reasignan_en_orden(self):
        s = SIGA("ED", 3)
        for i in range(1, 9):
            s.llegada_estudiante(i, f"E{i}")
        s.procesar_turnos(8)
        for i in (1, 2, 3):
            s.retirar(i)
        self.assertEqual(nombres(s.inscritos), ["E4", "E5", "E6"])
        for i in (4, 5, 6, 7, 8):
            self.assertIsNotNone(s.retirar(i))
        self.assertTrue(s.inscritos.is_empty())
        self.assertTrue(s.cola_circular.is_empty())
        self.assertEqual(s.verificar_consistencia(), [])

    def test_retirar_inexistente(self):
        self.assertIsNone(self.s.retirar(999))
        self.assertEqual(self.s.deshacer(), "Nada que deshacer")

    def test_procesar_con_colas_vacias_o_n_no_positivo(self):
        self.assertEqual(self.s.procesar_turnos(5), 0)
        self.assertEqual(self.s.procesar_turnos(0), 0)
        self.assertEqual(self.s.procesar_turnos(-3), 0)

    def test_id_duplicado_en_cualquier_estructura(self):
        self.llegan("A", "B", "C")
        self.s.procesar_turnos(3)
        self.s.llegada_estudiante(10, "P", 4)
        self.s.llegada_estudiante(11, "S")
        for id_ in (1, 3, 10, 11):          # inscrito, circular, prioridad, simple
            ok, _ = self.s.llegada_estudiante(id_, "Clon")
            self.assertFalse(ok)

    def test_validaciones_de_llegada(self):
        self.assertFalse(self.s.llegada_estudiante(0, "A")[0])
        self.assertFalse(self.s.llegada_estudiante(-1, "A")[0])
        self.assertFalse(self.s.llegada_estudiante("7", "A")[0])
        self.assertFalse(self.s.llegada_estudiante(1, "   ")[0])
        self.assertFalse(self.s.llegada_estudiante(1, "A", 6)[0])
        self.assertFalse(self.s.llegada_estudiante(1, "A", 0)[0])
        self.assertTrue(self.s.cola_simple.is_empty() and self.s.cola_prioridad.is_empty())

    def test_subir_cupos_reasigna_a_los_que_esperan(self):
        self.llegan("A", "B", "C", "D")
        self.s.procesar_turnos(4)
        self.s.configurar_curso("ED", 4)
        self.assertEqual(nombres(self.s.inscritos), ["A", "B", "C", "D"])
        self.assertTrue(self.s.cola_circular.is_empty())

    def test_subir_cupos_reasigna_prioridad_antes_que_circular(self):
        """_reasignar_cupos_libres: Prioridad primero, luego Circular."""
        self.llegan("A", "B", "C")                          # cupos=2
        self.s.procesar_turnos(3)                            # A, B inscritos; C en circular
        self.s.llegada_estudiante(10, "VIP", 5)              # VIP en prioridad
        self.s.configurar_curso("ED", 4)
        self.assertEqual(nombres(self.s.inscritos), ["A", "B", "VIP", "C"])

    def test_bajar_cupos_no_expulsa_y_deshacer_retirar_respeta_cupo(self):
        self.llegan("A", "B")
        self.s.procesar_turnos(2)
        self.s.retirar(1)
        self.s.configurar_curso("ED", 1)                  # B ocupa el único cupo
        self.assertIn("No se puede deshacer RETIRAR", self.s.deshacer())
        self.assertEqual(nombres(self.s.inscritos), ["B"])

    def test_consistencia_nunca_hay_ids_repetidos(self):
        for i in range(1, 15):
            self.s.llegada_estudiante(i, f"E{i}", prioridad=(i % 6) or None)
        self.s.procesar_turnos(20)
        self.s.retirar(self.s.inscritos.recorrer()[0]['id'])
        self.s.deshacer()
        self.s.deshacer()
        self.assertEqual(self.s.verificar_consistencia(), [])


class TestHistorial(unittest.TestCase):

    def setUp(self):
        self.s = SIGA("ED", 1)

    def test_historial_vacio(self):
        self.assertEqual(self.s.historial.recorrer_adelante(), [])
        self.assertEqual(self.s.historial.recorrer_atras(), [])
        self.assertIsNone(self.s.buscar_semestre(2024, 1))
        self.assertFalse(self.s.agregar_materia(2024, 1, "ED-101", "Est", 18)[0])
        self.assertFalse(self.s.actualizar_nota(2024, 1, "ED-101", 18)[0])

    def test_semestres_desordenados_quedan_ordenados(self):
        for a, t in [(2024, 2), (2022, 1), (2024, 1), (2023, 2)]:
            self.assertTrue(self.s.agregar_semestre(a, t)[0])
        adelante = [(x['anio'], x['term']) for x in self.s.historial.recorrer_adelante()]
        self.assertEqual(adelante, [(2022, 1), (2023, 2), (2024, 1), (2024, 2)])
        atras = [(x['anio'], x['term']) for x in self.s.historial.recorrer_atras()]
        self.assertEqual(atras, list(reversed(adelante)))
        self.assertIsNotNone(self.s.buscar_semestre(2023, 2))

    def test_semestre_duplicado_o_invalido(self):
        self.assertTrue(self.s.agregar_semestre(2024, 1)[0])
        self.assertFalse(self.s.agregar_semestre(2024, 1)[0])
        self.assertFalse(self.s.agregar_semestre("2024", 1)[0])
        self.assertFalse(self.s.agregar_semestre(2024, 0)[0])
        self.assertEqual(self.s.historial.size(), 1)

    def test_materias_notas_y_validaciones(self):
        self.s.agregar_semestre(2024, 1)
        self.assertTrue(self.s.agregar_materia(2024, 1, "ED-101", "Est I", 18)[0])
        self.assertFalse(self.s.agregar_materia(2024, 1, "ED-101", "Dup", 10)[0])
        self.assertFalse(self.s.agregar_materia(2024, 1, "ED-102", "X", 21)[0])
        self.assertFalse(self.s.agregar_materia(2024, 1, "ED-102", "X", -1)[0])
        self.assertFalse(self.s.agregar_materia(2024, 1, "", "X", 10)[0])
        self.assertTrue(self.s.actualizar_nota(2024, 1, "ED-101", 15)[0])
        self.assertFalse(self.s.actualizar_nota(2024, 1, "NOPE", 15)[0])
        self.assertEqual(self.s.buscar_semestre(2024, 1)['materias'][0]['nota'], 15)

    def test_deshacer_nota_materia_y_semestre(self):
        self.s.agregar_semestre(2024, 1)
        self.s.agregar_materia(2024, 1, "ED-101", "Est I", 18)
        self.s.actualizar_nota(2024, 1, "ED-101", 10)
        self.s.deshacer()
        self.assertEqual(self.s.buscar_semestre(2024, 1)['materias'][0]['nota'], 18)
        self.s.deshacer()
        self.assertEqual(self.s.buscar_semestre(2024, 1)['materias'], [])
        self.s.deshacer()
        self.assertTrue(self.s.historial.is_empty())


if __name__ == '__main__':
    unittest.main()
