import pytest
import os
import sys
import sqlite3
from pathlib import Path
from datetime import datetime

# Add src directory to Python path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Print for debugging
print(f"Project root: {project_root}")
print(f"Src path: {src_path}")

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Verify DB path is set
db_path = os.getenv("ACCL_DB_PATH")
if db_path:
    print(f"Using DB: {project_root / db_path}")
else:
    print("WARNING: ACCL_DB_PATH not set in .env")


@pytest.fixture(scope="session")
def project_root_path():
    """Return the project root directory path"""
    return project_root


@pytest.fixture(scope="session")
def src_path_fixture():
    """Return the src directory path"""
    return src_path


# Import these after path is set
from infrastructure.repositories.database import Database
from infrastructure.repositories.user_repository import UserRepository as User_repo
from infrastructure.repositories.student_repository import StudentRepository as Student_repo
from infrastructure.repositories.instructor_repository import InstructorRepository as Instructor_repo
from infrastructure.repositories.admin_repository import AdminRepository
from infrastructure.repositories.course_repository import CourseRepository as Course_repo
from infrastructure.repositories.assignment_repository import AssignmentRepository as Assignments_repo
from infrastructure.repositories.submission_repository import SubmissionRepository as Submission_repo
from infrastructure.repositories.test_case_repository import TestCaseRepository as Testcase_repo
from infrastructure.repositories.result_repository import ResultRepository
from infrastructure.repositories.enrollment_repository import EnrollmentRepository as Enrollment_repo
from infrastructure.repositories.notification_repository import NotificationRepository as Notification_repo
from infrastructure.repositories.hint_repository import HintRepository
from infrastructure.repositories.file_repository import FileRepository
from infrastructure.repositories.embedding_repository import EmbeddingRepository
from infrastructure.repositories.peer_review_repository import PeerReviewRepository as PeerReview_repo
from infrastructure.repositories.similarity_flag_repository import SimilarityFlagRepository as SimilarityFlag_repo
from infrastructure.repositories.similarity_comparison_repository import SimilarityComparisonRepository
from infrastructure.repositories.audit_log_repository import AuditLogRepository


@pytest.fixture(scope="session")
def test_db_path(tmp_path_factory):
    """Create a temporary database path for testing"""
    db_dir = tmp_path_factory.mktemp("test_db")
    db_file = db_dir / "test_accl.db"
    return str(db_file)


@pytest.fixture(scope="session")
def setup_test_database(test_db_path):
    """Setup test database with schema"""
    db_dir = os.path.dirname(test_db_path)
    os.makedirs(db_dir, exist_ok=True)
    
    conn = sqlite3.connect(test_db_path)
    conn.close()
    
    from infrastructure.database.migrations import run_migrations
    tables = run_migrations(
        db_path=test_db_path,
        tables_dir=str(project_root / "src" / "infrastructure" / "database" / "schema")
    )
    
    sqlite_url = f"sqlite:///{test_db_path}"
    os.environ["ACCL_DB_PATH"] = sqlite_url
    
    yield sqlite_url
    
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except:
            pass


@pytest.fixture(scope="function")
def db_connection(setup_test_database):
    """Provide a fresh database connection for each test"""
    from infrastructure.database.connection import DatabaseManager
    DatabaseManager._reset_instance()
    
    db = Database()
    db.connect()
    yield db
    if db.session:
        db.session.rollback()
    db.disconnect()


@pytest.fixture(scope="function")
def clean_db(db_connection):
    """Provide a clean database (all tables truncated)"""
    tables = [
        'audit_logs', 'peer_reviews', 'similarity_comparisons',
        'similarity_flags', 'results', 'hints', 'embeddings',
        'files', 'test_cases', 'submissions', 'enrollments', 'drafts',
        'assignments', 'courses', 'notifications', 'admins',
        'instructors', 'students', 'users'
    ]
    
    db_connection.execute("PRAGMA foreign_keys = OFF")
    for table in tables:
        db_connection.execute(f"DELETE FROM {table}")
    db_connection.commit()
    db_connection.execute("PRAGMA foreign_keys = ON")
    
    return db_connection


# Repository fixtures
@pytest.fixture
def user_repo(clean_db):
    return User_repo(clean_db)


@pytest.fixture
def student_repo(clean_db):
    return Student_repo(clean_db)


@pytest.fixture
def instructor_repo(clean_db):
    return Instructor_repo(clean_db)


@pytest.fixture
def admin_repo(clean_db):
    return AdminRepository(clean_db)


@pytest.fixture
def course_repo(clean_db):
    return Course_repo(clean_db)


@pytest.fixture
def assignment_repo(clean_db):
    return Assignments_repo(clean_db)


@pytest.fixture
def submission_repo(clean_db):
    return Submission_repo(clean_db)


@pytest.fixture
def testcase_repo(clean_db):
    return Testcase_repo(clean_db)


@pytest.fixture
def result_repo(clean_db):
    return ResultRepository(clean_db)


@pytest.fixture
def enrollment_repo(clean_db):
    return Enrollment_repo(clean_db)


@pytest.fixture
def notification_repo(clean_db):
    return Notification_repo(clean_db)


@pytest.fixture
def hint_repo(clean_db):
    return HintRepository(clean_db)


@pytest.fixture
def file_repo(clean_db):
    return FileRepository(clean_db)


@pytest.fixture
def embedding_repo(clean_db):
    return EmbeddingRepository(clean_db)


@pytest.fixture
def peer_review_repo(clean_db):
    return PeerReview_repo(clean_db)


@pytest.fixture
def similarity_repo(clean_db):
    """Alias for similarity_flag_repo"""
    return SimilarityFlag_repo(clean_db)


@pytest.fixture
def comparison_repo(clean_db):
    """Alias for similarity_comparison_repo"""
    return SimilarityComparisonRepository(clean_db)


@pytest.fixture
def similarity_flag_repo(clean_db):
    return SimilarityFlag_repo(clean_db)


@pytest.fixture
def similarity_comparison_repo(clean_db):
    return SimilarityComparisonRepository(clean_db)


@pytest.fixture
def audit_log_repo(clean_db):
    return AuditLogRepository(clean_db)


# Sample entity fixtures
from core.entities.user import User
from core.entities.student import Student
from core.entities.instructor import Instructor
from core.entities.admin import Admin
from core.entities.course import Course
from core.entities.assignment import Assignment
from core.entities.submission import Submission


@pytest.fixture
def sample_student(user_repo, student_repo):
    """Create and return a sample student"""
    user = User(
        id=None,
        name="Test Student",
        email="student@test.edu",
        password="hashed_password",
        role="student",
        is_active=True
    )
    saved_user = user_repo.create(user)
    
    student = Student(
        id=saved_user.get_id(),
        name=saved_user.name,
        email=saved_user.email,
        password=saved_user.get_password_hash(),
        created_at=saved_user.created_at,
        updated_at=saved_user.updated_at,
        student_number="ST12345",
        program="Computer Science",
        year_level=2
    )
    return student_repo.save_student(student)


@pytest.fixture
def sample_instructor(user_repo, instructor_repo):
    """Create and return a sample instructor"""
    user = User(
        id=None,
        name="Dr. Test Instructor",
        email="instructor@test.edu",
        password="hashed_password",
        role="instructor",
        is_active=True
    )
    saved_user = user_repo.create(user)
    
    instructor = Instructor(
        id=saved_user.get_id(),
        name=saved_user.name,
        email=saved_user.email,
        password=saved_user.get_password_hash(),
        created_at=saved_user.created_at,
        updated_at=saved_user.updated_at,
        instructor_code="TEST001",
        bio="Test instructor",
        office_hours="Mon-Fri 2-4pm"
    )
    return instructor_repo.save(instructor)


@pytest.fixture
def sample_course(course_repo, sample_instructor):
    """Create and return a sample course"""
    course = Course(
        id=None,
        instructor_id=sample_instructor.get_id(),
        code="CS101",
        title="Intro to Programming",
        description="Learn Python basics",
        year=2024,
        semester="Fall",
        max_students=30,
        created_at=datetime.now(),
        status="active",
        updated_at=datetime.now(),
        credits=3
    )
    return course_repo.create(course)


@pytest.fixture
def sample_assignment(assignment_repo, sample_course):
    """Create and return a sample assignment"""
    from datetime import timedelta
    assignment = Assignment(
        id=None,
        course_id=sample_course.get_id(),
        title="Homework 1",
        description="Write a hello world program",
        release_date="2024-01-01",
        due_date="2024-01-15",
        max_points=100,
        is_published=True,
        allow_late_submissions=True,
        late_submission_penalty=0.1,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    return assignment_repo.create(assignment)