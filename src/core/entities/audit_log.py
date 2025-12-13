class AuditLog:
    def __init__(self, id, actor_user_ID, action, entityType=None,entity_Id=None,details=None , ip_address=None, userAgent=None,created_at=None):
        self.__id = id
        self.__actor_user_ID = actor_user_ID
        self.action = action
        self.entityType = entityType
        self.entity_Id = entity_Id
        self.details = details
        self.ip_address = ip_address
        self.userAgent = userAgent
        self.created_at = created_at 

    def get_id(self):
        return self.__id
    def get_actor_user_ID(self):
        return self.__actor_user_ID
    def getActor(self) :  #return User object
        pass
    def get_Entity(self): #return Entity object
        pass  
    