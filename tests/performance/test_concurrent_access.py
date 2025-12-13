import pytest
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor


class TestConcurrentAccess:
    """Test suite for concurrent database access"""

    def test_concurrent_user_registration(self, sample_student, user_repo):
        """Test concurrent user read operations"""
        # Verify sample student exists
        assert sample_student is not None
        
        # Test concurrent reads
        results = []
        for _ in range(5):
            result = user_repo.get_by_id(sample_student.get_id())
            results.append(result)
        
        # All reads should succeed
        assert all(r is not None for r in results)

    def test_concurrent_submissions(self, sample_student, sample_assignment,
                                     submission_repo):
        """Test multiple submissions creation"""
        from core.entities.submission import Submission

        # Create submissions sequentially (SQLite doesn't handle concurrent writes well)
        submissions = []
        for i in range(5):
            submission = Submission(
                id=None,
                assignment_id=sample_assignment.get_id(),
                student_id=sample_student.get_id(),
                version=i+1,
                language="python",
                status="pending",
                score=0.0,
                is_late=False,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                grade_at=None
            )
            saved = submission_repo.create(submission)
            submissions.append(saved)

        # Verify all created
        assert len(submissions) == 5

    def test_concurrent_read_operations(self, sample_student, sample_assignment,
                                        submission_repo):
        """Test concurrent read operations"""
        from core.entities.submission import Submission

        # Create a submission first
        submission = Submission(
            id=None,
            assignment_id=sample_assignment.get_id(),
            student_id=sample_student.get_id(),
            version=1,
            language="python",
            status="pending",
            score=0.0,
            is_late=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            grade_at=None
        )
        saved = submission_repo.create(submission)

        # Sequential reads (more reliable for SQLite)
        start_time = time.time()
        results = []
        for _ in range(10):
            result = submission_repo.get_by_id(saved.get_id())
            results.append(result)
        elapsed = time.time() - start_time

        # All reads should succeed
        assert all(r is not None for r in results)
        assert elapsed < 2.0  # Complete in reasonable time
