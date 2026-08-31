"""Application errors translated into HTTP responses by the interface."""


class EmailAlreadyRegistered(Exception):
    pass


class InvalidCredentials(Exception):
    pass


class InvalidToken(Exception):
    pass


class TaskNotFound(Exception):
    pass


class InvalidInput(Exception):
    pass


class InvalidTaskUpdate(InvalidInput):
    pass
