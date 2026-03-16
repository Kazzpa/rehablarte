"""
File containing custom exceptions for the bot.
"""


# Exception for general use (internal/unkown error)
class RehablarteInternalException(Exception):
    def __init__(self, message, field: str = None):
        super().__init__(message)
        self.field = field


# Exception to capture errors in the RAE API
class RehablarteApiRaeException(Exception):
    def __init__(self, message, status_code: str = None, url_origin: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.url_origin = url_origin


# Exception for menu/keyboard errors
class MenukeyboardException(Exception):
    def __init__(self, message, menu_name: str = None):
        super().__init__(message)
        self.menu_name = menu_name


# Exception to capture mappings errors
class ReHablarteMappingException(Exception):
    def __init__(self, message, field: str = None):
        super().__init__(message)
        self.field = field
