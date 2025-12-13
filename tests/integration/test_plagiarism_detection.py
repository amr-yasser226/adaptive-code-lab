import pytest
from datetime import datetime


class TestPlagiarismDetection:
    """Test suite for plagiarism detection workflow"""

    def test_similarity_detection_and_flagging(self, sample_student, sample_assignment,
                                                submission_repo, similarity_repo):
        """Test complete similarity detection workflow"""
        from core.entities.submission import Submission
        from core.entities.similarity_flag import SimilarityFlag

        # Create submission for sample student
        submission = submission_repo.create(Submission(
            id=None, assignment_id=sample_assignment.get_id(),
            student_id=sample_student.get_id(), version=1, language="python",
            status="graded", score=90, is_late=False,
            created_at=datetime.now(), updated_at=datetime.now(),
            grade_at=datetime.now()
        ))

        # Create similarity flag with correct parameters
        flag = SimilarityFlag(
            id=None,
            submission_id=submission.get_id(),
            similarity_score=0.92,
            highlighted_spans="lines 1-10, 20-30",
            is_reviewed=False,
            reviewd_by=None,
            review_notes=None,
            reviewed_at=None,
            created_at=datetime.now()
        )
        saved_flag = similarity_repo.create(flag)

        # Verify flag was saved
        assert saved_flag is not None
        assert saved_flag.similarity_score == 0.92
        assert saved_flag.is_reviewed is False

    def test_flag_review_workflow(self, sample_student, sample_instructor, sample_assignment,
                                   submission_repo, similarity_repo):
        """Test instructor reviewing and dismissing similarity flag"""
        from core.entities.submission import Submission
        from core.entities.similarity_flag import SimilarityFlag

        # Create submission
        submission = submission_repo.create(Submission(
            id=None, assignment_id=sample_assignment.get_id(),
            student_id=sample_student.get_id(), version=1, language="python",
            status="graded", score=85, is_late=False,
            created_at=datetime.now(), updated_at=datetime.now(),
            grade_at=datetime.now()
        ))

        # Create flag with correct parameters
        flag = SimilarityFlag(
            id=None,
            submission_id=submission.get_id(),
            similarity_score=0.75,
            highlighted_spans="lines 5-15",
            is_reviewed=False,
            reviewd_by=None,
            review_notes=None,
            reviewed_at=None,
            created_at=datetime.now()
        )
        saved_flag = similarity_repo.create(flag)

        # Instructor reviews and dismisses
        saved_flag.is_reviewed = True
        saved_flag.reviewd_by = sample_instructor.get_id()
        saved_flag.review_notes = "Dismissed - common code pattern"
        saved_flag.reviewed_at = datetime.now()
        updated_flag = similarity_repo.update(saved_flag)

        assert updated_flag.is_reviewed is True
        assert updated_flag.review_notes == "Dismissed - common code pattern"
