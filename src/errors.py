class UnauthorizedException(Exception):
    def __init__(self, message):
        self.name = "UnauthorizedException"
        self.message = message

    def __str__(self):
        return f"{self.name}: {self.message}"


class EnvironmentException(Exception):
    def __init__(self, message):
        self.name = "EnvironmentException"
        self.message = message

    def __str__(self):
        return f"{self.name}: {self.message}"