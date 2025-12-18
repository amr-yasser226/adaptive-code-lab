import pytest
from datetime import datetime
from core.entities.sandbox_job import SandboxJob

@pytest.mark.repo
@pytest.mark.unit
class TestSandboxJobRepo:
    def test_create_and_get_job(self, sandbox_job_repo, sample_submission):
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

    def test_get_by_submission(self, sandbox_job_repo, sample_submission):
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
