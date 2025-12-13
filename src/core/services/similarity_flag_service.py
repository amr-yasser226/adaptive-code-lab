from datetime import datetime
from core.exceptions.validation_error import ValidationError
from core.exceptions.auth_error import AuthError
from core.entities.similarity_flag import SimilarityFlag
from core.entities.similarity_comparison import SimilarityComparison


class Similarity_flag_Service:
    def __init__(
        self,
        similarity_repo,
        comparison_repo,
        submission_repo,
        assignment_repo,
        course_repo
    ):
        self.similarity_repo = similarity_repo
        self.comparison_repo = comparison_repo
        self.submission_repo = submission_repo
        self.assignment_repo = assignment_repo
        self.course_repo = course_repo

    # ------------------------------------------------------------------
    # INTERNAL PERMISSION CHECK
    # ------------------------------------------------------------------
    def _verify_instructor_permission(self, instructor_id, flag: SimilarityFlag):
        """Ensure instructor reviewing the flag actually owns the course."""
        submission = self.submission_repo.get_by_id(flag.get_submission_id())
        if not submission:
            raise ValidationError("Cannot review: submission not found")

        assignment = self.assignment_repo.get_by_id(submission.get_assignment_id())
        if not assignment:
            raise ValidationError("Cannot review: assignment not found")

        course = self.course_repo.get_by_id(assignment.get_course_id())
        if not course:
            raise ValidationError("Cannot review: course not found")

        if course.get_instructor_id() != instructor_id:
            raise AuthError("You are not allowed to review similarity flags for this course")

    # ------------------------------------------------------------------
    # CREATE FLAG
    # ------------------------------------------------------------------
    def create_flag(self, submission_id, similarity_score, highlighted_spans=None):
        submission = self.submission_repo.get_by_id(submission_id)
        if not submission:
            raise ValidationError("Submission not found")

        flag = SimilarityFlag(
            id=None,
            submission_id=submission_id,
            similarity_score=similarity_score,
            highlighted_spans=highlighted_spans,
            is_reviewed=False,
            reviewd_by=None,
            review_notes=None,
            reviewed_at=None,
            created_at=datetime.now()
        )

        return self.similarity_repo.create(flag)

    # ------------------------------------------------------------------
    # ADD COMPARISON DETAILS
    # ------------------------------------------------------------------
    def add_comparison(self, similarity_id, compared_submission_id, match_score, note, segments):
        """Add a single similarity comparison entry."""

        flag = self.similarity_repo.get_by_id(similarity_id)
        if not flag:
            raise ValidationError("Similarity flag not found")

        comp = SimilarityComparison(
            similarity_id=similarity_id,
            compared_submission_id=compared_submission_id,
            match_score=match_score,
            note=note,
            match_segments=segments
        )

        return self.comparison_repo.create(comp)

    # ------------------------------------------------------------------
    # LIST COMPARISONS FOR FLAG
    # ------------------------------------------------------------------
    def get_comparisons(self, similarity_id):
        flag = self.similarity_repo.get_by_id(similarity_id)
        if not flag:
            raise ValidationError("Similarity flag not found")
        return self.comparison_repo.list_by_similarity(similarity_id)

    # ------------------------------------------------------------------
    # REVIEW FLAG
    # ------------------------------------------------------------------
    def review_flag(self, user, flag_id, review_notes=None):
        """
        Mark flag as reviewed.
        Only instructor who owns the course or an admin can review.
        """
        flag = self.similarity_repo.get_by_id(flag_id)
        if not flag:
            raise ValidationError("Similarity flag not found")

        # permission check
        if user.role == "instructor":
            self._verify_instructor_permission(user.get_id(), flag)
        elif user.role != "admin":
            raise AuthError("Only instructors or admins can review flags")

        reviewed_at = datetime.now()

        return self.similarity_repo.mark_reviewed(
            id=flag_id,
            reviewer_id=user.get_id(),
            review_notes=review_notes,
            reviewed_at=reviewed_at
        )

    # ------------------------------------------------------------------
    # DISMISS FLAG
    # ------------------------------------------------------------------
    def dismiss_flag(self, user, flag_id):
        flag = self.similarity_repo.get_by_id(flag_id)
        if not flag:
            raise ValidationError("Similarity flag not found")

        if user.role == "instructor":
            self._verify_instructor_permission(user.get_id(), flag)
        elif user.role != "admin":
            raise AuthError("Only instructors or admins can dismiss flags")

        return self.similarity_repo.dismiss(
            id=flag_id,
            reviewer_id=user.get_id(),
            reviewed_at=datetime.now()
        )

    # ------------------------------------------------------------------
    # ESCALATE FLAG
    # ------------------------------------------------------------------
    def escalate_flag(self, user, flag_id):
        flag = self.similarity_repo.get_by_id(flag_id)
        if not flag:
            raise ValidationError("Similarity flag not found")

        if user.role == "instructor":
            self._verify_instructor_permission(user.get_id(), flag)
        elif user.role != "admin":
            raise AuthError("Only instructors or admins can escalate flags")

        return self.similarity_repo.escalate(
            id=flag_id,
            reviewer_id=user.get_id(),
            reviewed_at=datetime.now()
        )

    # ------------------------------------------------------------------
    # LIST ALL UNREVIEWED FLAGS
    # ------------------------------------------------------------------
    def list_unreviewed(self, user):
        """Admin sees all, instructor sees only their own course flags."""

        if user.role == "admin":
            return self.similarity_repo.list_unreviewed(limit=200)

        if user.role == "instructor":
            flags = self.similarity_repo.list_unreviewed(limit=200)
            filtered = []

            for flag in flags:
                try:
                    self._verify_instructor_permission(user.get_id(), flag)
                    filtered.append(flag)
                except AuthError:
                    continue  # skip unrelated courses

            return filtered

        raise AuthError("Students cannot view similarity flags")
