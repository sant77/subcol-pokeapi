class ValidationError(Exception):
    """Errores por mala entrada del usuario."""
    pass

class NotFoundError(Exception):
    """Errores cuando la data no existe (e.g. Pokémon no existe)."""
    pass
