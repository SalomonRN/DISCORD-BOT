class UserNotFound(Exception):
    def __init__(self, mensaje="El usuario no existe en la base de datos"):
        super().__init__(mensaje)

class UserAlreadyExists(Exception):
    def __init__(self, mensaje="El usuario ya existe en la base de datos"):
        super().__init__(mensaje)
