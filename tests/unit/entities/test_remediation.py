import pytest
from datetime import datetime
from core.entities.remediation import Remediation, StudentRemediation


@pytest.mark.unit
class TestRemediationEntity:
    
    def test_create_remediation_default(self):
        """Test creating a remediation with default values."""
        rem = Remediation(
            id=1,
            failure_pattern='syntax_error',
            resource_title='Python Syntax Basics'
        )
        assert rem.get_id() == 1
        assert rem.failure_pattern == 'syntax_error'
        assert rem.resource_title == 'Python Syntax Basics'
        assert rem.resource_type == 'article'
        assert rem.difficulty_level == 'beginner'
        assert rem.language == 'python'
    
    def test_create_remediation_custom(self):
        """Test creating a remediation with custom values."""
        rem = Remediation(
            id=2,
            failure_pattern='timeout',
            resource_title='Algorithm Optimization',
            resource_type='video',
            resource_url='https://example.com/video',
            resource_content='Learn to optimize',
            difficulty_level='advanced',
            language='python'
        )
        assert rem.resource_type == 'video'
        assert rem.difficulty_level == 'advanced'
        assert rem.resource_url == 'https://example.com/video'
    
    def test_invalid_resource_type_raises_error(self):
        """Test that invalid resource type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid type"):
            Remediation(
                id=1,
                failure_pattern='syntax_error',
                resource_title='Test',
                resource_type='invalid_type'
            )
    
    def test_invalid_difficulty_level_raises_error(self):
        """Test that invalid difficulty level raises ValueError."""
        with pytest.raises(ValueError, match="Invalid level"):
            Remediation(
                id=1,
                failure_pattern='syntax_error',
                resource_title='Test',
                difficulty_level='expert'
            )
    
    def test_to_dict(self):
        """Test to_dict method."""
        rem = Remediation(
            id=1,
            failure_pattern='syntax_error',
            resource_title='Python Basics',
            resource_type='article',
            resource_url='https://docs.python.org',
            resource_content='Learn syntax',
            difficulty_level='beginner',
            language='python'
        )
        
        d = rem.to_dict()
        assert d['id'] == 1
        assert d['failure_pattern'] == 'syntax_error'
        assert d['resource_title'] == 'Python Basics'
        assert d['resource_url'] == 'https://docs.python.org'


@pytest.mark.unit
class TestStudentRemediationEntity:
    
    def test_create_student_remediation(self):
        """Test creating a student remediation."""
        sr = StudentRemediation(
            id=1,
            student_id=100,
            remediation_id=10,
            submission_id=200
        )
        assert sr.get_id() == 1
        assert sr.get_student_id() == 100
        assert sr.get_remediation_id() == 10
        assert sr.get_submission_id() == 200
        assert sr.is_viewed is False
        assert sr.is_completed is False
    
    def test_mark_viewed(self):
        """Test marking remediation as viewed."""
        sr = StudentRemediation(
            id=1,
            student_id=100,
            remediation_id=10
        )
        sr.mark_viewed()
        
        assert sr.is_viewed is True
        assert sr.viewed_at is not None
    
    def test_mark_completed(self):
        """Test marking remediation as completed."""
        sr = StudentRemediation(
            id=1,
            student_id=100,
            remediation_id=10
        )
        sr.mark_completed()
        
        assert sr.is_completed is True
        assert sr.completed_at is not None
        # Should also mark as viewed
        assert sr.is_viewed is True
    
    def test_mark_completed_when_already_viewed(self):
        """Test completing an already viewed remediation."""
        sr = StudentRemediation(
            id=1,
            student_id=100,
            remediation_id=10
        )
        sr.mark_viewed()
        original_viewed_at = sr.viewed_at
        
        sr.mark_completed()
        
        assert sr.is_completed is True
        # viewed_at should stay the same
        assert sr.viewed_at == original_viewed_at
