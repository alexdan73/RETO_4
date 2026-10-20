"""Exportar/Importar inscritos en CSV. Módulo defensivo y autocontenido.

Valida precondiciones (directorio existente, archivo existente, filas
válidas) y captura OSError/ValueError sin detener el sistema.
"""

import csv
import os

FIELDS = ['id', 'nombre', 'correo', 'cod_curso']

def _save_dir(path):
    dir = os.path.dirname(path)
    if dir:
        os.makedirs(dir, exist_ok=True)

def export_register(simple_list, path):
    """Exporta inscritos a CSV. Crea el directorio si hace falta.
     Retorna True si tuvo éxito, False si hubo error.
    """
    try: 
        _save_dir(path)
        with open(path, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            for e in simple_list.traverse():
                w.writerow({k: e.get(k, '')for k in FIELDS})
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
            for _row, row in enumerate(csv.DictReader(f), start=2):
                try:
                    row['id'] = int(row['id'])
                    simple_list.insert(row)
                    imports += 1
                except (ValueError, KeyError, TypeError) as e:
                    print(f"  ⚠ Fila {_row} corrupta, se omite: {e}")
    except (OSError, IOError) as e:
        print(f"  ⚠ Error leyendo {path}: {e}")

    return imports


