import sqlite3
from datetime import datetime
from core.entities.sandbox_job import SandboxJob


class SandboxJobRepository:
    def __init__(self, db_path):
        self.db_path = db_path
    
    def _get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def _row_to_entity(self, row):
        if not row:
            return None
        return SandboxJob(
            id=row[0],
            submission_id=row[1],
            status=row[2],
            started_at=row[3],
            completed_at=row[4],
            timeout_seconds=row[5],
            memory_limit_mb=row[6],
            exit_code=row[7],
            error_message=row[8],
            created_at=row[9]
        )
    
    def create(self, job: SandboxJob) -> SandboxJob:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO sandbox_jobs 
                (submission_id, status, started_at, completed_at, timeout_seconds, 
                 memory_limit_mb, exit_code, error_message, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job.get_submission_id(),
                job.status,
                job.started_at,
                job.completed_at,
                job.timeout_seconds,
                job.memory_limit_mb,
                job.exit_code,
                job.error_message,
                job.created_at.isoformat() if isinstance(job.created_at, datetime) else job.created_at
            ))
            conn.commit()
            return self.get_by_id(cursor.lastrowid)
        except sqlite3.Error as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_by_id(self, job_id: int) -> SandboxJob:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM sandbox_jobs WHERE id = ?", (job_id,))
            return self._row_to_entity(cursor.fetchone())
        finally:
            conn.close()
    
    def get_by_submission(self, submission_id: int) -> list:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT * FROM sandbox_jobs WHERE submission_id = ? ORDER BY created_at DESC",
                (submission_id,)
            )
            return [self._row_to_entity(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_pending_jobs(self, limit: int = 10) -> list:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT * FROM sandbox_jobs WHERE status = 'queued' ORDER BY created_at LIMIT ?",
                (limit,)
            )
            return [self._row_to_entity(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def update(self, job: SandboxJob) -> SandboxJob:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE sandbox_jobs 
                SET status = ?, started_at = ?, completed_at = ?, 
                    exit_code = ?, error_message = ?
                WHERE id = ?
            """, (
                job.status,
                job.started_at.isoformat() if isinstance(job.started_at, datetime) else job.started_at,
                job.completed_at.isoformat() if isinstance(job.completed_at, datetime) else job.completed_at,
                job.exit_code,
                job.error_message,
                job.get_id()
            ))
            conn.commit()
            return self.get_by_id(job.get_id())
        except sqlite3.Error as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
