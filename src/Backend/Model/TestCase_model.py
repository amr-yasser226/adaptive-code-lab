class Testcase : 
    def __init__(self, id , assignment_id , name  , stdin,description  , expected_output , timeoutms ,memory_limit_mb, points, is_visible , sortorder, created_at):
        self.__id = id
        self.__assignment_id = assignment_id
        self.name = name
        self.stdin = stdin
        self.description = description
        self.expected_output = expected_output
        self.timeoutms = timeoutms
        self.memory_limit_mb = memory_limit_mb
        self.points = points
        self.is_visible = bool(is_visible)
        self.sortorder = sortorder
        self.created_at = created_at
    def get_id(self): 
        return self.__id
    def get_assignment_id(self): 
        return self.__assignment_id
    def run_on(submission_id): 
        pass
    def validate(): 
        pass
    def clone(): 
        pass