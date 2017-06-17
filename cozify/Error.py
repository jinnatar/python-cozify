class APIError(Exception):
    """Error raised for non-200 API return codes"""
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message

    def __str__(self):
        """Return error string with API status code and possible error message."""
        return 'API error, %s: %s' % (self.status_code, self.message)

class AuthenticationError(Exception):
    """Error raised for nonrecoverable authentication failures."""
    def __init__(self, message):
        self.message = message

    def __str__(self):
        """Return error string with possible error message."""
        return 'Authentication error: %s' % self.message
