class Testcase:
    def __init__(self, id, assignment_id, name, stdin, descripion, expected_out, timeout_ms, memory_limit_mb, points, is_visible, sort_order, created_at):
        self.__id = id
        self.__assignment_id = assignment_id
        self.name = name
        self.stdin = stdin
        self.descripion = descripion
        self.expected_out = expected_out
        self.timeout_ms = int(timeout_ms) if timeout_ms is not None else None
        self.memory_limit_mb = int(memory_limit_mb) if memory_limit_mb is not None else None
        self.points = points
        self.is_visible = bool(is_visible)
        self.sort_order = sort_order
        self.created_at = created_at

    def get_id(self):
        return self.__id

    def get_assignment_id(self):
        return self.__assignment_id

    def run_on(self, submission_id):
        raise NotImplementedError("Execution handled by sandbox service")

    def validate(self):
        if not self.name:
            raise ValueError("Test case name cannot be empty")
        if self.points < 0:
            raise ValueError("Points cannot be negative")
        return True

    def clone(self):
        return Testcase(
            id=None,
            assignment_id=self.__assignment_id,
            name=f"{self.name} (Copy)",
            stdin=self.stdin,
            descripion=self.descripion,
            expected_out=self.expected_out,
            timeout_ms=self.timeout_ms,
            memory_limit_mb=self.memory_limit_mb,
            points=self.points,
            is_visible=self.is_visible,
            sort_order=self.sort_order,
            created_at=self.created_at
        )
