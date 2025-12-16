import pytest
from unittest.mock import Mock
from core.services.similarity_service import SimilarityService
from core.exceptions.validation_error import ValidationError


@pytest.fixture
def mock_embedding_service():
    return Mock()


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
def similarity_service(mock_embedding_service, mock_similarity_repo, 
                       mock_comparison_repo, mock_submission_repo):
    return SimilarityService(
        embedding_service=mock_embedding_service,
        similarity_repo=mock_similarity_repo,
        comparison_repo=mock_comparison_repo,
        submission_repo=mock_submission_repo,
        threshold=0.85
    )


class TestSimilarityService:
    """Test suite for SimilarityService"""

    def test_compute_cosine_similarity(self, similarity_service):
        """Test cosine similarity calculation"""
        vec_a = [1.0, 0.0, 0.0]
        vec_b = [1.0, 0.0, 0.0]

        result = similarity_service._compute_cosine_similarity(vec_a, vec_b)

        assert result == 1.0  # Identical vectors

    def test_compute_cosine_similarity_orthogonal(self, similarity_service):
        """Orthogonal vectors have 0 similarity"""
        vec_a = [1.0, 0.0, 0.0]
        vec_b = [0.0, 1.0, 0.0]

        result = similarity_service._compute_cosine_similarity(vec_a, vec_b)

        assert result == 0.0

    def test_compute_cosine_similarity_zero_vector(self, similarity_service):
        """Zero vector returns 0 similarity"""
        vec_a = [0.0, 0.0, 0.0]
        vec_b = [1.0, 1.0, 1.0]

        result = similarity_service._compute_cosine_similarity(vec_a, vec_b)

        assert result == 0.0

    def test_analyze_submission_success(self, similarity_service, mock_submission_repo,
                                         mock_embedding_service, mock_comparison_repo):
        """Test analyzing submission with no high similarity"""
        submission = Mock()
        submission.get_id.return_value = 1
        submission.get_assignment_id.return_value = 1
        mock_submission_repo.get_by_id.return_value = submission

        # No other submissions (only same submission returned)
        mock_submission_repo.list_by_assignment.return_value = [submission]
        mock_embedding_service.get_embedding_vector.return_value = [0.1, 0.2, 0.3]

        result = similarity_service.analyze_submission(1)

        assert result["submission_id"] == 1
        assert result["comparisons"] == []
        assert result["flag_created"] is None

    def test_analyze_submission_not_found(self, similarity_service, mock_submission_repo):
        """Submission not found raises ValidationError"""
        mock_submission_repo.get_by_id.return_value = None

        with pytest.raises(ValidationError, match="Submission not found"):
            similarity_service.analyze_submission(999)

    def test_analyze_submission_no_embedding(self, similarity_service, mock_submission_repo,
                                              mock_embedding_service):
        """Missing embedding raises ValidationError"""
        submission = Mock()
        submission.get_assignment_id.return_value = 1
        mock_submission_repo.get_by_id.return_value = submission
        mock_embedding_service.get_embedding_vector.return_value = None

        with pytest.raises(ValidationError, match="Embedding for submission not found"):
            similarity_service.analyze_submission(1)

    def test_analyze_submission_creates_flag_for_high_similarity(
        self, similarity_service, mock_submission_repo, mock_embedding_service,
        mock_comparison_repo, mock_similarity_repo
    ):
        """High similarity creates a flag"""
        submission1 = Mock()
        submission1.get_id.return_value = 1
        submission1.get_assignment_id.return_value = 1

        submission2 = Mock()
        submission2.get_id.return_value = 2

        mock_submission_repo.get_by_id.return_value = submission1
        mock_submission_repo.list_by_assignment.return_value = [submission1, submission2]

        # High similarity vectors
        mock_embedding_service.get_embedding_vector.side_effect = [
            [1.0, 0.0, 0.0],  # submission1
            [0.99, 0.1, 0.0]  # submission2 - very similar
        ]

        mock_comparison_repo.create.return_value = Mock()
        flag = Mock()
        flag.get_id.return_value = 1
        mock_similarity_repo.create.return_value = flag

        result = similarity_service.analyze_submission(1)

        assert result["flag_created"] is not None
        mock_similarity_repo.create.assert_called_once()

    def test_analyze_submission_with_embedding_generation(
        self, similarity_service, mock_submission_repo, mock_embedding_service
    ):
        """Test generating embedding during analysis"""
        submission = Mock()
        submission.get_assignment_id.return_value = 1
        mock_submission_repo.get_by_id.return_value = submission
        mock_submission_repo.list_by_assignment.return_value = [submission]

        mock_embedding_service.ensure_embedding.return_value = [0.1, 0.2, 0.3]

        result = similarity_service.analyze_submission(
            1, 
            generate_embedding_if_missing=True,
            code_text_for_embedding="def foo(): pass"
        )

        mock_embedding_service.ensure_embedding.assert_called_once()
        assert result["submission_id"] == 1

    def test_analyze_submission_custom_threshold(self, similarity_service, mock_submission_repo,
                                                  mock_embedding_service):
        """Test with custom threshold"""
        submission = Mock()
        submission.get_assignment_id.return_value = 1
        mock_submission_repo.get_by_id.return_value = submission
        mock_submission_repo.list_by_assignment.return_value = [submission]
        mock_embedding_service.get_embedding_vector.return_value = [0.1, 0.2, 0.3]

        result = similarity_service.analyze_submission(1, threshold=0.95)

        assert result["threshold_used"] == 0.95
