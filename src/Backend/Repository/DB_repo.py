from sqlalchemy import create_engine ,text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError


class Database : 
    def __init__(self,db_url:str): 
        self.db_url = db_url
        self.session_local=None
        self.engine = None
        self.session = None

    def connect(self):
        try: 
            self.engine= create_engine(self.db_url)
            self.session_local = sessionmaker(bind=self.engine)
            self.session = self.session_local()
            print("Database connection established.")
        except SQLAlchemyError as e:
            print(f"Error connecting to the database: {e}")

    def disconnect(self):
        try:    
            if self.session:
                self.session.close()
                print("Database session closed.")
            if self.engine:
                self.engine.dispose()
                print("Database engine disposed.")
        except SQLAlchemyError as e:
            print(f"Error disconnecting from the database: {e}")

    def begin_transaction(self):
        try:
            if self.session:
                self.session.begin()
                print("Transaction started.")
        except SQLAlchemyError as e:
            print(f"Error starting transaction: {e}")

    def commit(self):
        try: 
            self.session.commit()
            print("Transaction committed.")
        except SQLAlchemyError as e:
            print(f"Error committing transaction: {e}")
            self.session.rollback()
            print("Transaction rolled back due to error.") 

    def rollback(self):
        try:
            self.session.rollback()
            print("Transaction rolled back.")
        except SQLAlchemyError as e:
            print(f"Error rolling back transaction: {e}")
    
    def execute(self,query:str,params:dict=None):
        try:
            if params:
                result = self.session.execute(text(query),params)
            else:
                result = self.session.execute(text(query))
            print("Query executed successfully.")
            return result
        except SQLAlchemyError as e:
            print(f"Error executing query: {e}")
            return None