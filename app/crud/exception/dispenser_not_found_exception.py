class DispenserNotFoundException(Exception):
    """Dispensador no encontrado en la base de datos."""

    def __init__(self, message):
        super().__init__(message)
