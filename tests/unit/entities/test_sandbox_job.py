import pytest
from datetime import datetime
from core.entities.sandbox_job import SandboxJob


@pytest.mark.unit
class TestSandboxJobEntity:
    
    def test_create_sandbox_job_default(self):
        """Test creating a sandbox job with default values."""
        job = SandboxJob(
            id=1,
            submission_id=100
        )
        assert job.get_id() == 1
        assert job.get_submission_id() == 100
        assert job.status == 'queued'
        assert job.timeout_seconds == 5
        assert job.memory_limit_mb == 256
    
    def test_create_sandbox_job_custom(self):
        """Test creating a sandbox job with custom values."""
        job = SandboxJob(
            id=2,
            submission_id=200,
            status='running',
            timeout_seconds=10,
            memory_limit_mb=512
        )
        assert job.status == 'running'
        assert job.timeout_seconds == 10
        assert job.memory_limit_mb == 512
    
    def test_invalid_status_raises_error(self):
        """Test that invalid status raises ValueError."""
        with pytest.raises(ValueError, match="Invalid status"):
            SandboxJob(id=1, submission_id=100, status='invalid')
    
    def test_mark_running(self):
        """Test marking job as running."""
        job = SandboxJob(id=1, submission_id=100)
        job.mark_running()
        
        assert job.status == 'running'
        assert job.started_at is not None
    
    def test_mark_completed(self):
        """Test marking job as completed."""
        job = SandboxJob(id=1, submission_id=100)
        job.mark_running()
        job.mark_completed(exit_code=0)
        
        assert job.status == 'completed'
        assert job.completed_at is not None
        assert job.exit_code == 0
    
    def test_mark_failed(self):
        """Test marking job as failed."""
        job = SandboxJob(id=1, submission_id=100)
        job.mark_running()
        job.mark_failed("Syntax error", exit_code=1)
        
        assert job.status == 'failed'
        assert job.error_message == "Syntax error"
        assert job.exit_code == 1
    
    def test_mark_timeout(self):
        """Test marking job as timed out."""
        job = SandboxJob(id=1, submission_id=100, timeout_seconds=5)
        job.mark_running()
        job.mark_timeout()
        
        assert job.status == 'timeout'
        assert "5s timeout" in job.error_message
    
    def test_is_finished(self):
        """Test is_finished method."""
        job = SandboxJob(id=1, submission_id=100)
        assert job.is_finished() is False
        
        job.mark_completed()
        assert job.is_finished() is True
    
    def test_get_duration_ms(self):
        """Test duration calculation."""
        job = SandboxJob(id=1, submission_id=100)
        
        # No duration when not started
        assert job.get_duration_ms() is None
        
        job.mark_running()
        job.mark_completed()
        
        # Duration should be >= 0
        duration = job.get_duration_ms()
        assert duration is not None
        assert duration >= 0
