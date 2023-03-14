class DatasetAlreadyExistsError(Exception):
    message = "Dataset already exists"

    def __init__(self):
        super().__init__(self.message)


class DatasetDoesNotExistError(Exception):
    message = "Dataset doesn't exist"

    def __init__(self):
        super().__init__(self.message)
