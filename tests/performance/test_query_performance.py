import pytest
import time
from datetime import datetime


class TestQueryPerformance:
    """Test suite for query performance"""

    def test_indexed_query_performance(self, sample_student, student_repo):
        """Test performance of indexed field queries"""
        start_time = time.time()
        
        # Query by ID (should use index)
        result = student_repo.get_by_id(sample_student.get_id())
        
        elapsed = time.time() - start_time

        assert result is not None
        # Indexed query should be very fast
        assert elapsed < 0.5

    def test_join_query_performance(self, sample_student, sample_assignment,
                                     submission_repo):
        """Test performance of queries with joins"""
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

        # Query with implicit join (by student)
        start_time = time.time()
        results = submission_repo.list_by_student(sample_student.get_id())
        elapsed = time.time() - start_time

        assert len(results) >= 5
        assert elapsed < 1.0

    def test_pagination_query_performance(self, sample_student, sample_assignment, 
                                           submission_repo):
        """Test pagination query performance"""
        from core.entities.submission import Submission

        # Create submissions
        for i in range(10):
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

        # Query all
        start_time = time.time()
        results = submission_repo.list_by_student(sample_student.get_id())
        elapsed = time.time() - start_time

        assert len(results) >= 10
        assert elapsed < 1.0

    def test_aggregate_query_performance(self, sample_student, sample_assignment,
                                          submission_repo):
        """Test aggregate query performance"""
        from core.entities.submission import Submission

        # Create graded submissions
        for i in range(5):
            submission = Submission(
                id=None,
                assignment_id=sample_assignment.get_id(),
                student_id=sample_student.get_id(),
                version=i+1,
                language="python",
                status="graded",
                score=85.0 + i,
                is_late=False,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                grade_at=datetime.now()
            )
            submission_repo.create(submission)

        # Get submissions and calculate average manually
        start_time = time.time()
        results = submission_repo.list_by_student(sample_student.get_id())
        if results:
            graded = [s for s in results if s.status == "graded"]
            if graded:
                avg_score = sum(s.score for s in graded) / len(graded)
        elapsed = time.time() - start_time

        assert elapsed < 1.0
