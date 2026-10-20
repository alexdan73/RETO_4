"""Exportar/Importar historial y esperas en JSON, reconstruyendo las estructuras."""
import json
import os

from errores import ErrorPersistencia

PRIORIDAD_MIN, PRIORIDAD_MAX = 1, 5
NOTA_MIN, NOTA_MAX = 0, 20

def _asegurar_directorio(ruta):
    carpeta = os.path.dirname(ruta)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)


def _guardar_json(ruta, datos):
    tmp = ruta + ".tmp"
    try:
        _asegurar_directorio(ruta)
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
        os.replace(tmp, ruta)
    except (OSError, TypeError) as e:
        raise ErrorPersistencia(f"No se pudo exportar a {ruta}: {e}") from e


def _cargar_json(ruta):
    """Lee el JSON y valida que sea un objeto. Lanza ErrorPersistencia si falla."""
    if not os.path.exists(ruta):
        raise ErrorPersistencia(f"Archivo no encontrado: {ruta}")
    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            datos = json.load(f)
    except json.JSONDecodeError as e:
        raise ErrorPersistencia(f"JSON corrupto en {ruta}: {e}") from e
    except (OSError, UnicodeDecodeError) as e:
        raise ErrorPersistencia(f"Error leyendo {ruta}: {e}") from e
    if not isinstance(datos, dict):
        raise ErrorPersistencia(f"Formato inválido en {ruta}: se esperaba un objeto")
    return datos


def _es_entero(x):
    return isinstance(x, int) and not isinstance(x, bool)


def _es_numero(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


# ----------------------------------------------------------------------
# Historial
# ----------------------------------------------------------------------
def exportar_historial(lista_doble, ruta):
    _guardar_json(ruta, {'semestres': lista_doble.recorrer_adelante()})


def semestre_valido(sem):
    """Normaliza un semestre o devuelve None si es inválido."""
    if not isinstance(sem, dict):
        return None
    anio, term = sem.get('anio'), sem.get('term')
    if not _es_entero(anio) or not _es_entero(term) or anio <= 0 or term <= 0:
        return None
    materias_in = sem.get('materias', [])
    if not isinstance(materias_in, list):
        return None
    materias = []
    for m in materias_in:
        if (not isinstance(m, dict) or not isinstance(m.get('cod'), str)
                or not m['cod'].strip() or not _es_numero(m.get('nota'))
                or not NOTA_MIN <= m['nota'] <= NOTA_MAX):     # ← validación añadida
            return None
        materias.append({'cod': m['cod'].strip(),
                         'nombre': str(m.get('nombre', '')),
                         'nota': m['nota']})
    return {'anio': anio, 'term': term, 'materias': materias}

def importar_historial(lista_doble, ruta):
    """Carga semestres ordenados. Retorna (importados, omitidos)."""
    datos = _cargar_json(ruta)
    semestres = datos.get('semestres')
    if not isinstance(semestres, list):
        raise ErrorPersistencia(f"{ruta}: falta la lista 'semestres'")
    importados = omitidos = 0
    for sem in semestres:
        norm = semestre_valido(sem)
        if norm is None or lista_doble.buscar(
                lambda s: s['anio'] == norm['anio'] and s['term'] == norm['term']):
            omitidos += 1
            continue
        lista_doble.insertar_ordenado(norm, lambda s: (s['anio'], s['term']))
        importados += 1
    return importados, omitidos


# ----------------------------------------------------------------------
# Esperas (circular + prioridad)
# ----------------------------------------------------------------------
def exportar_esperas(circular, prioridad, ruta):
    _guardar_json(ruta, {'circular': circular.a_lista(),
                         'prioridad': prioridad.a_lista()})


def _estudiante_valido(e):
    if not isinstance(e, dict) or not _es_entero(e.get('id')) or e['id'] <= 0:
        return None
    nombre = e.get('nombre')
    if not isinstance(nombre, str) or not nombre.strip():
        return None
    return {'id': e['id'], 'nombre': nombre.strip(),
            'correo': str(e.get('correo', '') or ''),
            'cod_curso': str(e.get('cod_curso', '') or '')}


def importar_esperas(circular, prioridad, ruta):
    """Carga las colas de espera. Retorna (importados, omitidos)."""
    datos = _cargar_json(ruta)
    if not isinstance(datos.get('circular', []), list) or \
            not isinstance(datos.get('prioridad', []), list):
        raise ErrorPersistencia(f"{ruta}: 'circular' y 'prioridad' deben ser listas")
    if 'circular' not in datos and 'prioridad' not in datos:
        raise ErrorPersistencia(f"{ruta}: faltan las claves 'circular'/'prioridad'")
    importados = omitidos = 0
    for e in datos.get('circular', []):
        est = _estudiante_valido(e)
        if est is None:
            omitidos += 1
            continue
        circular.enqueue(est)
        importados += 1
    for e in datos.get('prioridad', []):
        est = _estudiante_valido(e)
        p = e.get('p') if isinstance(e, dict) else None
        if est is None or not _es_entero(p) or not PRIORIDAD_MIN <= p <= PRIORIDAD_MAX:
            omitidos += 1
            continue
        prioridad.enqueue(est, p)
        importados += 1
    return importados, omitidos
