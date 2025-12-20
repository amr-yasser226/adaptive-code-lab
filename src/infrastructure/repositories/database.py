from sqlalchemy import create_engine ,text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import os

import sqlite3

class Database:
    def __init__(self):
        load_dotenv()
        self.db_url = os.getenv("ACCL_DB_PATH")
        if not self.db_url:
            raise ValueError("ACCL_DB_PATH not found in .env")
        self.session_local = None
        self.engine = None
        self.session = None

    def connect(self):
        try:
            self.engine = create_engine(self.db_url)
            self.session_local = sessionmaker(bind=self.engine)
            self.session = self.session_local()
        except SQLAlchemyError as e:
            self._handle_error(e)

    def disconnect(self):
        try:
            if self.session:
                self.session.close()
            if self.engine:
                self.engine.dispose()
        except SQLAlchemyError as e:
            self._handle_error(e)

    def begin_transaction(self):
        try:
            if self.session:
                self.session.begin()
        except SQLAlchemyError as e:
            self._handle_error(e)

    def commit(self):
        try:
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            self._handle_error(e)

    def rollback(self):
        try:
            self.session.rollback()
        except SQLAlchemyError as e:
            self._handle_error(e)

    def execute(self, query: str, params: dict = None):
        try:
            if params:
                result = self.session.execute(text(query), params)
            else:
                result = self.session.execute(text(query))
            return result
        except SQLAlchemyError as e:
            self._handle_error(e)

    def _handle_error(self, e):
        """Unwrap SQLAlchemyError to raise the underlying DBAPI error if it's sqlite3.Error"""
        if hasattr(e, 'orig') and isinstance(e.orig, sqlite3.Error):
            raise e.orig
        raise e