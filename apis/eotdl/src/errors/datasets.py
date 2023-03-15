class DatasetAlreadyExistsError(Exception):
    message = "Dataset already exists"
    def __init__(self):
        super().__init__(self.message)


class DatasetDoesNotExistError(Exception):
    message = "Dataset doesn't exist"
    def __init__(self):
        super().__init__(self.message)

class NameCharsValidationError(Exception):
    message = "Use only alphanumeric characters and hypens (-). Names cannot start with numbers. Whitespaces are not allowed."
    def __init__(self):
        super().__init__(self.message)

class NameLengthValidationError(Exception):
    def __init__(self, max_len, min_len):
        message = f'Name must be less than {max_len} characters, and more than {min_len}'
        super().__init__(message)

class DescriptionLengthValidationError(Exception):
    def __init__(self, max_len, min_len):
        message = f'Description must be less than {max_len} characters, and more than {min_len}'
        super().__init__(message)