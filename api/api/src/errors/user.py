class UserUnauthorizedError(Exception):
    message = "You are not authorized to perform this action"

    def __init__(self):
        super().__init__(self.message)

class NoAccessToPrivateError(Exception):
    message = "NoAccessToPrivateError"

    def __init__(self):
        super().__init__(self.message)

class TierLimitError(Exception):
    def __init__(self, message):
        super().__init__(message)


class UserDoesNotExistError(Exception):
    def __init__(self):
        super().__init__("User does not exist")


class UserAlreadyExistsError(Exception):
    def __init__(self):
        super().__init__("User already exists")


class InvalidApiKey(Exception):
    def __init__(self):
        super().__init__("Invalid API key")
