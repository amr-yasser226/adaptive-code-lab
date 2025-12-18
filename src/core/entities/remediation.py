from datetime import datetime


class Remediation:
    
    valid_types = ('article', 'video', 'exercise', 'example', 'documentation')
    valid_levels = ('beginner', 'intermediate', 'advanced')
    
    def __init__(
        self,
        id,
        failure_pattern,
        resource_title,
        resource_type='article',
        resource_url=None,
        resource_content=None,
        difficulty_level='beginner',
        language='python',
        created_at=None
    ):
        if resource_type not in Remediation.valid_types:
            raise ValueError(f"Invalid type: {resource_type}")
        if difficulty_level not in Remediation.valid_levels:
            raise ValueError(f"Invalid level: {difficulty_level}")
        
        self.__id = id
        self.failure_pattern = failure_pattern
        self.resource_title = resource_title
        self.resource_type = resource_type
        self.resource_url = resource_url
        self.resource_content = resource_content
        self.difficulty_level = difficulty_level
        self.language = language
        self.created_at = created_at or datetime.utcnow()
    
    def get_id(self):
        return self.__id
    
    def to_dict(self):
        return {
            'id': self.__id,
            'failure_pattern': self.failure_pattern,
            'resource_title': self.resource_title,
            'resource_type': self.resource_type,
            'resource_url': self.resource_url,
            'resource_content': self.resource_content,
            'difficulty_level': self.difficulty_level,
            'language': self.language
        }


class StudentRemediation:
    
    def __init__(
        self,
        id,
        student_id,
        remediation_id,
        submission_id=None,
        is_viewed=False,
        is_completed=False,
        recommended_at=None,
        viewed_at=None,
        completed_at=None
    ):
        self.__id = id
        self.__student_id = student_id
        self.__remediation_id = remediation_id
        self.__submission_id = submission_id
        self.is_viewed = is_viewed
        self.is_completed = is_completed
        self.recommended_at = recommended_at or datetime.utcnow()
        self.viewed_at = viewed_at
        self.completed_at = completed_at
    
    def get_id(self):
        return self.__id
    
    def get_student_id(self):
        return self.__student_id
    
    def get_remediation_id(self):
        return self.__remediation_id
    
    def get_submission_id(self):
        return self.__submission_id
    
    def mark_viewed(self):
        self.is_viewed = True
        self.viewed_at = datetime.utcnow()
    
    def mark_completed(self):
        self.is_completed = True
        self.completed_at = datetime.utcnow()
        if not self.is_viewed:
            self.mark_viewed()
