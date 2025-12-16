import pytest
from unittest.mock import Mock
from core.services.similarity_flag_service import Similarity_flag_Service
from core.exceptions.auth_error import AuthError
from core.exceptions.validation_error import ValidationError


@pytest.fixture
def mock_similarity_repo():
    return Mock()


@pytest.fixture
def mock_comparison_repo():
    return Mock()


@pytest.fixture
def mock_submission_repo():
    return Mock()


@pytest.fixture
def mock_assignment_repo():
    return Mock()


@pytest.fixture
def mock_course_repo():
    return Mock()


@pytest.fixture
def similarity_flag_service(mock_similarity_repo, mock_comparison_repo,
                             mock_submission_repo, mock_assignment_repo, mock_course_repo):
    return Similarity_flag_Service(
        similarity_repo=mock_similarity_repo,
        comparison_repo=mock_comparison_repo,
        submission_repo=mock_submission_repo,
        assignment_repo=mock_assignment_repo,
        course_repo=mock_course_repo
    )


@pytest.fixture
def instructor_user():
    user = Mock()
    user.role = "instructor"
    user.get_id.return_value = 10
    return user


@pytest.fixture
def admin_user():
    user = Mock()
    user.role = "admin"
    user.get_id.return_value = 1
    return user


@pytest.fixture
def student_user():
    user = Mock()
    user.role = "student"
    user.get_id.return_value = 5
    return user


def setup_instructor_permission(mock_submission_repo, mock_assignment_repo, 
                                  mock_course_repo, instructor_id=10):
    """Setup mocks for instructor permission check"""
    submission = Mock()
    submission.get_assignment_id.return_value = 1
    mock_submission_repo.get_by_id.return_value = submission

    assignment = Mock()
    assignment.get_course_id.return_value = 1
    mock_assignment_repo.get_by_id.return_value = assignment

    course = Mock()
    course.get_instructor_id.return_value = instructor_id
    mock_course_repo.get_by_id.return_value = course


class TestSimilarityFlagService:
    """Test suite for Similarity_flag_Service"""

    def test_create_flag_success(self, similarity_flag_service, mock_submission_repo, 
                                  mock_similarity_repo):
        """Test creating a similarity flag"""
        mock_submission_repo.get_by_id.return_value = Mock()
        mock_similarity_repo.create.return_value = Mock()

        result = similarity_flag_service.create_flag(
            submission_id=1,
            similarity_score=0.85,
            highlighted_spans=None
        )

        mock_similarity_repo.create.assert_called_once()

    def test_create_flag_submission_not_found(self, similarity_flag_service, mock_submission_repo):
        """Submission not found raises ValidationError"""
        mock_submission_repo.get_by_id.return_value = None

        with pytest.raises(ValidationError, match="Submission not found"):
            similarity_flag_service.create_flag(1, 0.85)

    def test_add_comparison_success(self, similarity_flag_service, mock_similarity_repo, 
                                     mock_comparison_repo):
        """Test adding a comparison to a flag"""
        mock_similarity_repo.get_by_id.return_value = Mock()
        mock_comparison_repo.create.return_value = Mock()

        result = similarity_flag_service.add_comparison(
            similarity_id=1,
            compared_submission_id=2,
            match_score=0.9,
            note="High match",
            segments=None
        )

        mock_comparison_repo.create.assert_called_once()

    def test_add_comparison_flag_not_found(self, similarity_flag_service, mock_similarity_repo):
        """Flag not found raises ValidationError"""
        mock_similarity_repo.get_by_id.return_value = None

        with pytest.raises(ValidationError, match="Similarity flag not found"):
            similarity_flag_service.add_comparison(999, 2, 0.9, None, None)

    def test_get_comparisons(self, similarity_flag_service, mock_similarity_repo, 
                              mock_comparison_repo):
        """Test getting comparisons for a flag"""
        mock_similarity_repo.get_by_id.return_value = Mock()
        comparisons = [Mock(), Mock()]
        mock_comparison_repo.list_by_similarity.return_value = comparisons

        result = similarity_flag_service.get_comparisons(1)

        assert result == comparisons

    def test_review_flag_as_instructor(self, similarity_flag_service, instructor_user,
                                        mock_similarity_repo, mock_submission_repo,
                                        mock_assignment_repo, mock_course_repo):
        """Instructor can review flag for their course"""
        flag = Mock()
        flag.get_submission_id.return_value = 1
        mock_similarity_repo.get_by_id.return_value = flag
        setup_instructor_permission(mock_submission_repo, mock_assignment_repo, mock_course_repo)
        mock_similarity_repo.mark_reviewed.return_value = flag

        result = similarity_flag_service.review_flag(instructor_user, 1, "Reviewed - false positive")

        mock_similarity_repo.mark_reviewed.assert_called_once()

    def test_review_flag_as_admin(self, similarity_flag_service, admin_user, mock_similarity_repo):
        """Admin can review any flag"""
        flag = Mock()
        mock_similarity_repo.get_by_id.return_value = flag
        mock_similarity_repo.mark_reviewed.return_value = flag

        result = similarity_flag_service.review_flag(admin_user, 1, "Admin reviewed")

        mock_similarity_repo.mark_reviewed.assert_called_once()

    def test_review_flag_student_denied(self, similarity_flag_service, student_user, mock_similarity_repo):
        """Students cannot review flags"""
        flag = Mock()
        mock_similarity_repo.get_by_id.return_value = flag

        with pytest.raises(AuthError, match="Only instructors or admins can review flags"):
            similarity_flag_service.review_flag(student_user, 1)

    def test_dismiss_flag(self, similarity_flag_service, admin_user, mock_similarity_repo):
        """Test dismissing a flag"""
        flag = Mock()
        mock_similarity_repo.get_by_id.return_value = flag
        mock_similarity_repo.dismiss.return_value = flag

        result = similarity_flag_service.dismiss_flag(admin_user, 1)

        mock_similarity_repo.dismiss.assert_called_once()

    def test_escalate_flag(self, similarity_flag_service, admin_user, mock_similarity_repo):
        """Test escalating a flag"""
        flag = Mock()
        mock_similarity_repo.get_by_id.return_value = flag
        mock_similarity_repo.escalate.return_value = flag

        result = similarity_flag_service.escalate_flag(admin_user, 1)

        mock_similarity_repo.escalate.assert_called_once()

    def test_list_unreviewed_as_admin(self, similarity_flag_service, admin_user, mock_similarity_repo):
        """Admin sees all unreviewed flags"""
        flags = [Mock(), Mock()]
        mock_similarity_repo.list_unreviewed.return_value = flags

        result = similarity_flag_service.list_unreviewed(admin_user)

        assert result == flags

    def test_list_unreviewed_as_student_denied(self, similarity_flag_service, student_user):
        """Students cannot view flags"""
        with pytest.raises(AuthError, match="Students cannot view similarity flags"):
            similarity_flag_service.list_unreviewed(student_user)
