import sqlite3
from core.entities.draft import Draft

class DraftRepository:
    def __init__(self, db):
        self.db = db

    def create(self, draft: Draft):
        try:
            query = '''
                INSERT INTO drafts (user_id, assignment_id, content, language, saved_at)
                VALUES (:user_id, :assignment_id, :content, :language, CURRENT_TIMESTAMP)
            '''
            self.db.execute(query, {
                'user_id': draft.get_user_id(),
                'assignment_id': draft.get_assignment_id(),
                'content': draft.content,
                'language': draft.language
            })
            new_id = self.db.execute("SELECT last_insert_rowid() as id").fetchone()[0]
            self.db.commit()
            return self.get_by_id(new_id)
        except sqlite3.Error:
            self.db.rollback()
            return None

    def get_by_id(self, id: int):
        row = self.db.execute('SELECT * FROM drafts WHERE id = :id', {'id': id}).fetchone()
        if not row:
            return None
        return Draft(
            id=row.id,
            user_id=row.user_id,
            assignment_id=row.assignment_id,
            content=row.content,
            language=getattr(row, 'language', 'python'),
            saved_at=getattr(row, 'saved_at', None)
        )

    def get_latest(self, user_id: int, assignment_id: int):
        query = '''
            SELECT * FROM drafts
            WHERE user_id = :uid AND assignment_id = :aid
            ORDER BY saved_at DESC
            LIMIT 1
        '''
        row = self.db.execute(query, {'uid': user_id, 'aid': assignment_id}).fetchone()
        if not row:
            return None
        return Draft(
            id=row.id,
            user_id=row.user_id,
            assignment_id=row.assignment_id,
            content=row.content,
            language=getattr(row, 'language', 'python'),
            saved_at=getattr(row, 'saved_at', None)
        )

    def delete(self, id: int):
        try:
            self.db.execute('DELETE FROM drafts WHERE id = :id', {'id': id})
            self.db.commit()
            return True
        except sqlite3.Error:
            self.db.rollback()
            return False
