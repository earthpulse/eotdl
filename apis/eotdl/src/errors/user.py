class UserUnauthorizedError(Exception):
    message = "You are not authorized to perform this action"

    def __init__(self):
        super().__init__(self.message)