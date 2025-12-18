from datetime import datetime

class Draft:
    def __init__(self, id, user_id, assignment_id, content, metadata, version, created_at, updated_at):
        self.__id = id
        self.__user_id = user_id
        self.__assignment_id = assignment_id
        self.content = content
        self.metadata = metadata
        self.version = version
        self.created_at = created_at
        self.updated_at = updated_at

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
            'metadata': self.metadata,
            'version': self.version,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
