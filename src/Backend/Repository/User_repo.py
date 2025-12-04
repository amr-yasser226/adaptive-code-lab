from Model.User_model import User 
from sqlalchemy.exc import SQLAlchemyError
class User_repo : 
    def __init__(self, db):
        self.db=db
    
    def get_by_id(self, id):
        query= f"SELECT * FROM users WHERE id ={id}"
        result = self.db.execute(query)
        row =result.fetchone()
        if row is None : 
            return None 
        return User(id=row[0], name=row[1], email=row[2],role=row[3],password=row[4],role=row[5],created_at=row[6], updated_at=row[7], is_Active=row[8])
    def get_by_email (self , email:str): 
        query = f"SELECT * FROM  users WHERE email={email}"
        result= self.db.execute(query)
        row = result.fetchone()
        if row is None : 
            return None 
        return User(id=row[0], name=row[1], email=row[2],role=row[3],password=row[4],role=row[5],created_at=row[6], updated_at=row[7], is_Active=row[8])
    def save_user(self ,user:User):
        try : 
            self.db.begin_tansaction()   

            if user.get_id() is None :
                query="""
                    INSERT INTO users(name,email, password_hash , role  , is_active )
                    VALUES (:name, :email, :password_hash, :role, :is_active)

                """
                result=self.db.execute(query,{
                    "name": user.name,
                    "email": user.email,
                    "password_hash": user.get_password_hash(),
                    "role": user.role,
                    "is_active": user._is_Active

                })

                new_id = result.fetchone()[0]
                self.db.commit()
                return self.get_by_id(new_id)
        except SQLAlchemyError : 
            self.db.rollback()
            raise
    
    
    def delete(self, id:int ): 
        try: 
            self.db.begin_transaction()
            query="DELETE FROM users WHERE id = :id "
            self.db.execute(query,{"id":id})
            self.db.commit()
        except SQLAlchemyError : 
            self.db.rollback()
            raise



    def findALL(self, filters:dict=None):
        base_query ="""
            SELECT * FROM users 
        """
        params={}
        if filters : 
            conditions =[]
            
        
            for key ,value in filters.items(): 
                conditions.append(f"{key} = :{key}")
                params[key] = value

            base_query += " WHERE " + " AND ".join(conditions)

        
            
        
        result = self.db.execute(base_query,params)
        users = []
        for row in result.fetchall():
             users.append(
                  User(
                    id=row.id,
                    name=row.name,
                    email=row.email,
                    password=row.password_hash,
                    role=row.role,
                    created_at=row.created_at,
                    updated_at=row.updated_at,
                    is_Active=row.is_active
                )
            )

        return users
    
    def Update_data(self, user:User):
        try:
            self.db.begin_transaction()
            query="""
            UPDATE users
            SET 
                name = :name,
                email = :email,
                password_hash = :password_hash,
                role = :role,
                is_active = :is_active,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :id
            """
            self.db.execute(query, {
            "id": user.get_id(),
            "name": user.name,
            "email": user.email,
            "password_hash": user.get_password_hash(),
            "role": user.role,
            "is_active": user._is_Active
            })

            self.db.commit()
            return self.get_by_id(user.get_id())
        except Exception as e  : 
            self.db.rollback()
            print("Error updating user:", e)
            return None






        
    

        
