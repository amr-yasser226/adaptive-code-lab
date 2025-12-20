from datetime import datetime

class Draft:
    def __init__(self, id, user_id, assignment_id, content, language='python', saved_at=None):
        self.__id = id
        self.__user_id = user_id
        self.__assignment_id = assignment_id
        self.content = content
        self.language = language
        self.saved_at = saved_at

    def get_id(self):
        return self.__id

    def get_user_id(self):
        return self.__user_id

    def get_assignment_id(self):
        return self.__assignment_id

    def to_dict(self):
        return {
            'id': self.get_id(),
            'user_id': self.get_user_id(),
            'assignment_id': self.get_assignment_id(),
            'content': self.content,
            'language': self.language,
            'saved_at': self.saved_at.isoformat() if hasattr(self.saved_at, 'isoformat') else self.saved_at
        }
