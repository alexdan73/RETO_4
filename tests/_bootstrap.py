"""Añade /src al sys.path para que los tests puedan importar los módulos.

Este módulo debe importarse ANTES que cualquier clase del proyecto.
Basta con `import _bootstrap` al inicio de cada archivo de test.
"""
import os
import sys

_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)