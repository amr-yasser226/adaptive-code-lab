from datetime import datetime
from core.exceptions.auth_error import AuthError
from core.exceptions.validation_error import ValidationError
from core.entities.peer_review import PeerReview


class PeerReviewService:
    def __init__(
        self,
        peer_review_repo,
        submission_repo,
        enrollment_repo,
        assignment_repo,
        course_repo
    ):
        self.peer_review_repo = peer_review_repo
        self.submission_repo = submission_repo
        self.enrollment_repo = enrollment_repo
        self.assignment_repo = assignment_repo
        self.course_repo = course_repo

    # ----------------------------------------------------
    # INTERNAL HELPERS
    # ----------------------------------------------------
    def _verify_student_enrolled(self, student_id, course_id):
        enrollment = self.enrollment_repo.get(student_id, course_id)
        if not enrollment or enrollment.status != "enrolled":
            raise AuthError("Student is not enrolled in this course")

    def _verify_submission_exists(self, submission_id):
        submission = self.submission_repo.get_by_id(submission_id)
        if not submission:
            raise ValidationError("Submission not found")
        return submission

    def _verify_assignment_course(self, submission):
        assignment = self.assignment_repo.get_by_id(
            submission.get_assignment_id()
        )
        if not assignment:
            raise ValidationError("Assignment not found")

        course = self.course_repo.get_by_id(assignment.get_course_id())
        if not course:
            raise ValidationError("Course not found")

        return assignment, course

    # ----------------------------------------------------
    # CREATE PEER REVIEW (DRAFT)
    # ----------------------------------------------------
    def create_review(
        self,
        reviewer_student,
        submission_id,
        rubric_score=None,
        comments=None
    ):
        if reviewer_student.role != "student":
            raise AuthError("Only students can create peer reviews")

        submission = self._verify_submission_exists(submission_id)
        assignment, course = self._verify_assignment_course(submission)

        # Student must be enrolled
        self._verify_student_enrolled(
            reviewer_student.get_id(),
            course.get_id()
        )

        # Prevent self-review
        if submission.get_student_id() == reviewer_student.get_id():
            raise ValidationError("You cannot review your own submission")

        existing = self.peer_review_repo.get(
            submission_id,
            reviewer_student.get_id()
        )
        if existing:
            raise ValidationError("Peer review already exists")

        review = PeerReview(
            submission_id=submission_id,
            reviewer_student_id=reviewer_student.get_id(),
            rubric_score=rubric_score,
            comments=comments,
            is_submitted=False,
            submitted_at=None,
            created_at=datetime.now()
        )

        return self.peer_review_repo.create(review)

    # ----------------------------------------------------
    # UPDATE PEER REVIEW (DRAFT)
    # ----------------------------------------------------
    def update_review(
        self,
        reviewer_student,
        submission_id,
        rubric_score=None,
        comments=None
    ):
        review = self.peer_review_repo.get(
            submission_id,
            reviewer_student.get_id()
        )
        if not review:
            raise ValidationError("Peer review not found")

        if review.is_submitted:
            raise ValidationError("Cannot edit a submitted review")

        review.update_review(rubric_score, comments)
        return self.peer_review_repo.update(review)

    # ----------------------------------------------------
    # SUBMIT PEER REVIEW (FINAL)
    # ----------------------------------------------------
    def submit_review(self, reviewer_student, submission_id):
        review = self.peer_review_repo.get(
            submission_id,
            reviewer_student.get_id()
        )
        if not review:
            raise ValidationError("Peer review not found")

        if review.is_submitted:
            raise ValidationError("Peer review already submitted")

        if not review.rubric_score:
            raise ValidationError("Rubric score is required before submission")

        review.submit_review()
        return self.peer_review_repo.update(review)

    # ----------------------------------------------------
    # VIEW PEER REVIEWS
    # ----------------------------------------------------
    def list_reviews_for_submission(self, user, submission_id):
        submission = self._verify_submission_exists(submission_id)
        assignment, course = self._verify_assignment_course(submission)

        # Instructor can view all
        if user.role == "instructor":
            if course.get_instructor_id() != user.get_id():
                raise AuthError("Not authorized to view these reviews")
            return self.peer_review_repo.list_by_submission(submission_id)

        # Student can view only their received reviews
        if user.role == "student":
            if submission.get_student_id() != user.get_id():
                raise AuthError("You cannot view reviews for this submission")
            return self.peer_review_repo.list_by_submission(submission_id)

        raise AuthError("Unauthorized access")

    # ----------------------------------------------------
    # CALCULATE FINAL PEER SCORE
    # ----------------------------------------------------
    def calculate_peer_average(self, submission_id):
        reviews = self.peer_review_repo.list_by_submission(submission_id)
        if not reviews:
            return 0.0

        scores = [
            r.calculate_rubric_score()
            for r in reviews
            if r.is_submitted
        ]

        if not scores:
            return 0.0

        return sum(scores) / len(scores)
