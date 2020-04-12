class EntityUnsupported(Exception):
    def __init__(self, app, name):
        message = f"Publishing entity {app}.{name} is not supported"
        super(EntityUnsupported, self).__init__(message)


class NoWorkersFound(Exception):
    def __init__(self):
        message = f"No workers found"
        super().__init__(message)


class UpdatingSoftDeletedException(Exception):
    def __init__(self):
        message = "It's not possible to save changes to a soft deleted model. Undelete it first."
        super().__init__(message)
