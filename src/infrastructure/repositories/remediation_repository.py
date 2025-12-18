import sqlite3
from datetime import datetime
from core.entities.remediation import Remediation, StudentRemediation


class RemediationRepository:
    def __init__(self, db_path):
        self.db_path = db_path
    
    def _get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def _row_to_remediation(self, row):
        if not row:
            return None
        return Remediation(
            id=row[0],
            failure_pattern=row[1],
            resource_title=row[2],
            resource_type=row[3],
            resource_url=row[4],
            resource_content=row[5],
            difficulty_level=row[6],
            language=row[7],
            created_at=row[8]
        )
    
    def _row_to_student_remediation(self, row):
        if not row:
            return None
        return StudentRemediation(
            id=row[0],
            student_id=row[1],
            remediation_id=row[2],
            submission_id=row[3],
            is_viewed=bool(row[4]),
            is_completed=bool(row[5]),
            recommended_at=row[6],
            viewed_at=row[7],
            completed_at=row[8]
        )
    
    # Remediation CRUD
    
    def get_by_id(self, remediation_id: int) -> Remediation:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM remediations WHERE id = ?", (remediation_id,))
            return self._row_to_remediation(cursor.fetchone())
        finally:
            conn.close()
    
    def find_by_pattern(self, failure_pattern: str) -> list:
        """Find remediations matching a failure pattern."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT * FROM remediations WHERE failure_pattern = ?",
                (failure_pattern,)
            )
            return [self._row_to_remediation(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_all(self) -> list:
        """Get all remediations."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM remediations ORDER BY failure_pattern, difficulty_level")
            return [self._row_to_remediation(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def create(self, remediation: Remediation) -> Remediation:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO remediations 
                (failure_pattern, resource_title, resource_type, resource_url, 
                 resource_content, difficulty_level, language, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                remediation.failure_pattern,
                remediation.resource_title,
                remediation.resource_type,
                remediation.resource_url,
                remediation.resource_content,
                remediation.difficulty_level,
                remediation.language,
                datetime.utcnow().isoformat()
            ))
            conn.commit()
            return self.get_by_id(cursor.lastrowid)
        except sqlite3.Error as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_student_remediation(self, student_id: int, remediation_id: int) -> StudentRemediation:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT * FROM student_remediations WHERE student_id = ? AND remediation_id = ?",
                (student_id, remediation_id)
            )
            return self._row_to_student_remediation(cursor.fetchone())
        finally:
            conn.close()
    
    def get_student_remediation_by_id(self, sr_id: int) -> StudentRemediation:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM student_remediations WHERE id = ?", (sr_id,))
            return self._row_to_student_remediation(cursor.fetchone())
        finally:
            conn.close()
    
    def list_student_remediations(self, student_id: int, only_pending: bool = False) -> list:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            if only_pending:
                cursor.execute(
                    "SELECT * FROM student_remediations WHERE student_id = ? AND is_completed = 0 ORDER BY recommended_at DESC",
                    (student_id,)
                )
            else:
                cursor.execute(
                    "SELECT * FROM student_remediations WHERE student_id = ? ORDER BY recommended_at DESC",
                    (student_id,)
                )
            return [self._row_to_student_remediation(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def create_student_remediation(self, sr: StudentRemediation) -> StudentRemediation:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO student_remediations 
                (student_id, remediation_id, submission_id, is_viewed, is_completed, recommended_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                sr.get_student_id(),
                sr.get_remediation_id(),
                sr.get_submission_id(),
                sr.is_viewed,
                sr.is_completed,
                datetime.utcnow().isoformat()
            ))
            conn.commit()
            return self.get_student_remediation_by_id(cursor.lastrowid)
        except sqlite3.Error as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def update_student_remediation(self, sr: StudentRemediation) -> StudentRemediation:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE student_remediations 
                SET is_viewed = ?, is_completed = ?, viewed_at = ?, completed_at = ?
                WHERE id = ?
            """, (
                sr.is_viewed,
                sr.is_completed,
                sr.viewed_at.isoformat() if isinstance(sr.viewed_at, datetime) else sr.viewed_at,
                sr.completed_at.isoformat() if isinstance(sr.completed_at, datetime) else sr.completed_at,
                sr.get_id()
            ))
            conn.commit()
            return self.get_student_remediation_by_id(sr.get_id())
        except sqlite3.Error as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
