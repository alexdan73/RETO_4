"""Exportar/Importar historial y esperas en JSON. Módulo defensivo."""
import json
import os


def _save_dir(path):
    dir_ = os.path.dirname(path)
    if dir_:
        os.makedirs(dir_, exist_ok=True)


def _load_json(path):
    if not os.path.exists(path):
        print(f"  ⚠ Archivo no encontrado: {path} (se omite)")
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"  ⚠ JSON corrupto en {path}: {e} (se omite)")
        return None
    except (OSError, IOError) as e:
        print(f"  ⚠ Error leyendo {path}: {e}")
        return None


def export_history(double_list, path):
    try:
        _save_dir(path)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({'semestres': double_list.loop_forward()},   # FIX
                      f, indent=2, ensure_ascii=False)
        return True
    except (OSError, IOError) as e:
        print(f"  ⚠ No se pudo exportar a {path}: {e}")
        return False


def import_history(double_list, path):
    data = _load_json(path)
    if data is None:
        return 0
    if not isinstance(data, dict):
        print(f"  ⚠ Formato inválido en {path} (se esperaba un objeto)")
        return 0
    imports = 0
    for sem in data.get('semestres', []):
        if isinstance(sem, dict) and 'anio' in sem and 'term' in sem:
            sem.setdefault('materias', [])
            double_list.insert_sort(sem, lambda s: (s['anio'], s['term']))
            imports += 1
        else:
            print("  ⚠ Semestre inválido, se omite")
    return imports


def export_waits(circular, priority, path):
    try:
        _save_dir(path)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({
                'circular': circular.a_list(),
                'prioridad': priority.a_list()
            }, f, indent=2, ensure_ascii=False)
        return True
    except (OSError, IOError) as e:
        print(f"  ⚠ No se pudo exportar a {path}: {e}")
        return False


def import_waits(circular, priority, path):
    data = _load_json(path)
    if data is None:
        return 0
    if not isinstance(data, dict):
        print(f"  ⚠ Formato inválido en {path} (se esperaba un objeto)")
        return 0
    imports = 0
    for e in data.get('circular', []):
        if isinstance(e, dict) and 'id' in e:
            circular.enqueue(e)
            imports += 1
        else:
            print("  ⚠ Registro circular inválido, se omite")
    for e in data.get('prioridad', []):
        if isinstance(e, dict) and 'id' in e:
            priority.enqueue(e, e.get('p', 1))
            imports += 1
        else:
            print("  ⚠ Registro de prioridad inválido, se omite")
    return imports