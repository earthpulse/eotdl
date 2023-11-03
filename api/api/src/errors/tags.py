class InvalidTagError(Exception):
    message = "Invalid tag"

    def __init__(self):
        super().__init__(self.message)