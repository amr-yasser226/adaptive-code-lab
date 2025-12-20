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

    def test_get_jobs_for_submission(self, sandbox_service, mock_sandbox_job_repo):
        """Test getting all jobs for a submission (covers line 338)"""
        mock_sandbox_job_repo.get_by_submission.return_value = []
        result = sandbox_service.get_jobs_for_submission(100)
        assert result == []
        mock_sandbox_job_repo.get_by_submission.assert_called_with(100)

    @patch('requests.post')
    def test_execute_via_piston_success(self, mock_post, sandbox_service):
        """Test successful Piston API execution"""
        sandbox_service.use_external_api = True
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'run': {'stdout': 'hello\n', 'stderr': '', 'code': 0}
        }
        mock_post.return_value = mock_response
        
        result = sandbox_service.execute_code('print("hello")', language='python')
        assert result['success'] is True
        assert result['stdout'] == 'hello\n'

    @patch('requests.post')
    def test_execute_via_piston_api_error(self, mock_post, sandbox_service):
        """Test Piston API returning non-200 status"""
        sandbox_service.use_external_api = True
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        result = sandbox_service.execute_code('print("hello")', language='python')
        assert result['success'] is False
        assert 'API error: 500' in result['stderr']

    @patch('requests.post')
    def test_execute_via_piston_timeout(self, mock_post, sandbox_service):
        """Test Piston API timeout exception"""
        from requests.exceptions import Timeout
        sandbox_service.use_external_api = True
        mock_post.side_effect = Timeout()
        
        result = sandbox_service.execute_code('print("hello")', language='python')
        assert result['timed_out'] is True
        assert 'Request timed out' in result['stderr']

    @patch('requests.post')
    def test_execute_via_piston_fallback_on_exception(self, mock_post, sandbox_service):
        """Test falling back to subprocess on Piston API RequestException"""
        from requests.exceptions import RequestException
        sandbox_service.use_external_api = True
        mock_post.side_effect = RequestException("Network error")
        
        # This should fallback to subprocess (which works for python)
        result = sandbox_service.execute_code('print("hello")', language='python')
        assert result['success'] is True # Subprocess succeeded

    def test_execute_via_subprocess_error(self, sandbox_service):
        """Test subprocess execution error (covers lines 199-201)"""
        with patch('subprocess.Popen', side_effect=Exception("Execution failed")):
            result = sandbox_service.execute_code('print("hi")')
            assert result['success'] is False
            assert 'Execution failed' in result['stderr']

    def test_get_ai_feedback_error(self, sandbox_service, mock_groq_client):
        """Test AI feedback error handling (covers lines 317-319)"""
        mock_groq_client.generate_hint.side_effect = Exception("AI Crash")
        feedback = sandbox_service.get_ai_feedback("code", "error")
        assert feedback is None

    def test_execute_via_piston_unsupported_language(self, sandbox_service):
        """Line 58: Error for unsupported language in Piston"""
        result = sandbox_service._execute_via_piston("code", language="brainfuck")
        assert result["success"] is False
        assert "not supported" in result["stderr"]

    def test_execute_via_subprocess_unlink_error(self, sandbox_service):
        """Lines 212-213: Handle error during temporary file cleanup"""
        from unittest.mock import patch
        with patch("os.unlink", side_effect=Exception("Permission Denied")):
            # This should not crash despite unlink failure
            result = sandbox_service._execute_via_subprocess("print('hi')", language="python")
            assert result["success"] is True
            assert result["stdout"].strip() == "hi"

    def test_run_all_tests_no_points(self, sandbox_service):
        """Test scoring when test cases don't have points"""
        tc = Mock()
        # No .points attribute
        tc.name = "Test"
        tc.stdin = ""
        tc.expected_out = "hi"
        tc.timeout_seconds = 5
        
        if hasattr(tc, 'points'):
            del tc.points # Ensure it doesn't have it
        
        code = 'print("hi")'
        result = sandbox_service.run_all_tests(code, [tc])
        assert result['score'] == 100.0

    def test_run_all_tests_empty(self, sandbox_service):
        """Test scoring with no test cases"""
        result = sandbox_service.run_all_tests("code", [])
        assert result['score'] == 0.0
