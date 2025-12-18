import sqlite3
from datetime import datetime
from core.entities.sandbox_job import SandboxJob


class SandboxJobRepository:
    def __init__(self, db):
        self.db = db
    
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
        try:
            self.db.execute("""
                INSERT INTO sandbox_jobs 
                (submission_id, status, started_at, completed_at, timeout_seconds, 
                 memory_limit_mb, exit_code, error_message, created_at)
                VALUES (:sid, :status, :start, :comp, :tout, :mem, :exit, :err, :cat)
            """, {
                "sid": job.get_submission_id(),
                "status": job.status,
                "start": job.started_at,
                "comp": job.completed_at,
                "tout": job.timeout_seconds,
                "mem": job.memory_limit_mb,
                "exit": job.exit_code,
                "err": job.error_message,
                "cat": job.created_at.isoformat() if isinstance(job.created_at, datetime) else job.created_at
            })
            self.db.commit()
            new_id = self.db.execute("SELECT last_insert_rowid()").fetchone()[0]
            return self.get_by_id(new_id)
        except sqlite3.Error as e:
            self.db.rollback()
            raise e
    
    def get_by_id(self, job_id: int) -> SandboxJob:
        result = self.db.execute("SELECT * FROM sandbox_jobs WHERE id = :id", {"id": job_id})
        return self._row_to_entity(result.fetchone())
    
    def get_by_submission(self, submission_id: int) -> list:
        result = self.db.execute(
            "SELECT * FROM sandbox_jobs WHERE submission_id = :sid ORDER BY created_at DESC",
            {"sid": submission_id}
        )
        return [self._row_to_entity(row) for row in result.fetchall()]
    
    def get_pending_jobs(self, limit: int = 10) -> list:
        result = self.db.execute(
            "SELECT * FROM sandbox_jobs WHERE status = 'queued' ORDER BY created_at LIMIT :limit",
            {"limit": limit}
        )
        return [self._row_to_entity(row) for row in result.fetchall()]
    
    def update(self, job: SandboxJob) -> SandboxJob:
        try:
            self.db.execute("""
                UPDATE sandbox_jobs 
                SET status = :status, started_at = :start, completed_at = :comp, 
                    exit_code = :exit, error_message = :err
                WHERE id = :id
            """, {
                "status": job.status,
                "start": job.started_at.isoformat() if isinstance(job.started_at, datetime) else job.started_at,
                "comp": job.completed_at.isoformat() if isinstance(job.completed_at, datetime) else job.completed_at,
                "exit": job.exit_code,
                "err": job.error_message,
                "id": job.get_id()
            })
            self.db.commit()
            return self.get_by_id(job.get_id())
        except sqlite3.Error as e:
            self.db.rollback()
            raise e
