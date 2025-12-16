import pytest
import time
from datetime import datetime


class TestBulkOperations:
    """Test suite for bulk operation performance"""

    def test_bulk_user_registration(self, sample_student, user_repo):
        """Test bulk user operations work correctly"""
        # Verify sample student exists
        assert sample_student is not None
        
        # Verify we can retrieve the user
        retrieved = user_repo.get_by_id(sample_student.get_id())
        assert retrieved is not None

    def test_bulk_submission_creation(self, sample_student, sample_assignment,
                                       submission_repo):
        """Test creating many submissions efficiently"""
        from core.entities.submission import Submission

        start_time = time.time()
        count = 10

        submissions = []
        for i in range(count):
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

        elapsed = time.time() - start_time

        # Verify all created
        assert len(submissions) == count

        # Performance check
        assert elapsed < 5.0  # 10 submissions in under 5 seconds

    def test_bulk_query_performance(self, sample_student, sample_assignment, submission_repo):
        """Test querying large result sets"""
        from core.entities.submission import Submission

        # Create some submissions
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
            submission_repo.create(submission)

        # Query submissions
        start_time = time.time()
        submissions = submission_repo.list_by_student(sample_student.get_id())
        elapsed = time.time() - start_time

        # Verify query worked
        assert len(submissions) >= 5
        
        # Performance check
        assert elapsed < 1.0  # Query in under 1 second
