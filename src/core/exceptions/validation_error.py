class ValidationError(Exception):

    def __init__(self, message="Invalid input", field=None, code="validation_error", status=400):
        super().__init__(message)
        self.message = message
        self.field = field
        self.code = code
        self.status = status

    def __str__(self):
        if self.field:
            return f"[{self.code}] {self.field}: {self.message}"
        return f"[{self.code}] {self.message}"

    def to_dict(self):
        return {
            "error": self.code,
            "message": self.message,
            "field": self.field,
            "status": self.status
        }
