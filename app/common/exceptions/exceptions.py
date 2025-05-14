class NotFoundException(Exception):
    def __init__(self, message: str):
        self.message = message


class DatabaseException(Exception):
    def __init__(self, message: str):
        self.message = message
