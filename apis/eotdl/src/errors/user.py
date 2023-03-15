class UserUnauthorizedError(Exception):
    message = "You are not authorized to perform this action"

    def __init__(self):
        super().__init__(self.message)

class TierLimitError(Exception):
    def __init__(self, message):
        super().__init__(message)