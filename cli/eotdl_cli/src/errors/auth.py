class LoginError(Exception):
    def __init__(self, message='Login Error'):
        self.message = message
        super().__init__(self.message)

class AuthTimeOut(Exception):
    def __init__(self, message='Authentication timed out'):
        self.message = message
        super().__init__(self.message)