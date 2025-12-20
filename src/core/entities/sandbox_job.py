"""
Sandbox Job Entity - FR-04
Represents a code execution job in the sandbox
"""
from datetime import datetime


class SandboxJob:
    valid_statuses = ('queued', 'running', 'completed', 'failed', 'timeout')
    
    def __init__(
        self,
        id,
        submission_id,
        status='queued',
        started_at=None,
        completed_at=None,
        timeout_seconds=5,
        memory_limit_mb=256,
        exit_code=None,
        error_message=None,
        created_at=None
    ):
        if status not in SandboxJob.valid_statuses:
            raise ValueError(f"Invalid status: {status}. Allowed: {SandboxJob.valid_statuses}")
        
        self.__id = id
        self.__submission_id = submission_id
        self.status = status
        self.started_at = started_at
        self.completed_at = completed_at
        self.timeout_seconds = timeout_seconds
        self.memory_limit_mb = memory_limit_mb
        self.exit_code = exit_code
        self.error_message = error_message
        self.created_at = created_at or datetime.utcnow()
    
    def get_id(self):
        return self.__id
    
    def get_submission_id(self):
        return self.__submission_id
    
    def mark_running(self):
        """Mark job as running."""
        self.status = 'running'
        self.started_at = datetime.utcnow()
    
    def mark_completed(self, exit_code=0):
        """Mark job as completed successfully."""
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
        self.exit_code = exit_code
    
    def mark_failed(self, error_message, exit_code=1):
        """Mark job as failed."""
        self.status = 'failed'
        self.completed_at = datetime.utcnow()
        self.exit_code = exit_code
        self.error_message = error_message
    
    def mark_timeout(self):
        """Mark job as timed out."""
        self.status = 'timeout'
        self.completed_at = datetime.utcnow()
        self.error_message = f"Execution exceeded {self.timeout_seconds}s timeout"
    
    def is_finished(self):
        """Check if job has finished (regardless of outcome)."""
        return self.status in ('completed', 'failed', 'timeout')
    
    def get_duration_ms(self):
        """Get execution duration in milliseconds."""
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            return int(delta.total_seconds() * 1000)
        return None
