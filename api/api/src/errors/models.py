class ModelDoesNotExistError(Exception):
    message = "Model doesn't exist"

    def __init__(self):
        super().__init__(self.message)


class ModelAlreadyExistsError(Exception):
    message = "Model already exists"

    def __init__(self):
        super().__init__(self.message)
