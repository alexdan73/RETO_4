"""SIGA - Sistema Integral de Gestión Académica: lógica del sistema (sin I/O de consola).

Flujo de inscripción
--------------------
  llegada  -> ColaSimple (orden de llegada)  o  ColaPrioridad (p = 1..5, 5 = crítico)
  turno    -> si hay cupo : se inscribe (ListaSimple). Orden: prioridad > circular > simple
              si NO hay cupo: el estudiante de la cola simple pasa a ColaCircular (espera);
                              los prioritarios ya están esperando en ColaPrioridad
  retiro   -> libera cupo y reasigna: primero ColaPrioridad, si está vacía ColaCircular

Invariante de consistencia: un ID aparece en UNA sola estructura a la vez.
Cada acción relevante se apila en la Pila de acciones para poder DESHACER.
"""
import os

from pila import Pila
from cola_simple import ColaSimple
from cola_circular import ColaCircular
from cola_prioridad import ColaPrioridad
from lista_simple import ListaSimple
from lista_doble import ListaDoble
from errores import ErrorPersistencia
from persistencia_csv import exportar_inscritos, importar_inscritos
from persistencia_json import (exportar_historial, importar_historial,
                               exportar_esperas, importar_esperas,
                               semestre_valido)

RUTA_DATOS = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
ARCHIVOS = {'inscritos': 'inscritos.csv',
            'historial': 'historial.json',
            'esperas': 'esperas.json'}
PARTES = ('inscritos', 'esperas', 'historial')
PRIORIDAD_MIN, PRIORIDAD_MAX = 1, 5
NOTA_MIN, NOTA_MAX = 0, 20


def _es_entero(x):
    return isinstance(x, int) and not isinstance(x, bool)


def _clave_semestre(s):
    return (s['anio'], s['term'])


class SIGA:
    """Integra pila, colas y listas en un único sistema."""

    def __init__(self, curso="Sin Nombre", cupos=10, dir_datos=RUTA_DATOS):
        if not _es_entero(cupos) or cupos < 0:
            raise ValueError("Los cupos deben ser un entero >= 0")
        self.curso = curso
        self.cupos = cupos
        self.dir_datos = dir_datos
        self.inscritos = ListaSimple()
        self.cola_simple = ColaSimple()
        self.cola_prioridad = ColaPrioridad()
        self.cola_circular = ColaCircular()
        self.historial = ListaDoble()
        self.acciones = Pila()

    # ==================================================================
    # Utilidades
    # ==================================================================
    def hay_cupo(self):
        return self.inscritos.size() < self.cupos

    def _existe_id(self, id_):
        if self.inscritos.buscar(lambda e: e['id'] == id_)[0] >= 0:
            return True
        for cola in (self.cola_simple, self.cola_circular, self.cola_prioridad):
            for e in cola.a_lista():
                if e['id'] == id_:
                    return True
        return False

    def verificar_consistencia(self):
        """Devuelve los IDs que aparecen más de una vez entre todas las estructuras."""
        vistos, duplicados = ListaSimple(), []
        for estructura in (self.inscritos, self.cola_prioridad,
                           self.cola_circular, self.cola_simple):
            for e in (estructura.recorrer() if estructura is self.inscritos
                      else estructura.a_lista()):
                if vistos.buscar(lambda i: i == e['id'])[0] >= 0:
                    duplicados.append(e['id'])
                else:
                    vistos.insertar(e['id'])
        return duplicados

    def _devolver_a_cola(self, estudiante, origen):
        """Reinserta al frente de la cola de origen (para DESHACER)."""
        if origen == 'prio':
            self.cola_prioridad.insertar_al_frente(estudiante, estudiante.get('p', 1))
        elif origen == 'circ':
            self.cola_circular.insertar_al_frente(estudiante)
        else:
            self.cola_simple.insertar_al_frente(estudiante)

    # ==================================================================
    # Módulo de inscripciones
    # ==================================================================
    def configurar_curso(self, nombre, cupos):
        """Cambia nombre y cupos. Si suben los cupos, reasigna a quienes esperan."""
        if not _es_entero(cupos) or cupos < 0:
            return False, "Los cupos deben ser un entero >= 0"
        nombre = (nombre or '').strip() or self.curso
        self.curso, self.cupos = nombre, cupos
        extra = ""
        if self.inscritos.size() > cupos:
            extra = (f" (aviso: hay {self.inscritos.size()} inscritos, "
                     f"más que los cupos; no se expulsa a nadie)")
        reasignados = self._reasignar_cupos_libres()
        if reasignados:
            extra += f" Se reasignaron {reasignados} estudiante(s) desde las esperas."
        return True, f"Curso '{nombre}' con {cupos} cupos.{extra}"

    def llegada_estudiante(self, id_, nombre, prioridad=None, correo=''):
        """Registra la llegada. Retorna (ok, mensaje)."""
        if not _es_entero(id_) or id_ <= 0:
            return False, "El ID debe ser un entero positivo"
        nombre = (nombre or '').strip()
        if not nombre:
            return False, "El nombre no puede estar vacío"
        if prioridad is not None and (not _es_entero(prioridad) or
                                      not PRIORIDAD_MIN <= prioridad <= PRIORIDAD_MAX):
            return False, f"La prioridad debe estar entre {PRIORIDAD_MIN} y {PRIORIDAD_MAX}"
        if self._existe_id(id_):
            return False, "ID ya existe en el sistema"

        est = {'id': id_, 'nombre': nombre, 'correo': (correo or '').strip(),
               'cod_curso': self.curso}
        if prioridad is None:
            self.cola_simple.enqueue(est)
            return True, "Estudiante agregado a la cola simple"
        self.cola_prioridad.enqueue(est, prioridad)
        return True, f"Estudiante agregado a la cola de prioridad (p={prioridad})"

    def procesar_turnos(self, n):
        """Procesa hasta n turnos. Retorna cuántos se procesaron."""
        procesados = 0
        for _ in range(max(0, n)):
            if self.hay_cupo():
                if not self.cola_prioridad.is_empty():
                    est, origen = self.cola_prioridad.dequeue(), 'prio'
                elif not self.cola_circular.is_empty():
                    est, origen = self.cola_circular.dequeue(), 'circ'
                elif not self.cola_simple.is_empty():
                    est, origen = self.cola_simple.dequeue(), 'simple'
                else:
                    break
                self.inscritos.insertar(est)
                self.acciones.push({'tipo': 'INSCRIBIR', 'est': est, 'origen': origen})
            else:
                # Sin cupo: solo la cola simple "se mueve" a la espera circular.
                # Los prioritarios ya esperan (en orden de prioridad) en su cola.
                if self.cola_simple.is_empty():
                    break
                est = self.cola_simple.dequeue()
                self.cola_circular.enqueue(est)
                self.acciones.push({'tipo': 'ENVIAR_A_ESPERA', 'est': est})
            procesados += 1
        return procesados

    def _reasignar_cupos_libres(self):
        """Mientras haya cupo y alguien esperando: Prioridad primero, luego Circular."""
        reasignados = 0
        while self.hay_cupo():
            if not self.cola_prioridad.is_empty():
                est, desde = self.cola_prioridad.dequeue(), 'prio'
            elif not self.cola_circular.is_empty():
                est, desde = self.cola_circular.dequeue(), 'circ'
            else:
                break
            self.inscritos.insertar(est)
            self.acciones.push({'tipo': 'REASIGNAR', 'est': est, 'desde': desde})
            reasignados += 1
        return reasignados

    def retirar(self, id_):
        """Retira un inscrito, libera el cupo y reasigna. Retorna el estudiante o None."""
        est = self.inscritos.eliminar(lambda e: e['id'] == id_)
        if est is None:
            return None
        self.acciones.push({'tipo': 'RETIRAR', 'est': est})
        self._reasignar_cupos_libres()
        return est

    # ==================================================================
    # Módulo de historial académico (ListaDoble de semestres)
    # ==================================================================
    def buscar_semestre(self, anio, term):
        return self.historial.buscar(lambda s: s['anio'] == anio and s['term'] == term)

    def agregar_semestre(self, anio, term, materias=None):
        sem = semestre_valido({'anio': anio, 'term': term, 'materias': materias or []})
        if sem is None:
            return False, "Semestre inválido (año/término enteros positivos)"
        if self.buscar_semestre(anio, term):
            return False, "Ese semestre ya existe"
        self.historial.insertar_ordenado(sem, _clave_semestre)
        self.acciones.push({'tipo': 'AGREGAR_SEMESTRE', 'anio': anio, 'term': term})
        return True, "Semestre agregado"

    def agregar_materia(self, anio, term, cod, nombre, nota):
        sem = self.buscar_semestre(anio, term)
        if sem is None:
            return False, "No existe el semestre"
        cod = (cod or '').strip()
        if not cod:
            return False, "El código de la materia no puede estar vacío"
        if not (isinstance(nota, (int, float)) and not isinstance(nota, bool)
                and NOTA_MIN <= nota <= NOTA_MAX):
            return False, f"La nota debe estar entre {NOTA_MIN} y {NOTA_MAX}"
        if any(m['cod'] == cod for m in sem['materias']):
            return False, "La materia ya existe en ese semestre (use actualizar nota)"
        sem['materias'].append({'cod': cod, 'nombre': nombre, 'nota': nota})
        self.acciones.push({'tipo': 'AGREGAR_MATERIA', 'anio': anio, 'term': term,
                            'cod': cod})
        return True, "Materia agregada"

    def actualizar_nota(self, anio, term, cod, nota):
        sem = self.buscar_semestre(anio, term)
        if sem is None:
            return False, "No existe el semestre"
        if not (isinstance(nota, (int, float)) and not isinstance(nota, bool)
                and NOTA_MIN <= nota <= NOTA_MAX):
            return False, f"La nota debe estar entre {NOTA_MIN} y {NOTA_MAX}"
        for mat in sem['materias']:
            if mat['cod'] == cod:
                self.acciones.push({'tipo': 'ACTUALIZAR_NOTA', 'anio': anio,
                                    'term': term, 'cod': cod, 'nota_ant': mat['nota']})
                mat['nota'] = nota
                return True, "Nota actualizada"
        return False, "No existe esa materia en el semestre"

    # ==================================================================
    # Deshacer
    # ==================================================================
    def deshacer(self):
        """Revierte la última acción registrada. Retorna un mensaje."""
        if self.acciones.is_empty():
            return "Nada que deshacer"
        ac = self.acciones.pop()
        tipo = ac['tipo']

        if tipo == 'INSCRIBIR':
            est = ac['est']
            self.inscritos.eliminar(lambda e: e['id'] == est['id'])
            self._devolver_a_cola(est, ac['origen'])
            return f"Deshecho: INSCRIBIR de {est['nombre']}"

        if tipo == 'ENVIAR_A_ESPERA':
            est = self.cola_circular.quitar_ultimo()
            self.cola_simple.insertar_al_frente(est)
            return f"Deshecho: ENVIAR_A_ESPERA de {est['nombre']}"

        if tipo == 'REASIGNAR':
            est = ac['est']
            self.inscritos.eliminar(lambda e: e['id'] == est['id'])
            self._devolver_a_cola(est, ac['desde'])
            return f"Deshecho: REASIGNAR de {est['nombre']}"

        if tipo == 'RETIRAR':
            est = ac['est']
            if not self.hay_cupo():     # los cupos se redujeron después del retiro
                self.acciones.push(ac)
                return ("No se puede deshacer RETIRAR: ya no hay cupo "
                        "(se redujeron los cupos). La acción se conserva.")
            self.inscritos.insertar(est)
            return f"Deshecho: RETIRAR de {est['nombre']}"

        if tipo == 'AGREGAR_SEMESTRE':
            self.historial.eliminar(
                lambda s: s['anio'] == ac['anio'] and s['term'] == ac['term'])
            return f"Deshecho: AGREGAR_SEMESTRE {ac['anio']}-{ac['term']}"

        sem = self.buscar_semestre(ac['anio'], ac['term'])
        if sem is None:
            return "Semestre no encontrado (acción descartada)"

        if tipo == 'AGREGAR_MATERIA':
            sem['materias'] = [m for m in sem['materias'] if m['cod'] != ac['cod']]
            return f"Deshecho: AGREGAR_MATERIA {ac['cod']}"

        if tipo == 'ACTUALIZAR_NOTA':
            for mat in sem['materias']:
                if mat['cod'] == ac['cod']:
                    mat['nota'] = ac['nota_ant']
                    break
            return f"Deshecho: ACTUALIZAR_NOTA de {ac['cod']}"

        return "Acción desconocida (descartada)"

    # ==================================================================
    # Persistencia
    # ==================================================================
    def _ruta(self, parte):
        return os.path.join(self.dir_datos, ARCHIVOS[parte])

    def exportar(self, partes=PARTES):
        """Exporta las partes pedidas. Retorna lista de (ok, mensaje)."""
        informe = []
        for parte in partes:
            ruta = self._ruta(parte)
            try:
                if parte == 'inscritos':
                    exportar_inscritos(self.inscritos, ruta)
                elif parte == 'historial':
                    exportar_historial(self.historial, ruta)
                elif parte == 'esperas':
                    exportar_esperas(self.cola_circular, self.cola_prioridad, ruta)
                informe.append((True, f"{parte}: exportado a {ruta}"))
            except ErrorPersistencia as e:
                informe.append((False, f"{parte}: {e}"))
        return informe

    def importar(self, partes=PARTES):
        """Importa reconstruyendo las estructuras enlazadas.

        Cada parte es transaccional: se carga en estructuras temporales y solo si
        el archivo es válido reemplaza el estado actual (si falla, se conserva).
        Tras importar se depuran IDs duplicados entre estructuras.
        """
        informe, reemplazado = [], False

        if 'inscritos' in partes:
            nuevos = ListaSimple()
            try:
                imp, om = importar_inscritos(
                    nuevos, self._ruta('inscritos'),
                    rechazar=lambda r: nuevos.buscar(lambda e: e['id'] == r['id'])[0] >= 0)
                self.inscritos, reemplazado = nuevos, True
                informe.append((True, f"inscritos: {imp} importados, {om} omitidos"))
            except ErrorPersistencia as e:
                informe.append((False, f"inscritos: {e}. Se conserva el estado actual."))

        if 'esperas' in partes:
            circ, prio = ColaCircular(), ColaPrioridad()
            try:
                imp, om = importar_esperas(circ, prio, self._ruta('esperas'))
                self.cola_circular, self.cola_prioridad = circ, prio
                reemplazado = True
                informe.append((True, f"esperas: {imp} importados, {om} omitidos"))
            except ErrorPersistencia as e:
                informe.append((False, f"esperas: {e}. Se conserva el estado actual."))

        if 'historial' in partes:
            nuevo = ListaDoble()
            try:
                imp, om = importar_historial(nuevo, self._ruta('historial'))
                self.historial, reemplazado = nuevo, True
                informe.append((True, f"historial: {imp} semestres importados, {om} omitidos"))
            except ErrorPersistencia as e:
                informe.append((False, f"historial: {e}. Se conserva el estado actual."))

        if reemplazado:
            quitados = self._depurar_consistencia()
            if quitados:
                informe.append((True, f"consistencia: se eliminaron {quitados} ID(s) "
                                      f"repetidos de las colas"))
            if self.inscritos.size() > self.cupos:
                informe.append((False, f"aviso: hay {self.inscritos.size()} inscritos "
                                       f"y solo {self.cupos} cupos"))
            self.acciones = Pila()      # las acciones antiguas apuntan a estado previo
        return informe

    
    def _depurar_consistencia(self):
        """Quita de las colas los IDs ya presentes en inscritos o en una cola previa.
        Prioridad de conservación: inscritos > prioridad > circular > simple.

        Nota: `a_lista()` devuelve referencias a los dicts almacenados en los nodos,
        por lo que `x is e` identifica con precisión la instancia a eliminar. Esto
        importa si una cola importada trae IDs duplicados: se conserva la primera
        ocurrencia, no la primera que coincida por id.
        """
        vistos = ListaSimple()
        for e in self.inscritos.recorrer():
            vistos.insertar(e['id'])
        quitados = 0
        for cola in (self.cola_prioridad, self.cola_circular, self.cola_simple):
            for e in cola.a_lista():
                if vistos.buscar(lambda i: i == e['id'])[0] >= 0:
                    cola.eliminar(lambda x: x is e)
                    quitados += 1
                else:
                    vistos.insertar(e['id'])
        return quitados