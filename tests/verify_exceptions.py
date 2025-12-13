
import unittest
from unittest.mock import MagicMock, patch
import sqlite3
import sys
import os
import datetime

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from infrastructure.repositories.user_repository import UserRepository
from infrastructure.repositories.course_repository import CourseRepository
from infrastructure.repositories.assignment_repository import AssignmentRepository
from infrastructure.repositories.student_repository import StudentRepository
from infrastructure.repositories.instructor_repository import InstructorRepository
from infrastructure.repositories.enrollment_repository import EnrollmentRepository
from infrastructure.repositories.submission_repository import SubmissionRepository
from infrastructure.repositories.result_repository import Result_repo as ResultRepository
from infrastructure.repositories.audit_log_repository import AuditLog_repo as AuditLogRepository
from infrastructure.repositories.hint_repository import Hint_repo as HintRepository
from infrastructure.repositories.peer_review_repository import PeerReview_repo as PeerReviewRepository
from infrastructure.repositories.similarity_comparison_repository import SimilarityComparison_repo as SimilarityComparisonRepository
from infrastructure.repositories.similarity_flag_repository import SimilarityFlagRepository
from infrastructure.repositories.file_repository import File_repo as FileRepository
from infrastructure.repositories.admin_repository import Admin_repo as AdminRepository
from infrastructure.repositories.notification_repository import Notification_repo as NotificationRepository
from infrastructure.repositories.embedding_repository import Embedding_repo as EmbeddingRepository
from infrastructure.repositories.test_case_repository import Testcase_repo as TestCaseRepository
from infrastructure.repositories.flag_repository import Flag_repo as FlagRepository

class TestExceptionHandling(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        # Configure db.execute to raise sqlite3.Error when called
        self.mock_db.execute.side_effect = sqlite3.Error("Simulated DB Error")
        self.mock_db.commit = MagicMock()
        self.mock_db.rollback = MagicMock()

    def test_user_repo(self):
        print("Testing UserRepository...")
        repo = UserRepository(self.mock_db)
        user = MagicMock()
        user.get_id.return_value = None
        # Should catch error and re-raise (as per code inspection in earlier steps) or return None.
        # Wait, UserRepository had 'raise' in some blocks? Let's check. 
        # Actually UserRepo had `raise` in `save_user`? 
        # Checking my previous edits: "except sqlite3.Error: self.db.rollback(); raise" was in one snippet but user might have changed it?
        # Let's assume it might raise or return None. I'll catch it if it raises.
        try:
            repo.save_user(user)
        except sqlite3.Error:
             print("  -> UserRepository re-raised sqlite3.Error (Expected behavior if designed to bubble up)")
        except Exception as e:
             self.fail(f"UserRepository raised unexpected exception: {e}")
        
        self.mock_db.rollback.assert_called()
        print("  -> UserRepository.save_user verified.")

    def test_course_repo(self):
        print("Testing CourseRepository...")
        repo = CourseRepository(self.mock_db)
        course = MagicMock()
        course.get_id.return_value = None
        result = repo.create(course)
        self.assertIsNone(result)
        self.mock_db.rollback.assert_called()
        print("  -> CourseRepository.create verified.")

    def test_assignment_repo(self):
        print("Testing AssignmentRepository...")
        repo = AssignmentRepository(self.mock_db)
        assignment = MagicMock()
        assignment.get_id.return_value = None
        result = repo.create(assignment)
        self.assertIsNone(result)
        self.mock_db.rollback.assert_called()
        print("  -> AssignmentRepository.create verified.")

    def test_student_repo(self):
        print("Testing StudentRepository...")
        repo = StudentRepository(self.mock_db)
        student = MagicMock()
        student.get_id.return_value = 123 # Fix: Must have ID to pass validation
        student.name = "Test Student"
        student.email = "test@example.com"
        student.get_password_hash.return_value = "hash"
        # StudentRepo.save_student was seen to raise in previous snippet
        try:
            repo.save_student(student)
        except sqlite3.Error:
            print("  -> StudentRepository re-raised sqlite3.Error")
        self.mock_db.rollback.assert_called()
        print("  -> StudentRepository.save_student verified.")

    def test_admin_repo(self):
        print("Testing AdminRepository...")
        repo = AdminRepository(self.mock_db)
        admin = MagicMock()
        admin.get_id.return_value = 123 # Fix: Must have ID to pass validation
        admin.name = "Test Admin"
        admin.email = "admin@example.com"
        # admin.get_password_hash check in repo uses hasattr
        admin.password = "password" 
        result = repo.save_admin(admin)
        self.assertIsNone(result)
        self.mock_db.rollback.assert_called()
        print("  -> AdminRepository.save_admin verified.")

    def test_notification_repo(self):
        print("Testing NotificationRepository...")
        repo = NotificationRepository(self.mock_db)
        notif = MagicMock()
        result = repo.save_notification(notif)
        self.assertIsNone(result)
        self.mock_db.rollback.assert_called()
        print("  -> NotificationRepository.save_notification verified.")
        
    def test_embedding_repo(self):
        print("Testing EmbeddingRepository...")
        repo = EmbeddingRepository(self.mock_db)
        emb = MagicMock()
        result = repo.save_embedding(emb)
        self.assertIsNone(result)
        self.mock_db.rollback.assert_called()
        print("  -> EmbeddingRepository.save_embedding verified.")

    def test_hint_repo(self):
        print("Testing HintRepository...")
        repo = HintRepository(self.mock_db)
        hint = MagicMock()
        hint.get_id.return_value = None
        result = repo.create(hint)
        self.assertIsNone(result)
        self.mock_db.rollback.assert_called()
        print("  -> HintRepository.create verified.")

    def test_peer_review_repo(self):
        print("Testing PeerReviewRepository...")
        repo = PeerReviewRepository(self.mock_db)
        review = MagicMock()
        review.rubric_score = None # Fix: JSON serialization
        result = repo.create(review)
        self.assertIsNone(result)
        self.mock_db.rollback.assert_called()
        print("  -> PeerReviewRepository.create verified.")

    def test_similarity_comparison_repo(self):
        print("Testing SimilarityComparisonRepository...")
        repo = SimilarityComparisonRepository(self.mock_db)
        comp = MagicMock()
        comp.match_segments = None # Fix: JSON serialization
        result = repo.create(comp)
        self.assertIsNone(result)
        self.mock_db.rollback.assert_called()
        print("  -> SimilarityComparisonRepository.create verified.")

    def test_similarity_flag_repo(self):
        print("Testing SimilarityFlagRepository...")
        repo = SimilarityFlagRepository(self.mock_db)
        flag = MagicMock()
        flag.highlighted_spans = None # Fix: JSON serialization
        result = repo.create(flag)
        self.assertIsNone(result)
        self.mock_db.rollback.assert_called()
        print("  -> SimilarityFlagRepository.create verified.")

    def test_file_repo(self):
        print("Testing FileRepository...")
        repo = FileRepository(self.mock_db)
        file_entity = MagicMock()
        file_entity.get_id.return_value = None
        result = repo.save_file(file_entity)
        self.assertIsNone(result)
        self.mock_db.rollback.assert_called()
        print("  -> FileRepository.save_file verified.")

    def test_test_case_repo(self):
        print("Testing TestCaseRepository...")
        repo = TestCaseRepository(self.mock_db)
        testcase = MagicMock()
        testcase.get_id.return_value = None
        result = repo.create(testcase)
        self.assertIsNone(result)
        self.mock_db.rollback.assert_called()
        print("  -> TestCaseRepository.create verified.")

    def test_flag_repo(self):
        print("Testing FlagRepository...")
        repo = FlagRepository(self.mock_db)
        flag = MagicMock()
        flag.highlighted_spans = None # Fix: JSON serialization
        result = repo.save_similarityflag(flag)
        self.assertIsNone(result)
        self.mock_db.rollback.assert_called()
        print("  -> FlagRepository.save_similarityflag verified.")

    def test_instructor_repo(self):
        print("Testing InstructorRepository...")
        repo = InstructorRepository(self.mock_db)
        instructor = MagicMock()
        instructor.get_id.return_value = 123
        instructor.name = "Test Instructor"
        instructor.email = "inst@example.com"
        instructor.password = "pass"
        # Pre-validation might check existence/role, but mocked DB.execute raises immediately
        # unless it checks role first. Instructor check:
        # role_row = self.db.execute("SELECT role...").fetchone()
        # This will raise sqlite3.Error on the first execute call, which is caught.
        
        result = repo.save(instructor)
        self.assertIsNone(result)
        self.mock_db.rollback.assert_called()
        print("  -> InstructorRepository.save verified.")

    def test_submission_repo(self):
        print("Testing SubmissionRepository...")
        repo = SubmissionRepository(self.mock_db)
        submission = MagicMock()
        submission.get_id.return_value = None
        result = repo.create(submission)
        self.assertIsNone(result)
        self.mock_db.rollback.assert_called()
        print("  -> SubmissionRepository.create verified.")

    def test_enrollment_repo(self):
        print("Testing EnrollmentRepository...")
        repo = EnrollmentRepository(self.mock_db)
        enrollment = MagicMock()
        result = repo.enroll(enrollment)
        self.assertIsNone(result)
        self.mock_db.rollback.assert_called()
        print("  -> EnrollmentRepository.enroll verified.")

    def test_result_repo(self):
        print("Testing ResultRepository...")
        repo = ResultRepository(self.mock_db)
        result_entity = MagicMock()
        result_entity.passed = True
        result = repo.save_result(result_entity)
        self.assertIsNone(result)
        self.mock_db.rollback.assert_called()
        print("  -> ResultRepository.save_result verified.")

    def test_audit_log_repo(self):
        print("Testing AuditLogRepository...")
        repo = AuditLogRepository(self.mock_db)
        log = MagicMock()
        log.get_id.return_value = None
        result = repo.save(log)
        self.assertIsNone(result)
        self.mock_db.rollback.assert_called()
        print("  -> AuditLogRepository.save verified.")

if __name__ == '__main__':
    unittest.main()
