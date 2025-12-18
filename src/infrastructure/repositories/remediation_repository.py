import sqlite3
from datetime import datetime
from core.entities.remediation import Remediation, StudentRemediation


class RemediationRepository:
    def __init__(self, db):
        self.db = db
    
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
        result = self.db.execute("SELECT * FROM remediations WHERE id = :id", {"id": remediation_id})
        return self._row_to_remediation(result.fetchone())
    
    def find_by_pattern(self, failure_pattern: str) -> list:
        """Find remediations matching a failure pattern."""
        result = self.db.execute(
            "SELECT * FROM remediations WHERE failure_pattern = :pattern",
            {"pattern": failure_pattern}
        )
        return [self._row_to_remediation(row) for row in result.fetchall()]
    
    def get_all(self) -> list:
        """Get all remediations."""
        result = self.db.execute("SELECT * FROM remediations ORDER BY failure_pattern, difficulty_level")
        return [self._row_to_remediation(row) for row in result.fetchall()]
    
    def create(self, remediation: Remediation) -> Remediation:
        try:
            self.db.execute("""
                INSERT INTO remediations 
                (failure_pattern, resource_title, resource_type, resource_url, 
                 resource_content, difficulty_level, language, created_at)
                VALUES (:fp, :rt, :rtype, :rurl, :rcont, :diff, :lang, :cat)
            """, {
                "fp": remediation.failure_pattern,
                "rt": remediation.resource_title,
                "rtype": remediation.resource_type,
                "rurl": remediation.resource_url,
                "rcont": remediation.resource_content,
                "diff": remediation.difficulty_level,
                "lang": remediation.language,
                "cat": datetime.utcnow().isoformat()
            })
            self.db.commit()
            new_id = self.db.execute("SELECT last_insert_rowid()").fetchone()[0]
            return self.get_by_id(new_id)
        except sqlite3.Error as e:
            self.db.rollback()
            raise e
    
    def get_student_remediation(self, student_id: int, remediation_id: int) -> StudentRemediation:
        result = self.db.execute(
            "SELECT * FROM student_remediations WHERE student_id = :sid AND remediation_id = :rid",
            {"sid": student_id, "rid": remediation_id}
        )
        return self._row_to_student_remediation(result.fetchone())
    
    def get_student_remediation_by_id(self, sr_id: int) -> StudentRemediation:
        result = self.db.execute("SELECT * FROM student_remediations WHERE id = :id", {"id": sr_id})
        return self._row_to_student_remediation(result.fetchone())
    
    def list_student_remediations(self, student_id: int, only_pending: bool = False) -> list:
        if only_pending:
            result = self.db.execute(
                "SELECT * FROM student_remediations WHERE student_id = :sid AND is_completed = 0 ORDER BY recommended_at DESC",
                {"sid": student_id}
            )
        else:
            result = self.db.execute(
                "SELECT * FROM student_remediations WHERE student_id = :sid ORDER BY recommended_at DESC",
                {"sid": student_id}
            )
        return [self._row_to_student_remediation(row) for row in result.fetchall()]
    
    def create_student_remediation(self, sr: StudentRemediation) -> StudentRemediation:
        try:
            self.db.execute("""
                INSERT INTO student_remediations 
                (student_id, remediation_id, submission_id, is_viewed, is_completed, recommended_at)
                VALUES (:sid, :rid, :subid, :iv, :ic, :rat)
            """, {
                "sid": sr.get_student_id(),
                "rid": sr.get_remediation_id(),
                "subid": sr.get_submission_id(),
                "iv": int(sr.is_viewed),
                "ic": int(sr.is_completed),
                "rat": datetime.utcnow().isoformat()
            })
            self.db.commit()
            new_id = self.db.execute("SELECT last_insert_rowid()").fetchone()[0]
            return self.get_student_remediation_by_id(new_id)
        except sqlite3.Error as e:
            self.db.rollback()
            raise e
    
    def update_student_remediation(self, sr: StudentRemediation) -> StudentRemediation:
        try:
            self.db.execute("""
                UPDATE student_remediations 
                SET is_viewed = :iv, is_completed = :ic, viewed_at = :vat, completed_at = :cat
                WHERE id = :id
            """, {
                "iv": int(sr.is_viewed),
                "ic": int(sr.is_completed),
                "vat": sr.viewed_at.isoformat() if isinstance(sr.viewed_at, datetime) else sr.viewed_at,
                "cat": sr.completed_at.isoformat() if isinstance(sr.completed_at, datetime) else sr.completed_at,
                "id": sr.get_id()
            })
            self.db.commit()
            return self.get_student_remediation_by_id(sr.get_id())
        except sqlite3.Error as e:
            self.db.rollback()
            raise e
