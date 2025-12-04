class Result : 
    def __init__(self, id , submission_id ,test_case_id , passed ,stdout, stderr , runtime_ms , memory_kb , exit_code , error_message , created_at):
        self.__id = id
        self.__submission_id = submission_id
        self.__test_case_id = test_case_id
        self.passed = bool(passed)
        self.stdout = stdout
        self.stderr = stderr
        self.runtime_ms = runtime_ms
        self.memory_kb = memory_kb
        self.exit_code = exit_code
        self.error_message = error_message
        self.created_at = created_at
    def get_id(self):
            return self.__id
    def get_submission_id(self):
            return self.__submission_id
    def get_test_case_id(self):
            return self.__test_case_id
    def issuccessful(self):
            if self.passed and self.error_message is None:
                return True
            return False
    def get_detail(self):
            return {
                "id": self.__id,
                "submission_id": self.__submission_id,
                "test_case_id": self.__test_case_id,
                "passed": self.passed,
                "stdout": self.stdout,
                "stderr": self.stderr,
                "runtime_ms": self.runtime_ms,
                "memory_kb": self.memory_kb,
                "exit_code": self.exit_code,
                "error_message": self.error_message,
                "created_at": self.created_at
            }