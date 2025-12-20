import logging
from datetime import datetime
from typing import Optional, List, Dict

from core.entities.remediation import Remediation, StudentRemediation
from core.exceptions.validation_error import ValidationError

logger = logging.getLogger(__name__)


# Known failure patterns and how to detect them
FAILURE_PATTERNS = {
    'syntax_error': ['SyntaxError', 'IndentationError', 'TabError'],
    'name_error': ['NameError'],
    'type_error': ['TypeError'],
    'index_error': ['IndexError', 'KeyError'],
    'attribute_error': ['AttributeError'],
    'value_error': ['ValueError'],
    'zero_division': ['ZeroDivisionError'],
    'import_error': ['ImportError', 'ModuleNotFoundError'],
    'runtime_error': ['RuntimeError', 'RecursionError'],
    'assertion_error': ['AssertionError'],
    'timeout': ['TimeoutError', 'timed out', 'Execution exceeded'],
    'memory_error': ['MemoryError'],
    'infinite_loop': ['infinite', 'loop', 'timeout']
}


class RemediationService:
    def __init__(
        self,
        remediation_repo,
        result_repo=None,
        submission_repo=None
    ):
        self.remediation_repo = remediation_repo
        self.result_repo = result_repo
        self.submission_repo = submission_repo
    
    def detect_failure_pattern(self, error_output: str) -> Optional[str]:
        if not error_output:
            return None
        
        error_lower = error_output.lower()
        
        for pattern, keywords in FAILURE_PATTERNS.items():
            for keyword in keywords:
                if keyword.lower() in error_lower:
                    return pattern
        
        # Generic runtime error if nothing specific found
        if 'error' in error_lower or 'exception' in error_lower:
            return 'runtime_error'
        
        return None
    
    def analyze_submission_results(self, submission_id: int) -> List[str]:
        if not self.result_repo:
            return []
        
        results = self.result_repo.find_by_submission(submission_id)
        patterns = set()
        
        for result in results:
            if not result.passed:
                # Check stderr for patterns
                if result.stderr:
                    pattern = self.detect_failure_pattern(result.stderr)
                    if pattern:
                        patterns.add(pattern)
                
                # Check error message
                if result.error_message:
                    pattern = self.detect_failure_pattern(result.error_message)
                    if pattern:
                        patterns.add(pattern)
        
        return list(patterns)
    
    def get_recommendations(
        self,
        failure_pattern: str,
        limit: int = 3
    ) -> List[Remediation]:
        remediations = self.remediation_repo.find_by_pattern(failure_pattern)
        return remediations[:limit]
    
    def recommend_for_student(
        self,
        student_id: int,
        submission_id: int,
        patterns: List[str] = None
    ) -> List[Dict]:
        if patterns is None:
            patterns = self.analyze_submission_results(submission_id)
        
        if not patterns:
            return []
        
        recommendations = []
        
        for pattern in patterns:
            remediations = self.get_recommendations(pattern)
            
            for rem in remediations:
                # Check if already recommended
                existing = self.remediation_repo.get_student_remediation(
                    student_id, rem.get_id()
                )
                
                if not existing:
                    # Create new recommendation
                    sr = StudentRemediation(
                        id=None,
                        student_id=student_id,
                        remediation_id=rem.get_id(),
                        submission_id=submission_id
                    )
                    created = self.remediation_repo.create_student_remediation(sr)
                    
                    recommendations.append({
                        'student_remediation_id': created.get_id(),
                        'remediation': rem.to_dict(),
                        'is_new': True
                    })
                else:
                    recommendations.append({
                        'student_remediation_id': existing.get_id(),
                        'remediation': rem.to_dict(),
                        'is_new': False,
                        'is_viewed': existing.is_viewed,
                        'is_completed': existing.is_completed
                    })
        
        return recommendations
    
    def get_student_remediations(
        self,
        student_id: int,
        only_pending: bool = False
    ) -> List[Dict]:
        student_rems = self.remediation_repo.list_student_remediations(
            student_id, only_pending
        )
        
        result = []
        for sr in student_rems:
            rem = self.remediation_repo.get_by_id(sr.get_remediation_id())
            if rem:
                result.append({
                    'id': sr.get_id(),
                    'remediation': rem.to_dict(),
                    'submission_id': sr.get_submission_id(),
                    'is_viewed': sr.is_viewed,
                    'is_completed': sr.is_completed,
                    'recommended_at': sr.recommended_at,
                    'viewed_at': sr.viewed_at,
                    'completed_at': sr.completed_at
                })
        
        return result
    
    def mark_viewed(self, student_id: int, student_remediation_id: int) -> StudentRemediation:
        sr = self.remediation_repo.get_student_remediation_by_id(student_remediation_id)
        
        if not sr:
            raise ValidationError("Remediation record not found")
        
        if sr.get_student_id() != student_id:
            raise ValidationError("Not authorized to access this remediation")
        
        sr.mark_viewed()
        return self.remediation_repo.update_student_remediation(sr)
    
    def mark_completed(self, student_id: int, student_remediation_id: int) -> StudentRemediation:
        sr = self.remediation_repo.get_student_remediation_by_id(student_remediation_id)
        
        if not sr:
            raise ValidationError("Remediation record not found")
        
        if sr.get_student_id() != student_id:
            raise ValidationError("Not authorized to access this remediation")
        
        sr.mark_completed()
        return self.remediation_repo.update_student_remediation(sr)
    
    def get_all_remediations(self) -> List[Remediation]:
        return self.remediation_repo.get_all()
    
    def create_remediation(
        self,
        failure_pattern: str,
        resource_title: str,
        resource_type: str = 'article',
        resource_url: str = None,
        resource_content: str = None,
        difficulty_level: str = 'beginner',
        language: str = 'python'
    ) -> Remediation:
        rem = Remediation(
            id=None,
            failure_pattern=failure_pattern,
            resource_title=resource_title,
            resource_type=resource_type,
            resource_url=resource_url,
            resource_content=resource_content,
            difficulty_level=difficulty_level,
            language=language
        )
        return self.remediation_repo.create(rem)
