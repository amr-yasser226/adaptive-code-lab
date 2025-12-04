from sqlalchemy.exc import SQLAlchemyError
from Model.Instructor_model import Instructor

class Instrucotr_repo : 
    def __init__(self , db ):
        self.db = db


    def get_by_id(self ,id:int ):
        query = """
            SELECT 
                u.id, u.name, u.email, u.password_hash, u.role,
                u.created_at, u.updated_at, u.is_active,
                i.instructor_code, i.bio, i.office_hours
            FROM users u
            INNER JOIN instructors i ON u.id = i.id
            WHERE u.id = :id
        """
        result =self.db.execute(query, {"id":id})
        row =result.fetchone()
        if result: 
            row =result.fetchone()
        else : 
            row = None
                
        if not row : 
            return row
        
        return Instructor(
            id=row.id,
            name=row.name,
            email=row.email,
            password=row.password_hash,
            created_at=row.created_at,
            updated_at=row.updated_at,
            instructor_code=row.instructor_code,
            bio=row.bio,
            office_hours=row.office_hours,
            is_Active=row.is_active
        )
    
    def get_by_instructor_code (self , instructor_code): 
        query = """
            SELECT 
                u.id, u.name, u.email, u.password_hash, u.role,
                u.created_at, u.updated_at, u.is_active,
                i.instructor_code, i.bio, i.office_hours
            FROM users u
            INNER JOIN instructors i ON u.id = i.id
            WHERE i.instructor_code = :code
        """
        result =self.db.execute(query, {"code": instructor_code})
        if result : 
            row = result.fetchone()
        else : 
            row = None 

        if row is None : 
            return None
        
        return Instructor(
            id=row.id,
            name=row.name,
            email=row.email,
            password=row.password_hash,
            created_at=row.created_at,
            updated_at=row.updated_at,
            instructor_code=row.instructor_code,
            bio=row.bio,
            office_hours=row.office_hours,
            is_Active=row.is_active
        )