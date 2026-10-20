"""Excepciones propias del proyecto."""


class ErrorPersistencia(Exception):
    """Fallo a nivel de archivo: no existe, ilegible, corrupto o con formato inválido."""
