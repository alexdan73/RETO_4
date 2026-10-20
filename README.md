# SIGA – Sistema Integral de Gestión Académica (Reto 4)

Integra **pilas, colas y listas enlazadas implementadas desde cero** (sin `list`/`deque` como
contenedor base) en un sistema de inscripciones, historial académico, deshacer, persistencia,
pruebas y análisis de eficiencia.

## Cómo ejecutar

```bash
python src/app.py                          # aplicación CLI (menú 1-11)
python -m unittest discover -s tests -v    # 93 pruebas unitarias
python src/benchmarks.py                   # tabla de eficiencia (también opción 10 del menú)
```
Solo requiere Python 3.8+ y la biblioteca estándar. Los archivos se guardan en `data/`
(ruta absoluta respecto al proyecto, no depende del directorio desde el que se ejecute).

## Estructura

```
src/
  nodo_simple.py  nodo_doble.py            NodoSimple / NodoDoble
  pila.py                                  Pila (push, pop, peek, is_empty, size)
  cola_simple.py  cola_circular.py         ColaSimple / ColaCircular
  cola_prioridad.py                        ColaPrioridad (5 niveles, FIFO por nivel)
  lista_simple.py lista_doble.py           ListaSimple (inscritos) / ListaDoble (historial)
  siga.py                                  Lógica del sistema (clase SIGA, sin consola)
  persistencia_csv.py persistencia_json.py Exportar/importar + validación
  errores.py                               ErrorPersistencia
  benchmarks.py                            Medición con time.perf_counter
  app.py                                   Interfaz CLI
tests/   test_pila, test_colas, test_listas, test_siga, test_persistencia, test_benchmarks
data/    inscritos.csv, historial.json, esperas.json (ejemplo generado por el sistema)
```

## Reglas del sistema (decisiones de diseño)

| Situación | Comportamiento |
|---|---|
| Llegada sin prioridad | `ColaSimple` (orden de llegada) |
| Llegada con prioridad 1–5 | `ColaPrioridad` (5 = crítico). Fuera de rango → se rechaza |
| Turno con cupo | Se inscribe en `ListaSimple`. Orden: Prioridad → Circular → Simple |
| Turno sin cupo | El de la cola simple pasa a `ColaCircular`. Los prioritarios **siguen esperando en `ColaPrioridad`** (conservan su prioridad) |
| Retiro | Libera cupo y reasigna: primero `ColaPrioridad`, si está vacía `ColaCircular` |
| Consistencia | Un ID nunca está en dos estructuras a la vez (se valida al llegar e importar) |
| Deshacer | `Pila` de acciones: INSCRIBIR, ENVIAR_A_ESPERA, REASIGNAR, RETIRAR, ACTUALIZAR_NOTA, AGREGAR_SEMESTRE, AGREGAR_MATERIA |

Un retiro con reasignación genera **dos** acciones (RETIRAR y REASIGNAR): se deshacen con dos
pulsaciones de "Deshacer", en orden inverso.

Persistencia: cada archivo se importa de forma **transaccional** (si está corrupto o no existe,
se conserva el estado actual) y las filas inválidas se omiten contando cuántas fueron. Al importar
se vacía la pila de acciones. La cola simple no se persiste (no lo exige el enunciado); si algún
ID importado coincide con alguien en ella, se retira de la cola simple.

## Guía de defensa – casos de prueba mínimos (para el video)

Cupos = 2 en todos los casos (opción 1).

1. **Saturación** → llegan 4 estudiantes (opción 2), opción 3 con N=4, opción 6: dos inscritos y dos en la circular.
2. **Prioritarios** → llega un estudiante con prioridad 5 junto a los de la cola simple; en opción 3 se inscribe antes.
3. **Retiros** → con alguien en Prioridad y alguien en Circular, opción 4: entra primero el de Prioridad.
4. **Deshacer** → partir del escenario del caso 3 (dos inscritos, dos en circular, un
   retiro ya hecho) y pulsar opción 8 cuatro veces: revierte REASIGNAR → RETIRAR →
   ENVIAR_A_ESPERA → INSCRIBIR (mostrar colas entre cada paso).
5. **Historial** → opción 7: agregar semestres desordenados (2024-2, 2023-1, 2024-1), recorrer adelante/atrás, buscar.
6. **Persistencia** → opción 9→1 (exportar), reiniciar la app, opción 9→2 (importar), opción 5 y 6 para ver los datos reconstruidos. *(Nota: si `data/` está vacío, el import fallará con "Archivo no encontrado" — comportamiento correcto; exportar antes de reiniciar.)*
7. **Eficiencia** → opción 10.

Casos límite cubiertos en `tests/`: cupos = 0, múltiples prioritarios, retiros masivos, historial
vacío, IDs duplicados, importaciones corruptas (JSON roto, CSV sin encabezado, tipos inválidos,
archivo no UTF-8, archivos inexistentes), subir/bajar cupos.

## Análisis de eficiencia

`python src/benchmarks.py` imprime la tabla (promedio de 5 ejecuciones, solo se cronometra la
operación, no la preparación) y los insights calculados con los datos medidos.
