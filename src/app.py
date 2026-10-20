"""SIGA - Sistema Integral de Gestión Académica (Reto 4)."""
from stack import Stack
from simple_queue import SimpleQueue
from circular_queue import CircularQueue
from priority_queue import PriorityQueue
from simple_list import SimpleList
from double_list import DoubleList
from persistence_csv import export_register, import_register
from persistence_json import (
    export_history, import_history,
    export_waits, import_waits
)

DATA_DIR = "data"


class SIGA:
    """Sistema que integra pila, colas y listas."""

    def __init__(self, course_name="Sin Nombre", quota=10):
        self.course_name = course_name
        self.quota = quota
        self.registereds = SimpleList()
        self.simple_queue = SimpleQueue()
        self.priority_queue = PriorityQueue()
        self.circular_queue = CircularQueue()
        self.record = DoubleList()
        self.acctions = Stack()

    # ------------------------------------------------------------------
    # Utilidades internas
    # ------------------------------------------------------------------
    def _id_system(self, _id):
        """True si el ID ya existe en cualquier estructura."""
        # NOTA: asume que SimpleList.search retorna (indice, valor)
        if self.registereds.search(lambda e: e['id'] == _id)[0] >= 0:
            return True
        for queue in (self.simple_queue, self.circular_queue):
            for e in queue.a_list():
                if e['id'] == _id:
                    return True
        for e in self.priority_queue.a_list():
            if e['id'] == _id:
                return True
        return False

    def _next_student(self):
        """Saca el siguiente respetando prioridad sobre simple."""
        if not self.priority_queue.is_empty():
            return self.priority_queue.dequeue(), 'prio'
        if not self.simple_queue.is_empty():
            return self.simple_queue.dequeue(), 'simple'
        return None, None

    # ------------------------------------------------------------------
    # Módulo de inscripciones
    # ------------------------------------------------------------------
    def comming_student(self, _id, name, priority=None, mail=''):
        if self._id_system(_id):
            return False, "ID ya existe en el sistema"

        stu = {'id': _id, 'nombre': name, 'correo': mail,
               'cod_curso': self.course_name}

        if priority is not None and 1 <= priority <= 5:
            self.priority_queue.enqueue(stu, priority)
        else:
            self.simple_queue.enqueue(stu)
        return True, "Estudiante agregado a la lista"

    def attend_turns(self, n):
        """Procesa n turnos. Devuelve cuántos se procesaron (inscritos + espera)."""
        attends = 0
        for _ in range(n):
            stu, origin = self._next_student()
            if stu is None:
                break
            if self.registereds.size() < self.quota:
                self.registereds.insert(stu)
                self.acctions.push(
                    {'tipo': 'INSCRIBIR', 'stu': stu, 'origen': origin}
                )
            else:
                self.circular_queue.enqueue(stu)
                self.acctions.push(
                    {'tipo': 'ENVIAR_A_ESPERA', 'stu': stu, 'origen': origin}
                )
            attends += 1          # FIX: fuera del if/else
        return attends

    def withdraw(self, _id):
        stu = self.registereds.delete(lambda e: e['id'] == _id)
        if stu is None:
            return None

        self.acctions.push({'tipo': 'RETIRAR', 'stu': stu})

        # Reasignar: prioridad primero, luego circular
        if not self.priority_queue.is_empty():
            reassing = self.priority_queue.dequeue()
            _from = 'prio'
        elif not self.circular_queue.is_empty():
            reassing = self.circular_queue.dequeue()
            _from = 'circ'
        else:
            reassing = None

        if reassing:
            self.registereds.insert(reassing)
            self.acctions.push(
                {'tipo': 'REASIGNAR', 'stu': reassing, 'desde': _from}
            )
        return stu

    # ------------------------------------------------------------------
    # Deshacer
    # ------------------------------------------------------------------
    def undo(self):
        if self.acctions.is_empty():
            return "Nada que deshacer"
        ac = self.acctions.pop()
        _type = ac['tipo']

        if _type == 'INSCRIBIR':
            self.registereds.delete(lambda e: e['id'] == ac['stu']['id'])
            if ac['origen'] == 'prio':       # FIX: 'origen' no 'origin'
                self.priority_queue.front_insert(
                    ac['stu'], ac['stu'].get('p', 1))
            else:
                self.simple_queue.front_insert(ac['stu'])
            return f"Deshecho: INSCRIBIR de {ac['stu']['nombre']}"

        if _type == 'ENVIAR_A_ESPERA':
            self.circular_queue.last_remove()
            if ac['origen'] == 'prio':
                self.priority_queue.front_insert(
                    ac['stu'], ac['stu'].get('p', 1))
            else:
                self.simple_queue.front_insert(ac['stu'])
            return f"Deshecho: ENVIAR_A_ESPERA de {ac['stu']['nombre']}"

        if _type == 'REASIGNAR':
            self.registereds.delete(lambda e: e['id'] == ac['stu']['id'])
            if ac['desde'] == 'prio':
                self.priority_queue.front_insert(
                    ac['stu'], ac['stu'].get('p', 1))
            else:
                self.circular_queue.front_insert(ac['stu'])
            return f"Deshecho: REASIGNAR de {ac['stu']['nombre']}"

        if _type == 'RETIRAR':
            self.registereds.insert(ac['stu'])
            return f"Deshecho: RETIRAR de {ac['stu']['nombre']}"

        if _type == 'ACTUALIZAR_NOTA':
            sem = self.record.search(
                lambda s: s['anio'] == ac['anio'] and s['term'] == ac['term']
            )
            if sem:
                for mat in sem['materias']:
                    if mat['cod'] == ac['cod']:      # FIX: ac no a
                        mat['nota'] = ac['nota_ant']
                        break
                return f"Deshecho: ACTUALIZAR_NOTA de {ac['cod']}"  # FIX: fuera del for
            return "Semestre no encontrado"

        return "Acción desconocida"

    # ------------------------------------------------------------------
    # Módulo de historial académico
    # ------------------------------------------------------------------
    def add_semester(self, anio, term, subjects=None):
        sem = {'anio': anio, 'term': term, 'materias': subjects or []}
        self.record.insert_sort(sem, lambda s: (s['anio'], s['term']))

    def add_subject(self, anio, term, cod, name, grade):
        sem = self.record.search(
            lambda s: s['anio'] == anio and s['term'] == term
        )
        if sem is None:
            return False
        sem['materias'].append({'cod': cod, 'nombre': name, 'nota': grade})
        return True

    def update_grade(self, anio, term, cod, grade):
        sem = self.record.search(
            lambda s: s['anio'] == anio and s['term'] == term
        )
        if sem is None:
            return False

        for mat in sem['materias']:
            if mat['cod'] == cod:
                self.acctions.push({
                    'tipo': 'ACTUALIZAR_NOTA', 'anio': anio, 'term': term,
                    'cod': cod, 'nota_ant': mat['nota']})
                mat['nota'] = grade
                return True
        return False

    # ------------------------------------------------------------------
    # Persistencia (delegada a módulos defensivos)
    # ------------------------------------------------------------------
    def export_all(self):
        ok1 = export_register(self.registereds, f"{DATA_DIR}/inscritos.csv")
        ok2 = export_history(self.record, f"{DATA_DIR}/historial.json")
        ok3 = export_waits(self.circular_queue, self.priority_queue,
                           f"{DATA_DIR}/esperas.json")
        return ok1 and ok2 and ok3

    def import_all(self):
        self.registereds = SimpleList()
        self.record = DoubleList()
        self.circular_queue = CircularQueue()
        self.priority_queue = PriorityQueue()
        # NOTA: simple_queue y acctions NO se resetean (decisión de diseño:
        # la cola simple es estado efímero; el historial de undo no se persiste)
        n = 0
        n += import_register(self.registereds, f"{DATA_DIR}/inscritos.csv")
        n += import_history(self.record, f"{DATA_DIR}/historial.json")
        n += import_waits(self.circular_queue, self.priority_queue,
                          f"{DATA_DIR}/esperas.json")
        return n


# ======================================================================
# Interfaz CLI
# ======================================================================
def show_registered(siga):
    data = siga.registereds.a_list()
    print(f"\nInscritos ({len(data)}/{siga.quota}):")
    if not data:
        print("  (vacío)")
    for e in data:
        print(f"  - ID {e['id']} | {e['nombre']} | {e.get('correo', '')}")


def show_queues(siga):
    print("\nCola simple:",
          [e['nombre'] for e in siga.simple_queue.a_list()] or "(vacía)")
    print("Cola prioridad:",
          [f"{e['nombre']}(p={e.get('p')})"
           for e in siga.priority_queue.a_list()] or "(vacía)")
    print("Cola circular:",
          [e['nombre'] for e in siga.circular_queue.a_list()] or "(vacía)")


def menu_history(siga):
    while True:
        print("\n--- Historial académico ---")
        print("1. Agregar semestre")
        print("2. Agregar materia a semestre")
        print("3. Actualizar nota")
        print("4. Recorrer adelante")
        print("5. Recorrer atrás")
        print("6. Buscar semestre")
        print("0. Volver")
        op = input("Opción: ").strip()
        if op == '0':
            break
        try:
            if op == '1':
                anio = int(input("Año: "))
                term = int(input("Término: "))
                siga.add_semester(anio, term)
                print("  ✓ Semestre agregado")
            elif op == '2':
                anio = int(input("Año: "))
                term = int(input("Término: "))
                cod = input("Código materia: ")
                nombre = input("Nombre materia: ")
                nota = float(input("Nota: "))
                ok = siga.add_subject(anio, term, cod, nombre, nota)
                print("  ✓ Agregada" if ok else "  ✗ No existe el semestre")
            elif op == '3':
                anio = int(input("Año: "))
                term = int(input("Término: "))
                cod = input("Código materia: ")
                nota = float(input("Nueva nota: "))
                ok = siga.update_grade(anio, term, cod, nota)
                print("  ✓ Actualizada" if ok else "  ✗ No encontrada")
            elif op == '4':
                for s in siga.record.loop_forward():
                    print(f"  {s['anio']}-{s['term']}: {s['materias']}")
            elif op == '5':
                for s in siga.record.loop_backward():
                    print(f"  {s['anio']}-{s['term']}: {s['materias']}")
            elif op == '6':
                anio = int(input("Año: "))
                term = int(input("Término: "))
                s = siga.record.search(
                    lambda x: x['anio'] == anio and x['term'] == term)
                print(s if s else "  ✗ No encontrado")
        except ValueError:
            print("  ✗ Entrada inválida")


def menu_persistence(siga):
    print("\n--- Persistencia ---")
    print("1. Exportar todo")
    print("2. Importar todo (reemplaza estado actual)")
    print("0. Volver")
    op = input("Opción: ").strip()
    if op == '1':
        ok = siga.export_all()
        print("  ✓ Exportado a /data" if ok else "  ⚠ Hubo errores al exportar")
    elif op == '2':
        n = siga.import_all()
        print(f"  ✓ Importación completa ({n} registros)")


def main():
    siga = SIGA()
    while True:
        print("\n=========== SIGA ===========")
        print("1.  Configurar curso")
        print("2.  Llegada de estudiante")
        print("3.  Procesar N turnos")
        print("4.  Retirar estudiante")
        print("5.  Mostrar inscritos")
        print("6.  Mostrar colas")
        print("7.  Historial académico")
        print("8.  Deshacer última acción")
        print("9.  Persistencia (export/import)")
        print("10. Benchmarks")
        print("11. Salir")
        op = input("Opción: ").strip()

        try:
            if op == '1':
                siga.course_name = input("Nombre del curso: ") or siga.course_name
                siga.quota = int(input("Cupos: "))
                print(f"  ✓ Curso '{siga.course_name}' con {siga.quota} cupos")
            elif op == '2':
                _id = int(input("ID: "))
                nombre = input("Nombre: ")
                p_str = input("Prioridad (1-5, vacío = normal): ").strip()
                priority = int(p_str) if p_str else None
                mail = input("Correo (opcional): ").strip()
                ok, msg = siga.comming_student(_id, nombre, priority, mail)
                print(f"  {'✓' if ok else '✗'} {msg}")
            elif op == '3':
                n = int(input("Cuántos turnos: "))
                print(f"  Procesados: {siga.attend_turns(n)}")
            elif op == '4':
                _id = int(input("ID a retirar: "))
                stu = siga.withdraw(_id)
                print(f"  {'✓ Retirado ' + stu['nombre'] if stu else '✗ No encontrado'}")
            elif op == '5':
                show_registered(siga)
            elif op == '6':
                show_queues(siga)
            elif op == '7':
                menu_history(siga)
            elif op == '8':
                print(f"  {siga.undo()}")
            elif op == '9':
                menu_persistence(siga)
            elif op == '10':
                from benchmarks import run_benchmarks
                run_benchmarks()
            elif op == '11':
                print("¡Hasta luego!")
                break
        except ValueError:
            print("  ✗ Entrada inválida")
        except Exception as e:
            print(f"  ✗ Error: {e}")


if __name__ == "__main__":
    main()