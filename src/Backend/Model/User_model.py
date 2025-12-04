import hashlib
class User:
    def __init__(self, id ,name,email,password,role,created_at=None,updated_at=None,is_Active=True):
        self.__id = id
        self.name = name
        self.email = email
        self.__password_hash = password
        self.role = role
        self.created_at = created_at
        self.updated_at = updated_at
        self._is_Active = bool(is_Active)

    def get_id(self):
        return self.__id
    @staticmethod # static method to hash password
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    def set_password(self, password):
        self.__password_hash = User.hash_password(password)
    def get_password_hash(self):
        return self.__password_hash
    def authenticate_password(self, password):
        return self.get_password_hash() == User.hash_password(password)
    def Update_profile(self, name=None, email=None ,role=None,password=None):
        if name:
            self.name = name
        if email:
            self.email = email
        if role:
            self.role = role
        if password:
            self.set_password(password)

    def Deactivate_account(self):
        self.is_Active = False
    def Activate_account(self):
        self.is_Active = True
        
    
    
    
   
    
    

    

