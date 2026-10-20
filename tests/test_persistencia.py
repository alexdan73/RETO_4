"""Pruebas de persistencia CSV/JSON, reconstrucción de estructuras e importaciones corruptas."""
import json
import os
import tempfile
import unittest

try:
    from . import _bootstrap  
except ImportError:
    import _bootstrap 
from siga import SIGA
from errores import ErrorPersistencia
from lista_simple import ListaSimple
from lista_doble import ListaDoble
from cola_circular import ColaCircular
from cola_prioridad import ColaPrioridad
from persistencia_csv import importar_inscritos, exportar_inscritos
from persistencia_json import importar_historial, importar_esperas


def escribir(ruta, texto):
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(texto)


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name
        self.s = SIGA("ED", 2, dir_datos=self.dir)

    def tearDown(self):
        self._tmp.cleanup()

    def ruta(self, nombre):
        return os.path.join(self.dir, nombre)

    def poblar(self):
        for i, (n, p) in enumerate([("A", None), ("B", None), ("C", None), ("D", None)], 1):
            self.s.llegada_estudiante(i, n, p, f"{n.lower()}@u.edu")
        self.s.llegada_estudiante(10, "VIP", 5)
        self.s.procesar_turnos(5)       # VIP, A inscritos; B, C, D circular
        self.s.llegada_estudiante(11, "VIP2", 4)   # queda esperando en prioridad
        self.s.agregar_semestre(2024, 2)
        self.s.agregar_semestre(2023, 1)
        self.s.agregar_materia(2023, 1, "ED-101", "Estructuras I", 18)


class TestRoundTrip(Base):

    def test_exportar_importar_reconstruye_todo(self):
        self.poblar()
        self.assertTrue(all(ok for ok, _ in self.s.exportar()))
        sin_p = lambda lista: [{k: v for k, v in e.items() if k != 'p'} for e in lista]  # noqa: E731
        antes = (sin_p(self.s.inscritos.recorrer()), self.s.cola_circular.a_lista(),
                 self.s.cola_prioridad.a_lista(), self.s.historial.recorrer_adelante())

        nuevo = SIGA("ED", 2, dir_datos=self.dir)
        informe = nuevo.importar()
        self.assertTrue(all(ok for ok, _ in informe), informe)
        despues = (sin_p(nuevo.inscritos.recorrer()), nuevo.cola_circular.a_lista(),
                   nuevo.cola_prioridad.a_lista(), nuevo.historial.recorrer_adelante())
        self.assertEqual(antes, despues)
        self.assertEqual(nuevo.verificar_consistencia(), [])
        # las estructuras importadas siguen siendo funcionales
        nuevo.retirar(10)
        self.assertEqual(nuevo.inscritos.size(), 2)

    def test_formatos_del_enunciado(self):
        self.poblar()
        self.s.exportar()
        with open(self.ruta('inscritos.csv'), encoding='utf-8') as f:
            self.assertEqual(f.readline().strip(), "id,nombre,correo,cod_curso")
        with open(self.ruta('historial.json'), encoding='utf-8') as f:
            sem = json.load(f)['semestres']
        self.assertEqual([(x['anio'], x['term']) for x in sem], [(2023, 1), (2024, 2)])
        self.assertEqual(sem[0]['materias'][0], {'cod': 'ED-101', 'nombre': 'Estructuras I', 'nota': 18})
        with open(self.ruta('esperas.json'), encoding='utf-8') as f:
            esperas = json.load(f)
        self.assertEqual(set(esperas), {'circular', 'prioridad'})
        self.assertEqual(esperas['prioridad'][0]['p'], 4)

    def test_acentos_y_comas_en_csv(self):
        self.s.llegada_estudiante(1, "Sofía, Ñandú \"Z\"")
        self.s.procesar_turnos(1)
        self.s.exportar(('inscritos',))
        nuevo = SIGA("ED", 2, dir_datos=self.dir)
        nuevo.importar(('inscritos',))
        self.assertEqual(nuevo.inscritos.recorrer()[0]['nombre'], "Sofía, Ñandú \"Z\"")

    def test_exportar_estructuras_vacias_e_importar(self):
        self.assertTrue(all(ok for ok, _ in self.s.exportar()))
        nuevo = SIGA("ED", 2, dir_datos=self.dir)
        self.assertTrue(all(ok for ok, _ in nuevo.importar()))
        self.assertTrue(nuevo.inscritos.is_empty() and nuevo.historial.is_empty())

    def test_importar_vacia_el_stack_de_acciones(self):
        self.poblar()
        self.s.exportar()
        self.s.importar()
        self.assertEqual(self.s.deshacer(), "Nada que deshacer")


class TestImportacionesCorruptas(Base):

    def test_archivos_inexistentes_conservan_el_estado(self):
        self.poblar()
        antes = self.s.inscritos.recorrer()
        informe = self.s.importar()
        self.assertTrue(all(not ok for ok, _ in informe))
        self.assertEqual(self.s.inscritos.recorrer(), antes)
        self.assertEqual(self.s.historial.size(), 2)

    def test_json_corrupto_conserva_el_estado(self):
        self.poblar()
        escribir(self.ruta('historial.json'), '{"semestres": [ {"anio": 2024,')
        escribir(self.ruta('esperas.json'), 'esto no es json')
        informe = self.s.importar(('historial', 'esperas'))
        self.assertTrue(all(not ok for ok, _ in informe))
        self.assertEqual(self.s.historial.size(), 2)
        self.assertEqual(self.s.cola_circular.size(), 3)

    def test_historial_rechaza_notas_fuera_de_rango(self):
        """Consistencia con agregar_materia: la nota debe estar entre 0 y 20."""
        datos = {"semestres": [
            {"anio": 2024, "term": 1, "materias": [{"cod": "A", "nombre": "A", "nota": 999}]},
            {"anio": 2024, "term": 2, "materias": [{"cod": "B", "nombre": "B", "nota": -1}]},
            {"anio": 2025, "term": 1, "materias": [{"cod": "C", "nombre": "C", "nota": 21}]},
            {"anio": 2023, "term": 1, "materias": [{"cod": "D", "nombre": "D", "nota": 0}]},
            {"anio": 2023, "term": 2, "materias": [{"cod": "E", "nombre": "E", "nota": 20}]},
        ]}
        escribir(self.ruta('historial.json'), json.dumps(datos))
        lista = ListaDoble()
        imp, om = importar_historial(lista, self.ruta('historial.json'))
        self.assertEqual((imp, om), (2, 3))
        self.assertEqual([(s['anio'], s['term']) for s in lista.recorrer_adelante()],
                        [(2023, 1), (2023, 2)])

    def test_json_con_formato_invalido(self):
        for contenido in ('[1, 2, 3]', '{"semestres": "no es lista"}', '{}', 'null', ''):
            escribir(self.ruta('historial.json'), contenido)
            with self.assertRaises(ErrorPersistencia, msg=contenido):
                importar_historial(ListaDoble(), self.ruta('historial.json'))
        escribir(self.ruta('esperas.json'), '{"circular": 5}')
        with self.assertRaises(ErrorPersistencia):
            importar_esperas(ColaCircular(), ColaPrioridad(), self.ruta('esperas.json'))
        escribir(self.ruta('esperas.json'), '{}')
        with self.assertRaises(ErrorPersistencia):
            importar_esperas(ColaCircular(), ColaPrioridad(), self.ruta('esperas.json'))

    def test_historial_omite_semestres_invalidos_sin_crashear(self):
        datos = {"semestres": [
            {"anio": "abc", "term": 1},                                  # tipo inválido
            {"anio": 2024},                                              # falta term
            "basura", None, 5,
            {"anio": 2024, "term": 1, "materias": "x"},                  # materias no es lista
            {"anio": 2024, "term": 1, "materias": [{"cod": "A", "nota": "mala"}]},
            {"anio": 2023, "term": 2, "materias": [{"cod": "ED-1", "nombre": "N", "nota": 15}]},
            {"anio": 2023, "term": 2},                                   # duplicado
            {"anio": 2022, "term": 1},                                   # válido, sin materias
        ]}
        escribir(self.ruta('historial.json'), json.dumps(datos))
        lista = ListaDoble()
        imp, om = importar_historial(lista, self.ruta('historial.json'))
        self.assertEqual((imp, om), (2, 8))
        self.assertEqual([(s['anio'], s['term']) for s in lista.recorrer_adelante()],
                         [(2022, 1), (2023, 2)])

    def test_historial_desordenado_se_ordena_al_importar(self):
        datos = {"semestres": [{"anio": 2024, "term": 2}, {"anio": 2022, "term": 1},
                               {"anio": 2024, "term": 1}]}
        escribir(self.ruta('historial.json'), json.dumps(datos))
        lista = ListaDoble()
        importar_historial(lista, self.ruta('historial.json'))
        self.assertEqual([(s['anio'], s['term']) for s in lista.recorrer_atras()],
                         [(2024, 2), (2024, 1), (2022, 1)])

    def test_csv_filas_corruptas_se_omiten(self):
        escribir(self.ruta('inscritos.csv'),
                 "id,nombre,correo,cod_curso\n"
                 "1,Ana,a@u.edu,ED\n"
                 "abc,Mal,x@u.edu,ED\n"         # id no numérico
                 "2,,b@u.edu,ED\n"              # nombre vacío
                 "-4,Neg,,ED\n"                 # id negativo
                 "5\n"                           # fila corta
                 "1,Repetida,,ED\n"              # ID duplicado
                 "3,Beto,,ED\n")
        lista = ListaSimple()
        imp, om = importar_inscritos(
            lista, self.ruta('inscritos.csv'),
            rechazar=lambda r: lista.buscar(lambda e: e['id'] == r['id'])[0] >= 0)
        self.assertEqual((imp, om), (2, 5))
        self.assertEqual([e['id'] for e in lista.recorrer()], [1, 3])

    def test_csv_sin_encabezado_valido_o_vacio(self):
        escribir(self.ruta('inscritos.csv'), "1,Ana,a@u.edu,ED\n")
        with self.assertRaises(ErrorPersistencia):
            importar_inscritos(ListaSimple(), self.ruta('inscritos.csv'))
        escribir(self.ruta('inscritos.csv'), "")
        with self.assertRaises(ErrorPersistencia):
            importar_inscritos(ListaSimple(), self.ruta('inscritos.csv'))

    def test_csv_solo_encabezado(self):
        escribir(self.ruta('inscritos.csv'), "id,nombre,correo,cod_curso\n")
        self.assertEqual(importar_inscritos(ListaSimple(), self.ruta('inscritos.csv')), (0, 0))

    def test_csv_binario_no_utf8(self):
        with open(self.ruta('inscritos.csv'), 'wb') as f:
            f.write(b"id,nombre\n1,\xff\xfe\xfa\n")
        with self.assertRaises(ErrorPersistencia):
            importar_inscritos(ListaSimple(), self.ruta('inscritos.csv'))

    def test_esperas_omite_registros_invalidos(self):
        datos = {"circular": [{"id": 1, "nombre": "Diego"}, {"nombre": "sin id"}, "x"],
                 "prioridad": [{"id": 2, "nombre": "Sofía", "p": 5},
                               {"id": 3, "nombre": "SinP"},
                               {"id": 4, "nombre": "PMala", "p": 9},
                               {"id": 5, "nombre": "PTexto", "p": "alta"}]}
        escribir(self.ruta('esperas.json'), json.dumps(datos))
        circ, prio = ColaCircular(), ColaPrioridad()
        imp, om = importar_esperas(circ, prio, self.ruta('esperas.json'))
        self.assertEqual((imp, om), (2, 5))
        self.assertEqual(circ.a_lista()[0]['nombre'], "Diego")
        self.assertEqual(prio.front()['p'], 5)

    def test_importar_depura_ids_duplicados_entre_estructuras(self):
        escribir(self.ruta('inscritos.csv'),
                 "id,nombre,correo,cod_curso\n1,Ana,,ED\n2,Beto,,ED\n")
        escribir(self.ruta('esperas.json'), json.dumps({
            "circular": [{"id": 1, "nombre": "Ana-clon"}, {"id": 3, "nombre": "Carla"},
                         {"id": 3, "nombre": "Carla2"}],
            "prioridad": [{"id": 3, "nombre": "Carla-prio", "p": 5}]}))
        self.s.llegada_estudiante(2, "Beto-en-simple")          # ya inscrito por el CSV
        self.s.llegada_estudiante(9, "Zoe")                      # legítimo, debe sobrevivir
        informe = self.s.importar(('inscritos', 'esperas'))
        self.assertEqual(self.s.verificar_consistencia(), [], informe)
        self.assertEqual(nombres_de(self.s.cola_prioridad), ["Carla-prio"])
        self.assertEqual(nombres_de(self.s.cola_circular), [])
        self.assertEqual(nombres_de(self.s.cola_simple), ["Zoe"])

    def test_exportar_a_ruta_invalida_lanza_error_controlado(self):
        bloqueo = self.ruta('archivo_normal')
        escribir(bloqueo, 'x')
        lista = ListaSimple()
        with self.assertRaises(ErrorPersistencia):
            exportar_inscritos(lista, os.path.join(bloqueo, 'sub', 'inscritos.csv'))
        s = SIGA("ED", 1, dir_datos=os.path.join(bloqueo, 'sub'))
        self.assertTrue(all(not ok for ok, _ in s.exportar()))


def nombres_de(cola):
    return [e['nombre'] for e in cola.a_lista()]


if __name__ == '__main__':
    unittest.main()
