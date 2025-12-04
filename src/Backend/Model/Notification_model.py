class Notification:
    Allowed_Types = ('info', 'warning', 'alert')
    def __init__(self,id,user_id,message,type,is_read=False,created_at=None,read_at=None,link=None):
        if type not in Notification.Allowed_Types:
            raise ValueError(f"Invalid notification type: {type}. Allowed types are: {Notification.Allowed_Types}")
        self.__id = id
        self.__user_id = user_id
        self.message = message
        self.type = type
        self.is_read = bool(is_read)
        self.created_at = created_at
        self.read_at = read_at
        self.link = link
    def get_id(self):
        return self.__id
    def get_user_id(self):
        return self.__user_id
    def mark_as_read(self, read_at):
        self.is_read = True
        self.read_at = read_at
    def mark_as_unread(self):
        self.is_read = False
        self.read_at = None
    def delete_notification(self):
        pass