import subprocess
import tempfile
import os
import sys
import logging
import requests
from datetime import datetime
from typing import Optional, Dict, Any, List

from core.entities.sandbox_job import SandboxJob
from config.settings import SANDBOX_TIMEOUT, SANDBOX_MEMORY_LIMIT_MB, SANDBOX_PATH

logger = logging.getLogger(__name__)

# Piston API - Free public code execution API
PISTON_API_URL = os.getenv("PISTON_API_URL", "https://emkc.org/api/v2/piston")

# Language mapping for Piston API
PISTON_LANGUAGES = {
    'python': {'language': 'python', 'version': '3.10'},
    'javascript': {'language': 'javascript', 'version': '18.15.0'},
    'java': {'language': 'java', 'version': '15.0.2'},
    'cpp': {'language': 'cpp', 'version': '10.2.0'},
    'c': {'language': 'c', 'version': '10.2.0'}
}


class SandboxService:
    
    def __init__(
        self,
        sandbox_job_repo,
        submission_repo,
        result_service=None,
        groq_client=None,
        timeout: int = None,
        memory_limit_mb: int = None,
        use_external_api: bool = True
    ):
        self.sandbox_job_repo = sandbox_job_repo
        self.submission_repo = submission_repo
        self.result_service = result_service
        self.groq_client = groq_client  # For AI feedback on errors
        self.timeout = timeout or SANDBOX_TIMEOUT
        self.memory_limit_mb = memory_limit_mb or SANDBOX_MEMORY_LIMIT_MB
        self.use_external_api = use_external_api
        
        # Ensure sandbox directory exists (for fallback)
        os.makedirs(SANDBOX_PATH, exist_ok=True)
    
    def _execute_via_piston(
        self,
        code: str,
        language: str = 'python',
        stdin: str = ''
    ) -> Dict[str, Any]:
        if language not in PISTON_LANGUAGES:
            return {
                'success': False,
                'stdout': '',
                'stderr': f'Language {language} not supported. Supported: {list(PISTON_LANGUAGES.keys())}',
                'exit_code': 1,
                'runtime_ms': 0,
                'timed_out': False
            }
        
        lang_config = PISTON_LANGUAGES[language]
        
        payload = {
            'language': lang_config['language'],
            'version': lang_config['version'],
            'files': [{'content': code}],
            'stdin': stdin,
            'run_timeout': self.timeout * 1000  # ms
        }
        
        start_time = datetime.utcnow()
        
        try:
            response = requests.post(
                f"{PISTON_API_URL}/execute",
                json=payload,
                timeout=self.timeout + 5  # Extra time for API overhead
            )
            
            end_time = datetime.utcnow()
            runtime_ms = int((end_time - start_time).total_seconds() * 1000)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'stdout': '',
                    'stderr': f'API error: {response.status_code}',
                    'exit_code': 1,
                    'runtime_ms': runtime_ms,
                    'timed_out': False
                }
            
            result = response.json()
            run_result = result.get('run', {})
            
            stdout = run_result.get('stdout', '')
            stderr = run_result.get('stderr', '')
            exit_code = run_result.get('code', 0)
            signal = run_result.get('signal')
            
            timed_out = signal == 'SIGKILL' or 'timed out' in stderr.lower()
            
            return {
                'success': exit_code == 0 and not timed_out,
                'stdout': stdout,
                'stderr': stderr,
                'exit_code': exit_code,
                'runtime_ms': runtime_ms,
                'timed_out': timed_out
            }
            
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'stdout': '',
                'stderr': f'Request timed out after {self.timeout}s',
                'exit_code': -1,
                'runtime_ms': self.timeout * 1000,
                'timed_out': True
            }
        except requests.exceptions.RequestException as e:
            logger.warning(f"Piston API error: {e}, falling back to subprocess")
            return None  # Signal to use fallback
    
    def _execute_via_subprocess(
        self,
        code: str,
        language: str = 'python',
        stdin: str = ''
    ) -> Dict[str, Any]:
        if language != 'python':
            return {
                'success': False,
                'stdout': '',
                'stderr': f'Local execution only supports Python',
                'exit_code': 1,
                'runtime_ms': 0,
                'timed_out': False
            }
        
        start_time = datetime.utcnow()
        
        # Create temporary file for code
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            dir=SANDBOX_PATH,
            delete=False
        ) as f:
            f.write(code)
            code_file = f.name
        
        try:
            cmd = [sys.executable, code_file]
            
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=SANDBOX_PATH,
                env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}
            )
            
            try:
                stdout, stderr = process.communicate(
                    input=stdin.encode() if stdin else None,
                    timeout=self.timeout
                )
                timed_out = False
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                timed_out = True
            
            end_time = datetime.utcnow()
            runtime_ms = int((end_time - start_time).total_seconds() * 1000)
            
            result = {
                'success': process.returncode == 0 and not timed_out,
                'stdout': stdout.decode('utf-8', errors='replace'),
                'stderr': stderr.decode('utf-8', errors='replace'),
                'exit_code': process.returncode if not timed_out else -1,
                'runtime_ms': runtime_ms,
                'timed_out': timed_out
            }
            
            if timed_out:
                result['stderr'] = f"Execution timed out after {self.timeout} seconds"
            
            return result
            
        except Exception as e:
            logger.error(f"Subprocess execution error: {e}")
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'exit_code': 1,
                'runtime_ms': 0,
                'timed_out': False
            }
        finally:
            try:
                os.unlink(code_file)
            except Exception:
                pass
    
    def execute_code(
        self,
        code: str,
        language: str = 'python',
        stdin: str = '',
        timeout: int = None,
        memory_limit_mb: int = None
    ) -> Dict[str, Any]:
        if timeout:
            self.timeout = timeout
        
        # Try external API first
        if self.use_external_api:
            result = self._execute_via_piston(code, language, stdin)
            if result is not None:
                return result
        
        # Fallback to subprocess
        return self._execute_via_subprocess(code, language, stdin)
    
    def run_test_case(
        self,
        code: str,
        test_case,
        language: str = 'python'
    ) -> Dict[str, Any]:
        result = self.execute_code(
            code=code,
            language=language,
            stdin=test_case.stdin or '',
            timeout=test_case.timeout_seconds if hasattr(test_case, 'timeout_seconds') else self.timeout
        )
        
        actual_output = result['stdout'].strip()
        expected_output = (test_case.expected_out or '').strip()
        
        passed = (
            result['success'] and 
            not result['timed_out'] and 
            actual_output == expected_output
        )
        
        return {
            'test_name': test_case.name,
            'passed': passed,
            'actual_output': actual_output,
            'expected_output': expected_output,
            'stdout': result['stdout'],
            'stderr': result['stderr'],
            'exit_code': result['exit_code'],
            'runtime_ms': result['runtime_ms'],
            'timed_out': result['timed_out']
        }
    
    def run_all_tests(
        self,
        code: str,
        test_cases: List,
        language: str = 'python'
    ) -> Dict[str, Any]:
        """
        Run code against all test cases.
        """
        results = []
        passed_count = 0
        total_points = 0
        earned_points = 0
        
        for tc in test_cases:
            result = self.run_test_case(code, tc, language)
            results.append(result)
            
            if result['passed']:
                passed_count += 1
                earned_points += tc.points if hasattr(tc, 'points') else 0
            
            total_points += tc.points if hasattr(tc, 'points') else 0
        
        score = (earned_points / total_points * 100) if total_points > 0 else (
            (passed_count / len(test_cases) * 100) if test_cases else 0
        )
        
        return {
            'results': results,
            'passed_count': passed_count,
            'total_count': len(test_cases),
            'score': round(score, 2),
            'earned_points': earned_points,
            'total_points': total_points
        }
    
    def get_ai_feedback(self, code: str, error_message: str) -> Optional[str]:
        """Get AI-powered feedback on code errors using Groq."""
        if not self.groq_client:
            return None
        
        try:
            return self.groq_client.generate_hint(
                code=code,
                error_message=error_message,
                context="This code failed during sandbox execution."
            )
        except Exception as e:
            logger.warning(f"AI feedback unavailable: {e}")
            return None
    
    def create_job(self, submission_id: int) -> SandboxJob:
        """Create a new sandbox job for a submission."""
        job = SandboxJob(
            id=None,
            submission_id=submission_id,
            status='queued',
            timeout_seconds=self.timeout,
            memory_limit_mb=self.memory_limit_mb
        )
        return self.sandbox_job_repo.create(job)
    
    def get_job(self, job_id: int) -> SandboxJob:
        """Get a sandbox job by ID."""
        return self.sandbox_job_repo.get_by_id(job_id)
    
    def get_jobs_for_submission(self, submission_id: int) -> List[SandboxJob]:
        """Get all sandbox jobs for a submission."""
        return self.sandbox_job_repo.get_by_submission(submission_id)
