"""SIGA - Interfaz de consola (CLI). Ejecutar:  python src/app.py"""
from siga import SIGA, PARTES


def _fmt_est(e):
    p = f" (p={e['p']})" if 'p' in e else ""
    return f"{e['nombre']}[{e['id']}]{p}"


def _fmt_sem(s):
    mats = ", ".join(f"{m['cod']}:{m['nota']}" for m in s['materias']) or "sin materias"
    return f"{s['anio']}-{s['term']}  [{mats}]"


def _leer_entero(texto):
    return int(input(texto).strip())


def _leer_nota(texto):
    return float(input(texto).strip().replace(',', '.'))


def _mostrar_informe(informe):
    for ok, msg in informe:
        print(f"  {'✓' if ok else '⚠'} {msg}")


# ----------------------------------------------------------------------
def mostrar_inscritos(siga):
    datos = siga.inscritos.recorrer()
    print(f"\nInscritos en '{siga.curso}' ({len(datos)}/{siga.cupos}):")
    if not datos:
        print("  (vacío)")
    for e in datos:
        print(f"  - ID {e['id']} | {e['nombre']} | {e.get('correo', '')}")


def mostrar_colas(siga):
    print()
    siga.cola_simple.mostrar(_fmt_est)
    siga.cola_prioridad.mostrar(_fmt_est)
    siga.cola_circular.mostrar(_fmt_est)


def menu_historial(siga):
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
            return
        try:
            if op == '1':
                ok, msg = siga.agregar_semestre(_leer_entero("Año: "), _leer_entero("Término: "))
            elif op == '2':
                anio, term = _leer_entero("Año: "), _leer_entero("Término: ")
                cod, nombre = input("Código materia: "), input("Nombre materia: ")
                ok, msg = siga.agregar_materia(anio, term, cod, nombre, _leer_nota("Nota: "))
            elif op == '3':
                anio, term = _leer_entero("Año: "), _leer_entero("Término: ")
                cod = input("Código materia: ").strip()
                ok, msg = siga.actualizar_nota(anio, term, cod, _leer_nota("Nueva nota: "))
            elif op in ('4', '5'):
                datos = (siga.historial.recorrer_adelante() if op == '4'
                         else siga.historial.recorrer_atras())
                print("  (historial vacío)" if not datos else "")
                for s in datos:
                    print(f"  {_fmt_sem(s)}")
                continue
            elif op == '6':
                s = siga.buscar_semestre(_leer_entero("Año: "), _leer_entero("Término: "))
                print(f"  {_fmt_sem(s)}" if s else "  ✗ No encontrado")
                continue
            else:
                print("  ✗ Opción no válida")
                continue
            print(f"  {'✓' if ok else '✗'} {msg}")
        except ValueError:
            print("  ✗ Entrada inválida")


def menu_persistencia(siga):
    print("\n--- Persistencia ---")
    print("1. Exportar todo (CSV + JSON)")
    print("2. Importar todo (CSV + JSON)")
    print("3. Exportar solo CSV (inscritos)")
    print("4. Exportar solo JSON (historial + esperas)")
    print("5. Importar solo CSV (inscritos)")
    print("6. Importar solo JSON (historial + esperas)")
    print("0. Volver")
    op = input("Opción: ").strip()
    acciones = {'1': ('e', PARTES), '2': ('i', PARTES),
                '3': ('e', ('inscritos',)), '4': ('e', ('esperas', 'historial')),
                '5': ('i', ('inscritos',)), '6': ('i', ('esperas', 'historial'))}
    if op == '0':
        return
    if op not in acciones:
        print("  ✗ Opción no válida")
        return
    modo, partes = acciones[op]
    _mostrar_informe(siga.exportar(partes) if modo == 'e' else siga.importar(partes))


def main():
    siga = SIGA()
    while True:
        print("\n=========== SIGA ===========")
        print("1.  Configurar curso")
        print("2.  Llegada de estudiante")
        print("3.  Procesar N turnos")
        print("4.  Retirar estudiante inscrito")
        print("5.  Mostrar inscritos")
        print("6.  Mostrar todas las colas")
        print("7.  Historial académico")
        print("8.  Deshacer última acción")
        print("9.  Persistencia (export/import)")
        print("10. Benchmarks")
        print("11. Salir")
        try:
            op = input("Opción: ").strip()
        except EOFError:
            print()
            break

        try:
            if op == '1':
                nombre = input("Nombre del curso: ")
                ok, msg = siga.configurar_curso(nombre, _leer_entero("Cupos: "))
                print(f"  {'✓' if ok else '✗'} {msg}")
            elif op == '2':
                id_ = _leer_entero("ID: ")
                nombre = input("Nombre: ")
                p_txt = input("Prioridad (1-5, vacío = normal): ").strip()
                prioridad = int(p_txt) if p_txt else None
                correo = input("Correo (opcional): ")
                ok, msg = siga.llegada_estudiante(id_, nombre, prioridad, correo)
                print(f"  {'✓' if ok else '✗'} {msg}")
            elif op == '3':
                n = _leer_entero("Cuántos turnos: ")
                if n <= 0:
                    print("  ✗ N debe ser mayor que 0")
                else:
                    print(f"  Procesados: {siga.procesar_turnos(n)}")
            elif op == '4':
                est = siga.retirar(_leer_entero("ID a retirar: "))
                print(f"  ✓ Retirado {est['nombre']}" if est else "  ✗ No hay un inscrito con ese ID")
            elif op == '5':
                mostrar_inscritos(siga)
            elif op == '6':
                mostrar_colas(siga)
            elif op == '7':
                menu_historial(siga)
            elif op == '8':
                print(f"  {siga.deshacer()}")
            elif op == '9':
                menu_persistencia(siga)
            elif op == '10':
                from benchmarks import run_benchmarks
                run_benchmarks()
            elif op == '11':
                print("¡Hasta luego!")
                break
            else:
                print("  ✗ Opción no válida (elija 1-11)")
        except ValueError:
            print("  ✗ Entrada inválida")
        except EOFError:
            break


if __name__ == "__main__":
    main()
