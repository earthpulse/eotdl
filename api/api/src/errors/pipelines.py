class PipelineDoesNotExistError(Exception):
    message = "Pipeline doesn't exist"

    def __init__(self):
        super().__init__(self.message)


class PipelineAlreadyExistsError(Exception):
    message = "Pipeline already exists"

    def __init__(self):
        super().__init__(self.message)


class PipelineVersionDoesNotExistError(Exception):
    message = "Pipeline version doesn't exist"

    def __init__(self):
        super().__init__(self.message)


class PipelineNotActiveError(Exception):
    message = "Requested Pipeline(s) not active"

    def __init__(self):
        super().__init__(self.message)
