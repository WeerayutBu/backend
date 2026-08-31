"""Application errors translated into HTTP responses by the routers."""


class EmailAlreadyRegistered(Exception):
    pass


class InvalidCredentials(Exception):
    pass


class InvalidToken(Exception):
    pass


class TaskNotFound(Exception):
    pass


class InvalidTaskUpdate(Exception):
    pass
