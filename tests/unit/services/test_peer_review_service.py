import pytest
from unittest.mock import Mock
from core.services.peer_review_service import PeerReviewService
from core.exceptions.auth_error import AuthError
from core.exceptions.validation_error import ValidationError


@pytest.fixture
def mock_peer_review_repo():
    return Mock()


@pytest.fixture
def mock_submission_repo():
    return Mock()


@pytest.fixture
def mock_enrollment_repo():
    return Mock()


@pytest.fixture
def mock_assignment_repo():
    return Mock()


@pytest.fixture
def mock_course_repo():
    return Mock()


@pytest.fixture
def peer_review_service(mock_peer_review_repo, mock_submission_repo, 
                        mock_enrollment_repo, mock_assignment_repo, mock_course_repo):
    return PeerReviewService(
        peer_review_repo=mock_peer_review_repo,
        submission_repo=mock_submission_repo,
        enrollment_repo=mock_enrollment_repo,
        assignment_repo=mock_assignment_repo,
        course_repo=mock_course_repo
    )


@pytest.fixture
def student_reviewer():
    user = Mock()
    user.role = "student"
    user.get_id.return_value = 1
    return user


@pytest.fixture
def instructor_user():
    user = Mock()
    user.role = "instructor"
    user.get_id.return_value = 10
    return user


def setup_valid_submission(mock_submission_repo, mock_assignment_repo, 
                           mock_course_repo, mock_enrollment_repo, student_id=999):
    """Helper to setup valid submission chain"""
    submission = Mock()
    submission.get_student_id.return_value = student_id
    submission.get_assignment_id.return_value = 1
    mock_submission_repo.get_by_id.return_value = submission

    assignment = Mock()
    assignment.get_course_id.return_value = 1
    mock_assignment_repo.get_by_id.return_value = assignment

    course = Mock()
    course.get_id.return_value = 1
    course.get_instructor_id.return_value = 10
    mock_course_repo.get_by_id.return_value = course

    enrollment = Mock()
    enrollment.status = "enrolled"
    mock_enrollment_repo.get.return_value = enrollment

    return submission, assignment, course


class TestPeerReviewService:
    """Test suite for PeerReviewService"""

    def test_create_review_success(self, peer_review_service, student_reviewer,
                                   mock_submission_repo, mock_assignment_repo,
                                   mock_course_repo, mock_enrollment_repo,
                                   mock_peer_review_repo):
        """Test successful review creation"""
        setup_valid_submission(
            mock_submission_repo, mock_assignment_repo, 
            mock_course_repo, mock_enrollment_repo
        )
        mock_peer_review_repo.get.return_value = None
        mock_peer_review_repo.create.return_value = Mock()

        result = peer_review_service.create_review(
            reviewer_student=student_reviewer,
            submission_id=1,
            rubric_score={"quality": 4},
            comments="Good work"
        )

        mock_peer_review_repo.create.assert_called_once()

    def test_create_review_non_student_denied(self, peer_review_service, instructor_user):
        """Non-students cannot create reviews"""
        with pytest.raises(AuthError, match="Only students can create peer reviews"):
            peer_review_service.create_review(instructor_user, 1)

    def test_create_review_self_review_denied(self, peer_review_service, student_reviewer,
                                               mock_submission_repo, mock_assignment_repo,
                                               mock_course_repo, mock_enrollment_repo):
        """Students cannot review their own submission"""
        setup_valid_submission(
            mock_submission_repo, mock_assignment_repo, 
            mock_course_repo, mock_enrollment_repo,
            student_id=1  # Same as reviewer
        )

        with pytest.raises(ValidationError, match="You cannot review your own submission"):
            peer_review_service.create_review(student_reviewer, 1)

    def test_create_review_already_exists(self, peer_review_service, student_reviewer,
                                           mock_submission_repo, mock_assignment_repo,
                                           mock_course_repo, mock_enrollment_repo,
                                           mock_peer_review_repo):
        """Cannot create duplicate review"""
        setup_valid_submission(
            mock_submission_repo, mock_assignment_repo, 
            mock_course_repo, mock_enrollment_repo
        )
        mock_peer_review_repo.get.return_value = Mock()

        with pytest.raises(ValidationError, match="Peer review already exists"):
            peer_review_service.create_review(student_reviewer, 1)

    def test_update_review_success(self, peer_review_service, student_reviewer, mock_peer_review_repo):
        """Test successful review update"""
        review = Mock()
        review.is_submitted = False
        mock_peer_review_repo.get.return_value = review
        mock_peer_review_repo.update.return_value = review

        result = peer_review_service.update_review(
            student_reviewer, 1, 
            rubric_score={"quality": 5}, 
            comments="Updated"
        )

        review.update_review.assert_called_once()
        mock_peer_review_repo.update.assert_called_once()

    def test_update_review_not_found(self, peer_review_service, student_reviewer, mock_peer_review_repo):
        """Review not found raises ValidationError"""
        mock_peer_review_repo.get.return_value = None

        with pytest.raises(ValidationError, match="Peer review not found"):
            peer_review_service.update_review(student_reviewer, 1)

    def test_update_review_already_submitted(self, peer_review_service, student_reviewer, mock_peer_review_repo):
        """Cannot edit submitted review"""
        review = Mock()
        review.is_submitted = True
        mock_peer_review_repo.get.return_value = review

        with pytest.raises(ValidationError, match="Cannot edit a submitted review"):
            peer_review_service.update_review(student_reviewer, 1)

    def test_submit_review_success(self, peer_review_service, student_reviewer, mock_peer_review_repo):
        """Test successful review submission"""
        review = Mock()
        review.is_submitted = False
        review.rubric_score = {"quality": 5}
        mock_peer_review_repo.get.return_value = review
        mock_peer_review_repo.update.return_value = review

        result = peer_review_service.submit_review(student_reviewer, 1)

        review.submit_review.assert_called_once()

    def test_submit_review_no_score(self, peer_review_service, student_reviewer, mock_peer_review_repo):
        """Cannot submit without rubric score"""
        review = Mock()
        review.is_submitted = False
        review.rubric_score = None
        mock_peer_review_repo.get.return_value = review

        with pytest.raises(ValidationError, match="Rubric score is required"):
            peer_review_service.submit_review(student_reviewer, 1)

    def test_calculate_peer_average(self, peer_review_service, mock_peer_review_repo):
        """Test calculating peer average score"""
        review1 = Mock()
        review1.is_submitted = True
        review1.calculate_rubric_score.return_value = 80

        review2 = Mock()
        review2.is_submitted = True
        review2.calculate_rubric_score.return_value = 90

        mock_peer_review_repo.list_by_submission.return_value = [review1, review2]

        result = peer_review_service.calculate_peer_average(1)

        assert result == 85.0

    def test_calculate_peer_average_no_reviews(self, peer_review_service, mock_peer_review_repo):
        """Average with no reviews returns 0 (covers line 164)"""
        mock_peer_review_repo.list_by_submission.return_value = []
        result = peer_review_service.calculate_peer_average(1)
        assert result == 0.0

    def test_calculate_peer_average_no_submitted_scores(self, peer_review_service, mock_peer_review_repo):
        """Average with no submitted reviews returns 0 (covers line 173)"""
        review = Mock()
        review.is_submitted = False
        mock_peer_review_repo.list_by_submission.return_value = [review]

        result = peer_review_service.calculate_peer_average(1)

        assert result == 0.0

    def test_verify_student_enrolled_denied(self, peer_review_service, mock_enrollment_repo):
        """Line 28: AuthError when student is not enrolled"""
        mock_enrollment_repo.get.return_value = None
        with pytest.raises(AuthError, match="not enrolled"):
            peer_review_service._verify_student_enrolled(5, 1)

    def test_verify_submission_exists_not_found(self, peer_review_service, mock_submission_repo):
        """Line 33: ValidationError when submission not found"""
        mock_submission_repo.get_by_id.return_value = None
        with pytest.raises(ValidationError, match="Submission not found"):
            peer_review_service._verify_submission_exists(999)

    def test_verify_assignment_course_assignment_not_found(self, peer_review_service, mock_assignment_repo):
        """Line 41: ValidationError when assignment not found"""
        sub = Mock()
        sub.get_assignment_id.return_value = 1
        mock_assignment_repo.get_by_id.return_value = None
        with pytest.raises(ValidationError, match="Assignment not found"):
            peer_review_service._verify_assignment_course(sub)

    def test_verify_assignment_course_course_not_found(self, peer_review_service, mock_assignment_repo, mock_course_repo):
        """Line 45: ValidationError when course not found"""
        sub = Mock()
        sub.get_assignment_id.return_value = 1
        mock_assignment_repo.get_by_id.return_value = Mock(get_course_id=lambda: 1)
        mock_course_repo.get_by_id.return_value = None
        with pytest.raises(ValidationError, match="Course not found"):
            peer_review_service._verify_assignment_course(sub)

    def test_submit_review_not_found(self, peer_review_service, student_reviewer, mock_peer_review_repo):
        """Line 126: ValidationError when review to submit is not found"""
        mock_peer_review_repo.get.return_value = None
        with pytest.raises(ValidationError, match="Peer review not found"):
            peer_review_service.submit_review(student_reviewer, 1)

    def test_submit_review_already_submitted(self, peer_review_service, student_reviewer, mock_peer_review_repo):
        """Line 129: ValidationError when review is already submitted"""
        review = Mock()
        review.is_submitted = True
        mock_peer_review_repo.get.return_value = review
        with pytest.raises(ValidationError, match="already submitted"):
            peer_review_service.submit_review(student_reviewer, 1)

    def test_list_reviews_for_submission_instructor(self, peer_review_service, instructor_user, 
                                                   mock_submission_repo, mock_assignment_repo, 
                                                   mock_course_repo, mock_peer_review_repo):
        """Lines 145-148: Instructor listing reviews success and failure"""
        setup_valid_submission(mock_submission_repo, mock_assignment_repo, mock_course_repo, Mock())
        
        # Unauthorized (not owner)
        instructor_user.get_id.return_value = 99
        with pytest.raises(AuthError, match="Not authorized"):
            peer_review_service.list_reviews_for_submission(instructor_user, 1)
            
        # Authorized
        instructor_user.get_id.return_value = 10
        mock_peer_review_repo.list_by_submission.return_value = []
        result = peer_review_service.list_reviews_for_submission(instructor_user, 1)
        assert result == []

    def test_list_reviews_for_submission_student(self, peer_review_service, student_reviewer, 
                                                mock_submission_repo, mock_assignment_repo, 
                                                mock_course_repo, mock_peer_review_repo):
        """Lines 151-154: Student listing reviews success and failure"""
        setup_valid_submission(mock_submission_repo, mock_assignment_repo, mock_course_repo, Mock(), student_id=5)
        
        # Unauthorized (not their submission)
        student_reviewer.get_id.return_value = 99
        with pytest.raises(AuthError, match="cannot view reviews"):
            peer_review_service.list_reviews_for_submission(student_reviewer, 1)
            
        # Authorized
        student_reviewer.get_id.return_value = 5
        mock_peer_review_repo.list_by_submission.return_value = []
        result = peer_review_service.list_reviews_for_submission(student_reviewer, 1)
        assert result == []

    def test_list_reviews_for_submission_invalid_role(self, peer_review_service, mock_submission_repo, 
                                                     mock_assignment_repo, mock_course_repo):
        """Line 156: AuthError for invalid role"""
        setup_valid_submission(mock_submission_repo, mock_assignment_repo, mock_course_repo, Mock())
        user = Mock()
        user.role = "guest"
        with pytest.raises(AuthError, match="Unauthorized access"):
            peer_review_service.list_reviews_for_submission(user, 1)
