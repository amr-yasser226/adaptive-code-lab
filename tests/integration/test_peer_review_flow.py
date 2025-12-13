import pytest
from datetime import datetime


class TestPeerReviewFlow:
    """Test suite for peer review end-to-end workflow"""

    def test_peer_review_cycle(self, clean_db, sample_student, sample_assignment,
                                user_repo, student_repo, submission_repo, peer_review_repo):
        """Test complete peer review cycle"""
        from core.entities.submission import Submission
        from core.entities.peer_review import PeerReview
        from core.entities.student import Student

        # Create second student as reviewer using proper User + Student pattern
        from core.entities.user import User
        reviewer_user = User(
            id=None,
            name="Reviewer Student",
            email="reviewer@test.edu",
            password="hashed_pwd",
            role="student",
            is_active=True
        )
        saved_reviewer_user = user_repo.save_user(reviewer_user)
        
        reviewer = Student(
            id=saved_reviewer_user.get_id(),
            name=saved_reviewer_user.name,
            email=saved_reviewer_user.email,
            password=saved_reviewer_user.get_password_hash(),
            created_at=saved_reviewer_user.created_at,
            updated_at=saved_reviewer_user.updated_at,
            student_number="ST9999", program="CS", year_level=2
        )
        saved_reviewer = student_repo.save_student(reviewer)

        # Create submission to be reviewed
        submission = Submission(
            id=None,
            assignment_id=sample_assignment.get_id(),
            student_id=sample_student.get_id(),
            version=1,
            language="python",
            status="graded",
            score=85,
            is_late=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            grade_at=datetime.now()
        )
        saved_submission = submission_repo.create(submission)

        # Create peer review
        review = PeerReview(
            submission_id=saved_submission.get_id(),
            reviewer_student_id=saved_reviewer.get_id(),
            rubric_score={"code_quality": 4, "documentation": 5, "correctness": 4},
            comments="Good work, well documented",
            is_submitted=False,
            submitted_at=None,
            created_at=datetime.now()
        )
        saved_review = peer_review_repo.create(review)

        # Submit review
        saved_review.is_submitted = True
        saved_review.submitted_at = datetime.now()
        final_review = peer_review_repo.update(saved_review)

        # Verify
        assert final_review.is_submitted is True
        assert final_review.calculate_rubric_score() > 0

    def test_multiple_peer_reviews(self, clean_db, sample_assignment, student_repo,
                                    submission_repo, peer_review_repo, user_repo):
        """Test multiple reviews for same submission"""
        from core.entities.submission import Submission
        from core.entities.peer_review import PeerReview
        from core.entities.student import Student
        from core.entities.user import User

        # Helper function to create student with User
        def create_student(name, email, student_num):
            user = User(id=None, name=name, email=email, password="pwd", role="student", is_active=True)
            saved_user = user_repo.save_user(user)
            student = Student(
                id=saved_user.get_id(), name=saved_user.name, email=saved_user.email,
                password=saved_user.get_password_hash(), created_at=saved_user.created_at,
                updated_at=saved_user.updated_at, student_number=student_num, program="CS", year_level=2
            )
            return student_repo.save_student(student)

        # Create author and two reviewers
        author = create_student("Author", "author@test.edu", "STA001")
        reviewer1 = create_student("Reviewer1", "r1@test.edu", "STR001")
        reviewer2 = create_student("Reviewer2", "r2@test.edu", "STR002")

        # Create submission
        submission = submission_repo.create(Submission(
            id=None, assignment_id=sample_assignment.get_id(),
            student_id=author.get_id(), version=1, language="python",
            status="graded", score=80, is_late=False,
            created_at=datetime.now(), updated_at=datetime.now(),
            grade_at=datetime.now()
        ))

        # Create two reviews
        review1 = peer_review_repo.create(PeerReview(
            submission_id=submission.get_id(),
            reviewer_student_id=reviewer1.get_id(),
            rubric_score={"quality": 4},
            comments="Good",
            is_submitted=True,
            submitted_at=datetime.now(),
            created_at=datetime.now()
        ))
        review2 = peer_review_repo.create(PeerReview(
            submission_id=submission.get_id(),
            reviewer_student_id=reviewer2.get_id(),
            rubric_score={"quality": 5},
            comments="Excellent",
            is_submitted=True,
            submitted_at=datetime.now(),
            created_at=datetime.now()
        ))

        # Get all reviews for submission
        reviews = peer_review_repo.list_by_submission(submission.get_id())
        assert len(reviews) == 2

        # Calculate average peer score
        scores = [r.calculate_rubric_score() for r in reviews]
        avg_score = sum(scores) / len(scores)
        assert avg_score == 4.5
