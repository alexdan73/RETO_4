"""Exportar/Importar inscritos en CSV: id,nombre,correo,cod_curso.

- Errores de archivo (no existe, ilegible, sin encabezado válido) -> ErrorPersistencia.
- Errores de fila (id no numérico, nombre vacío, duplicado...) -> la fila se omite y se cuenta.
"""
import csv
import os

from errores import ErrorPersistencia

CAMPOS = ['id', 'nombre', 'correo', 'cod_curso']


def _asegurar_directorio(ruta):
    carpeta = os.path.dirname(ruta)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)


def exportar_inscritos(lista_simple, ruta):
    """Escribe los inscritos en CSV (escritura atómica: temporal + replace)."""
    tmp = ruta + ".tmp"
    try:
        _asegurar_directorio(ruta)
        with open(tmp, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=CAMPOS)
            w.writeheader()
            for e in lista_simple.recorrer():
                w.writerow({k: e.get(k, '') for k in CAMPOS})
        os.replace(tmp, ruta)
    except OSError as e:
        raise ErrorPersistencia(f"No se pudo exportar a {ruta}: {e}") from e


def _fila_valida(fila):
    """Devuelve el dict normalizado o None si la fila es inválida."""
    try:
        id_ = int((fila.get('id') or '').strip())
    except ValueError:
        return None
    nombre = (fila.get('nombre') or '').strip()
    if id_ <= 0 or not nombre:
        return None
    return {'id': id_, 'nombre': nombre,
            'correo': (fila.get('correo') or '').strip(),
            'cod_curso': (fila.get('cod_curso') or '').strip()}


def importar_inscritos(lista_simple, ruta, rechazar=None):
    """Carga inscritos en `lista_simple`. Retorna (importados, omitidos).

    rechazar: función opcional registro -> motivo (str) o None; permite al
    llamador vetar filas (p. ej. IDs duplicados).
    """
    if not os.path.exists(ruta):
        raise ErrorPersistencia(f"Archivo no encontrado: {ruta}")
    importados = omitidos = 0
    try:
        with open(ruta, 'r', newline='', encoding='utf-8') as f:
            lector = csv.DictReader(f)
            campos = lector.fieldnames or []
            if 'id' not in campos or 'nombre' not in campos:
                raise ErrorPersistencia(
                    f"{ruta}: encabezado inválido (se requiere al menos id,nombre)")
            for fila in lector:
                reg = _fila_valida(fila)
                if reg is None or (rechazar and rechazar(reg)):
                    omitidos += 1
                    continue
                lista_simple.insertar(reg)
                importados += 1
    except (OSError, UnicodeDecodeError, csv.Error) as e:
        raise ErrorPersistencia(f"Error leyendo {ruta}: {e}") from e
    return importados, omitidos
