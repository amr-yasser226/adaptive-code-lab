import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from core.services.remediation_service import RemediationService, FAILURE_PATTERNS
from core.entities.remediation import Remediation, StudentRemediation


@pytest.fixture
def mock_remediation_repo():
    """Create mock remediation repository."""
    repo = Mock()
    
    # Default behaviors
    repo.find_by_pattern.return_value = [
        Remediation(
            id=1,
            failure_pattern='syntax_error',
            resource_title='Python Syntax Basics',
            resource_type='article',
            resource_url='https://docs.python.org',
            resource_content='Learn Python syntax',
            difficulty_level='beginner'
        )
    ]
    repo.get_by_id.return_value = Remediation(
        id=1,
        failure_pattern='syntax_error',
        resource_title='Python Syntax Basics'
    )
    repo.get_student_remediation.return_value = None  # No existing recommendation
    repo.create_student_remediation.return_value = StudentRemediation(
        id=1, student_id=100, remediation_id=1
    )
    repo.list_student_remediations.return_value = []
    
    return repo


@pytest.fixture
def mock_result_repo():
    """Create mock result repository."""
    repo = Mock()
    repo.find_by_submission.return_value = []
    return repo


@pytest.fixture
def mock_submission_repo():
    """Create mock submission repository."""
    return Mock()


@pytest.fixture
def remediation_service(mock_remediation_repo, mock_result_repo, mock_submission_repo):
    """Create remediation service with mocks."""
    return RemediationService(
        remediation_repo=mock_remediation_repo,
        result_repo=mock_result_repo,
        submission_repo=mock_submission_repo
    )


@pytest.mark.unit
class TestRemediationService:
    
    def test_detect_syntax_error_pattern(self, remediation_service):
        """Test detecting syntax error pattern."""
        error = "SyntaxError: invalid syntax at line 5"
        pattern = remediation_service.detect_failure_pattern(error)
        
        assert pattern == 'syntax_error'
    
    def test_detect_name_error_pattern(self, remediation_service):
        """Test detecting name error pattern."""
        error = "NameError: name 'undefined_var' is not defined"
        pattern = remediation_service.detect_failure_pattern(error)
        
        assert pattern == 'name_error'
    
    def test_detect_timeout_pattern(self, remediation_service):
        """Test detecting timeout pattern."""
        error = "Execution timed out after 5 seconds"
        pattern = remediation_service.detect_failure_pattern(error)
        
        assert pattern == 'timeout'
    
    def test_detect_type_error_pattern(self, remediation_service):
        """Test detecting type error pattern."""
        error = "TypeError: unsupported operand type(s)"
        pattern = remediation_service.detect_failure_pattern(error)
        
        assert pattern == 'type_error'
    
    def test_detect_index_error_pattern(self, remediation_service):
        """Test detecting index error pattern."""
        error = "IndexError: list index out of range"
        pattern = remediation_service.detect_failure_pattern(error)
        
        assert pattern == 'index_error'
    
    def test_detect_generic_runtime_error(self, remediation_service):
        """Test detecting generic runtime error."""
        error = "Some unknown error occurred"
        pattern = remediation_service.detect_failure_pattern(error)
        
        assert pattern == 'runtime_error'
    
    def test_detect_no_pattern_empty_string(self, remediation_service):
        """Test no pattern detected for empty string."""
        pattern = remediation_service.detect_failure_pattern("")
        assert pattern is None
    
    def test_detect_no_pattern_none(self, remediation_service):
        """Test no pattern detected for None."""
        pattern = remediation_service.detect_failure_pattern(None)
        assert pattern is None

    def test_detect_failure_pattern_no_match(self, remediation_service):
        """Test returning None when no patterns match and no generic error keyword."""
        pattern = remediation_service.detect_failure_pattern("Everything is fine")
        assert pattern is None
    
    def test_get_recommendations(self, remediation_service, mock_remediation_repo):
        """Test getting recommendations for a pattern."""
        recommendations = remediation_service.get_recommendations('syntax_error')
        
        mock_remediation_repo.find_by_pattern.assert_called_with('syntax_error')
        assert len(recommendations) > 0
        assert recommendations[0].failure_pattern == 'syntax_error'
    
    def test_recommend_for_student_new(self, remediation_service, mock_remediation_repo):
        """Test creating new recommendations for a student."""
        recommendations = remediation_service.recommend_for_student(
            student_id=100,
            submission_id=200,
            patterns=['syntax_error']
        )
        
        assert len(recommendations) > 0
        assert recommendations[0]['is_new'] is True
        mock_remediation_repo.create_student_remediation.assert_called()
    
    def test_recommend_for_student_existing(self, remediation_service, mock_remediation_repo):
        """Test recommendations when student already has one."""
        # Setup: student already has this remediation
        mock_remediation_repo.get_student_remediation.return_value = StudentRemediation(
            id=1, student_id=100, remediation_id=1, is_viewed=True
        )
        
        recommendations = remediation_service.recommend_for_student(
            student_id=100,
            submission_id=200,
            patterns=['syntax_error']
        )
        
        assert len(recommendations) > 0
        assert recommendations[0]['is_new'] is False
        assert recommendations[0]['is_viewed'] is True
    
    def test_recommend_for_student_empty_patterns(self, remediation_service):
        """Test empty recommendations when no patterns."""
        recommendations = remediation_service.recommend_for_student(
            student_id=100,
            submission_id=200,
            patterns=[]
        )
        
        assert recommendations == []

    def test_recommend_for_student_detect_patterns(self, remediation_service, mock_result_repo):
        """Test that recommend_for_student calls analyze_submission_results if patterns is None."""
        mock_result = Mock()
        mock_result.passed = False
        mock_result.stderr = "SyntaxError"
        mock_result.error_message = None
        mock_result_repo.find_by_submission.return_value = [mock_result]
        
        recommendations = remediation_service.recommend_for_student(
            student_id=100,
            submission_id=200,
            patterns=None
        )
        
        assert len(recommendations) > 0
        mock_result_repo.find_by_submission.assert_called_with(200)

    def test_analyze_submission_results_no_repo(self):
        """Test analyze_submission_results when result_repo is None."""
        service = RemediationService(remediation_repo=Mock(), result_repo=None)
        assert service.analyze_submission_results(1) == []

    def test_analyze_submission_results_error_message(self, remediation_service, mock_result_repo):
        """Test analyze_submission_results checks error_message if stderr is empty."""
        mock_result = Mock()
        mock_result.passed = False
        mock_result.stderr = ""
        mock_result.error_message = "NameError"
        mock_result_repo.find_by_submission.return_value = [mock_result]
        
        patterns = remediation_service.analyze_submission_results(1)
        assert "name_error" in patterns
    
    def test_get_student_remediations(self, remediation_service, mock_remediation_repo):
        """Test getting student's remediations."""
        mock_remediation_repo.list_student_remediations.return_value = [
            StudentRemediation(id=1, student_id=100, remediation_id=1)
        ]
        
        result = remediation_service.get_student_remediations(100)
        
        mock_remediation_repo.list_student_remediations.assert_called_with(100, False)
        assert len(result) > 0
    
    def test_get_student_remediations_only_pending(self, remediation_service, mock_remediation_repo):
        """Test getting only pending remediations."""
        remediation_service.get_student_remediations(100, only_pending=True)
        
        mock_remediation_repo.list_student_remediations.assert_called_with(100, True)
    
    def test_mark_viewed(self, remediation_service, mock_remediation_repo):
        """Test marking remediation as viewed."""
        sr = StudentRemediation(id=1, student_id=100, remediation_id=1)
        mock_remediation_repo.get_student_remediation_by_id.return_value = sr
        mock_remediation_repo.update_student_remediation.return_value = sr
        
        result = remediation_service.mark_viewed(100, 1)
        
        assert result.is_viewed is True
        mock_remediation_repo.update_student_remediation.assert_called()
    
    def test_mark_viewed_wrong_student(self, remediation_service, mock_remediation_repo):
        """Test marking viewed fails for wrong student."""
        sr = StudentRemediation(id=1, student_id=100, remediation_id=1)
        mock_remediation_repo.get_student_remediation_by_id.return_value = sr
        
        from core.exceptions.validation_error import ValidationError
        with pytest.raises(ValidationError, match="Not authorized"):
            remediation_service.mark_viewed(999, 1)  # Wrong student
    
    def test_mark_completed(self, remediation_service, mock_remediation_repo):
        """Test marking remediation as completed."""
        sr = StudentRemediation(id=1, student_id=100, remediation_id=1)
        mock_remediation_repo.get_student_remediation_by_id.return_value = sr
        mock_remediation_repo.update_student_remediation.return_value = sr
        
        result = remediation_service.mark_completed(100, 1)
        
        assert result.is_completed is True
        mock_remediation_repo.update_student_remediation.assert_called()

    def test_mark_viewed_not_found(self, remediation_service, mock_remediation_repo):
        """Test mark_viewed raises ValidationError if not found."""
        mock_remediation_repo.get_student_remediation_by_id.return_value = None
        from core.exceptions.validation_error import ValidationError
        with pytest.raises(ValidationError, match="not found"):
            remediation_service.mark_viewed(1, 1)

    def test_mark_completed_not_found(self, remediation_service, mock_remediation_repo):
        """Test mark_completed raises ValidationError if not found."""
        mock_remediation_repo.get_student_remediation_by_id.return_value = None
        from core.exceptions.validation_error import ValidationError
        with pytest.raises(ValidationError, match="not found"):
            remediation_service.mark_completed(1, 1)

    def test_mark_completed_unauthorized(self, remediation_service, mock_remediation_repo):
        """Test mark_completed raises ValidationError if unauthorized."""
        sr = StudentRemediation(id=1, student_id=100, remediation_id=1)
        mock_remediation_repo.get_student_remediation_by_id.return_value = sr
        from core.exceptions.validation_error import ValidationError
        with pytest.raises(ValidationError, match="Not authorized"):
            remediation_service.mark_completed(999, 1)

    def test_get_all_remediations(self, remediation_service, mock_remediation_repo):
        """Test getting all generic remediation resources."""
        mock_remediation_repo.get_all.return_value = []
        result = remediation_service.get_all_remediations()
        assert result == []
        mock_remediation_repo.get_all.assert_called_once()
    
    def test_create_remediation(self, remediation_service, mock_remediation_repo):
        """Test creating a new remediation resource."""
        mock_remediation_repo.create.return_value = Remediation(
            id=10,
            failure_pattern='new_pattern',
            resource_title='New Resource'
        )
        
        result = remediation_service.create_remediation(
            failure_pattern='new_pattern',
            resource_title='New Resource',
            resource_type='video',
            difficulty_level='intermediate'
        )
        
        mock_remediation_repo.create.assert_called()
        assert result.get_id() == 10


@pytest.mark.unit
class TestFailurePatterns:
    """Test that all expected failure patterns are defined."""
    
    def test_syntax_error_patterns_exist(self):
        """Test syntax error patterns are defined."""
        assert 'syntax_error' in FAILURE_PATTERNS
        assert 'SyntaxError' in FAILURE_PATTERNS['syntax_error']
    
    def test_name_error_patterns_exist(self):
        """Test name error patterns are defined."""
        assert 'name_error' in FAILURE_PATTERNS
        assert 'NameError' in FAILURE_PATTERNS['name_error']
    
    def test_timeout_patterns_exist(self):
        """Test timeout patterns are defined."""
        assert 'timeout' in FAILURE_PATTERNS
        assert 'timed out' in FAILURE_PATTERNS['timeout']
