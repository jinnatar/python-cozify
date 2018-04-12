class APIError(Exception):
    """Error raised for non-200 API return codes

    Args:
        status_code(int): HTTP status code returned by the API
        message(str): Potential error message returned by the API
    
    Attributes:
        status_code(int): HTTP status code returned by the API
        message(str): Potential error message returned by the API
    """

    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return 'API error, %s: %s' % (self.status_code, self.message)

class AuthenticationError(Exception):
    """Error raised for nonrecoverable authentication failures.

    Args:
        message(str): Human readable error description
    
    Attributes:
        message(str): Human readable error description
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'Authentication error: %s' % self.message
