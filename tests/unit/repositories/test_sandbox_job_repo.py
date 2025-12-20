import pytest
import sqlite3
from unittest.mock import Mock
from datetime import datetime
from core.entities.sandbox_job import SandboxJob


@pytest.mark.repo
@pytest.mark.unit
class TestSandboxJobRepo:
    """Test suite for SandboxJobRepository"""
    
    def test_create_and_get_job(self, sandbox_job_repo, sample_submission):
        """Test creating and retrieving sandbox job by ID"""
        job = SandboxJob(
            id=None,
            submission_id=sample_submission.get_id(),
            status="queued",
            started_at=None,
            completed_at=None,
            timeout_seconds=30,
            memory_limit_mb=128
        )
        
        saved = sandbox_job_repo.create(job)
        assert saved.get_id() is not None
        assert saved.status == "queued"
        
        retrieved = sandbox_job_repo.get_by_id(saved.get_id())
        assert retrieved is not None
        assert retrieved.get_submission_id() == sample_submission.get_id()

    def test_get_by_id_not_found(self, sandbox_job_repo):
        """Line 12: _row_to_entity returns None for empty row"""
        assert sandbox_job_repo.get_by_id(9999) is None

    def test_get_by_submission(self, sandbox_job_repo, sample_submission):
        """Test retrieving jobs by submission ID"""
        job = SandboxJob(
            id=None,
            submission_id=sample_submission.get_id(),
            status="queued"
        )
        sandbox_job_repo.create(job)
        
        jobs = sandbox_job_repo.get_by_submission(sample_submission.get_id())
        assert len(jobs) >= 1
        assert jobs[0].get_submission_id() == sample_submission.get_id()

    def test_get_pending_jobs(self, sandbox_job_repo, sample_submission):
        """Test retrieving queued jobs with limit"""
        job = SandboxJob(
            id=None,
            submission_id=sample_submission.get_id(),
            status="queued"
        )
        sandbox_job_repo.create(job)
        
        pending = sandbox_job_repo.get_pending_jobs(limit=5)
        assert len(pending) >= 1
        assert any(p.status == "queued" for p in pending)

    def test_update_job(self, sandbox_job_repo, sample_submission):
        """Test updating sandbox job status and timestamps"""
        job = SandboxJob(
            id=None,
            submission_id=sample_submission.get_id(),
            status="queued"
        )
        saved = sandbox_job_repo.create(job)
        
        saved.mark_running()
        updated = sandbox_job_repo.update(saved)
        assert updated.status == "running"
        assert updated.started_at is not None
        
        updated.mark_completed(exit_code=0)
        final = sandbox_job_repo.update(updated)
        assert final.status == "completed"
        assert final.completed_at is not None
        assert final.exit_code == 0

    def test_create_error(self, sandbox_job_repo, sample_submission):
        """Line 48-49: create handles sqlite3.Error"""
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        sandbox_job_repo.db = mock_db
        job = SandboxJob(None, sample_submission.get_id(), "queued")
        with pytest.raises(sqlite3.Error):
            sandbox_job_repo.create(job)
        mock_db.rollback.assert_called_once()

    def test_update_error(self, sandbox_job_repo, sample_submission):
        """Line 87-89: update handles sqlite3.Error"""
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        sandbox_job_repo.db = mock_db
        job = SandboxJob(1, sample_submission.get_id(), "running")
        # Ensure job has non-None created_at for update query fields if necessary, 
        # though update doesn't use all fields.
        with pytest.raises(sqlite3.Error):
            sandbox_job_repo.update(job)
        mock_db.rollback.assert_called_once()
