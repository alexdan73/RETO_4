"""Exportar/Importar inscritos en CSV. Módulo defensivo y autocontenido."""
import csv
import os

FIELDS = ['id', 'nombre', 'correo', 'cod_curso']


def _save_dir(path):
    dir_ = os.path.dirname(path)
    if dir_:
        os.makedirs(dir_, exist_ok=True)


def export_register(simple_list, path):
    """Exporta inscritos a CSV. Crea el directorio si hace falta.
    Retorna True si tuvo éxito, False si hubo error."""
    try:
        _save_dir(path)
        with open(path, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            for e in simple_list.a_list():        # FIX: era traverse()
                w.writerow({k: e.get(k, '') for k in FIELDS})
        return True
    except (OSError, IOError) as e:
        print(f"  ⚠ No se pudo exportar a {path}: {e}")
        return False


def import_register(simple_list, path):
    if not os.path.exists(path):
        print(f"  ⚠ Archivo no encontrado: {path} (se omite)")
        return 0
    imports = 0
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line_num, row in enumerate(csv.DictReader(f), start=2):
                try:
                    row['id'] = int(row['id'])
                    simple_list.insert(row)
                    imports += 1
                except (ValueError, KeyError, TypeError) as e:
                    print(f"  ⚠ Fila {line_num} corrupta, se omite: {e}")
    except (OSError, IOError) as e:
        print(f"  ⚠ Error leyendo {path}: {e}")
    return imports