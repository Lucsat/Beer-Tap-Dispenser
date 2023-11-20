class DispenserAlreadyOpenedClosedException(Exception):
    """El dispensador ya se encuentra abierto o cerrado."""

    def __init__(self, message):
        super().__init__(message)
