class AuthError(Exception):
    """
    Custom authentication/authorization error.

    Attributes:
        message (str): Human-readable explanation of the error.
        code (str): Error identifier (e.g. 'invalid_credentials', 'not_authorized').
        status (int): Optional HTTP status code (useful for web frameworks).
    """

    def __init__(self, message="Authentication error", code="auth_error", status=401):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status = status

    def __str__(self):
        return f"[{self.code}] {self.message}"

    def to_dict(self):
        """
        Returns the error details in dict form.
        Useful if you ever return errors in JSON.
        """
        return {
            "error": self.code,
            "message": self.message,
            "status": self.status
        }
