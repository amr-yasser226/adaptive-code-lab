import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from core.services.sandbox_service import SandboxService
from core.entities.sandbox_job import SandboxJob


@pytest.fixture
def mock_sandbox_job_repo():
    """Create mock sandbox job repository."""
    repo = Mock()
    repo.create.return_value = SandboxJob(
        id=1, submission_id=100, status='queued'
    )
    repo.get_by_id.return_value = SandboxJob(
        id=1, submission_id=100, status='queued'
    )
    return repo


@pytest.fixture
def mock_submission_repo():
    """Create mock submission repository."""
    return Mock()


@pytest.fixture
def mock_groq_client():
    """Create mock Groq client for AI feedback."""
    client = Mock()
    client.generate_hint.return_value = "Try checking your syntax near line 5."
    return client


@pytest.fixture
def sandbox_service(mock_sandbox_job_repo, mock_submission_repo, mock_groq_client):
    """Create sandbox service with mocks."""
    return SandboxService(
        sandbox_job_repo=mock_sandbox_job_repo,
        submission_repo=mock_submission_repo,
        groq_client=mock_groq_client,
        timeout=5,
        memory_limit_mb=256,
        use_external_api=False  # Use subprocess for predictable testing
    )


@pytest.mark.unit
class TestSandboxService:
    
    def test_execute_simple_code(self, sandbox_service):
        """Test executing simple Python code."""
        result = sandbox_service.execute_code('print("Hello")')
        
        assert result['success'] is True
        assert 'Hello' in result['stdout']
        assert result['exit_code'] == 0
        assert result['timed_out'] is False
    
    def test_execute_code_with_syntax_error(self, sandbox_service):
        """Test executing code with syntax error."""
        result = sandbox_service.execute_code('print("Hello')
        
        assert result['success'] is False
        assert 'SyntaxError' in result['stderr'] or result['exit_code'] != 0
    
    def test_execute_code_with_stdin(self, sandbox_service):
        """Test executing code that reads stdin."""
        code = 'x = input(); print(f"Got: {x}")'
        result = sandbox_service.execute_code(code, stdin='test_input')
        
        assert result['success'] is True
        assert 'test_input' in result['stdout']
    
    def test_execute_code_timeout(self, sandbox_service):
        """Test that infinite loop times out."""
        # Create service with very short timeout
        sandbox_service.timeout = 1
        code = 'while True: pass'
        
        result = sandbox_service.execute_code(code, timeout=1)
        
        assert result['timed_out'] is True
        assert result['success'] is False
    
    def test_unsupported_language(self, sandbox_service):
        """Test unsupported language returns error."""
        result = sandbox_service.execute_code('console.log("hi")', language='javascript')
        
        # With subprocess fallback, only Python is supported
        assert result['success'] is False
        assert 'only supports Python' in result['stderr'] or 'not supported' in result['stderr']
    
    def test_run_test_case_pass(self, sandbox_service):
        """Test running a passing test case."""
        mock_test_case = Mock()
        mock_test_case.name = "Test Addition"
        mock_test_case.stdin = "5 3"
        mock_test_case.expected_out = "8"
        mock_test_case.timeout_seconds = 5  # Add timeout
        
        code = '''
a, b = map(int, input().split())
print(a + b)
'''
        result = sandbox_service.run_test_case(code, mock_test_case)
        
        assert result['test_name'] == "Test Addition"
        assert result['passed'] is True
        assert result['actual_output'] == "8"
    
    def test_run_test_case_fail(self, sandbox_service):
        """Test running a failing test case."""
        mock_test_case = Mock()
        mock_test_case.name = "Test Fail"
        mock_test_case.stdin = ""
        mock_test_case.expected_out = "expected"
        mock_test_case.timeout_seconds = 5  # Add timeout
        
        code = 'print("actual")'
        result = sandbox_service.run_test_case(code, mock_test_case)
        
        assert result['passed'] is False
        assert result['actual_output'] == 'actual'
        assert result['expected_output'] == 'expected'
    
    def test_run_all_tests(self, sandbox_service):
        """Test running multiple test cases."""
        tc1 = Mock()
        tc1.name = "Test 1"
        tc1.stdin = ""
        tc1.expected_out = "hello"
        tc1.points = 50
        tc1.timeout_seconds = 5  # Add timeout
        
        tc2 = Mock()
        tc2.name = "Test 2"
        tc2.stdin = ""
        tc2.expected_out = "hello"
        tc2.points = 50
        tc2.timeout_seconds = 5  # Add timeout
        
        code = 'print("hello")'
        result = sandbox_service.run_all_tests(code, [tc1, tc2])
        
        assert result['passed_count'] == 2
        assert result['total_count'] == 2
        assert result['score'] == 100.0
    
    def test_get_ai_feedback(self, sandbox_service, mock_groq_client):
        """Test AI feedback generation."""
        feedback = sandbox_service.get_ai_feedback(
            code='prnt("hello")',
            error_message='NameError: prnt is not defined'
        )
        
        assert feedback is not None
        mock_groq_client.generate_hint.assert_called_once()
    
    def test_get_ai_feedback_no_client(self, mock_sandbox_job_repo, mock_submission_repo):
        """Test AI feedback when no client configured."""
        service = SandboxService(
            sandbox_job_repo=mock_sandbox_job_repo,
            submission_repo=mock_submission_repo,
            groq_client=None  # No AI client
        )
        
        feedback = service.get_ai_feedback('code', 'error')
        assert feedback is None
    
    def test_create_job(self, sandbox_service, mock_sandbox_job_repo):
        """Test creating a sandbox job."""
        job = sandbox_service.create_job(submission_id=100)
        
        mock_sandbox_job_repo.create.assert_called_once()
        assert job.get_submission_id() == 100
    
    def test_get_job(self, sandbox_service, mock_sandbox_job_repo):
        """Test getting a sandbox job."""
        job = sandbox_service.get_job(1)
        
        mock_sandbox_job_repo.get_by_id.assert_called_with(1)
        assert job is not None
