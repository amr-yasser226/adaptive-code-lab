from core.entities.file import File
from datetime import datetime
class Submission :
    valid_languages =('python', 'java', 'cpp', 'javascript') 
    valid_statuses =('pending','queued', 'running', 'graded', 'failed', 'error')
    def __init__(self, id , assignment_id , student_id , version , language , status , score , is_late , created_at , updated_at , grade_at ): 
        if language not in Submission.valid_languages:
            raise ValueError(
                f"Invalid language: {language}. "
                f"Allowed languages: {Submission.valid_languages}"
            )
        if status not in Submission.valid_statuses:
            raise ValueError(
                f"Invalid status: {status}. "
                f"Allowed statuses: {Submission.valid_statuses}"
            )
        self.__id = id
        self.__assignment_id = assignment_id
        self.__student_id = student_id
        self.version = version
        self.language = language
        self.status = status
        self.score = score
        self.is_late = bool(is_late)
        self.created_at = created_at
        self.updated_at = updated_at
        self.grade_at = grade_at

    def get_id(self):
            return self.__id
    def get_assignment_id(self):
            return self.__assignment_id
    def get_student_id(self):
            return self.__student_id
    
    def enqueue_for_grading(self):
            self.status = 'queued'
    def attach_file(self , file_repo, path ,file_name ,content_type , size_bytes , uploader_id  , checksum =None , storage_url=None ):
        file =File(
        id=None,
        submission_id=self.get_id(),
        uploader_id=uploader_id,
        path=path,
        file_name=file_name,
        content_type=content_type,
        size_bytes=size_bytes,
        checksum=checksum,
        storage_url=storage_url,
        created_at=datetime.now()
    )
        return file_repo.save_file(file)
        
    def get_results(self):
            pass
    def regrade(self):
            pass 
    def calculated_score(self):
            pass
    def get_files(self ,file_repo):
        return file_repo.find_by_submission(self.get_id())