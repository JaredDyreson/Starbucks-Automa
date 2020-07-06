class MessageException(Exception):
    def __init__(self, message):
        if(not (isinstance(message, str))):
            raise ValueError
        self.message = message


class EnviornmentException(MessageException):
    def __init__(self, message):
        super().__init__(message)

