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

    # def run_on(self, submission_id):
    #     pass

    # def validate(self):
    #     pass

    # def clone(self):
    #     pass
