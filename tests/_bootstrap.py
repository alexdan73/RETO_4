"""Añade /src al sys.path para que los tests importen los módulos del proyecto.
Se importa con `import _bootstrap` ANTES que cualquier clase del proyecto."""
import os
import sys

_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
