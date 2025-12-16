import pytest
import os
import sys
import sqlite3
from pathlib import Path
from datetime import datetime

# Add src to path
# Adjusted for location in tests/unit/conftest.py (3 levels up to root)
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

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

from core.entities.user import User
from core.entities.student import Student
from core.entities.instructor import Instructor
from core.entities.admin import Admin
from core.entities.course import Course
from core.entities.assignment import Assignment
from core.entities.submission import Submission
from core.entities.test_case import Testcase
from core.entities.result import Result
from core.entities.enrollment import Enrollment
from core.entities.notification import Notification
from core.entities.hint import Hint
from core.entities.file import File
from core.entities.embedding import Embedding
from core.entities.peer_review import PeerReview
from core.entities.similarity_flag import SimilarityFlag
from core.entities.similarity_comparison import SimilarityComparison
from core.entities.audit_log import AuditLog


@pytest.fixture(scope="session")
def test_db_path(tmp_path_factory):
    """Create a temporary database path for testing"""
    db_dir = tmp_path_factory.mktemp("test_db")
    db_file = db_dir / "test_accl.db"
    return str(db_file)


@pytest.fixture(scope="session")
def setup_test_database(test_db_path):
    """Setup test database with schema"""
    # Ensure directory exists
    db_dir = os.path.dirname(test_db_path)
    os.makedirs(db_dir, exist_ok=True)
    
    # Create empty database file
    conn = sqlite3.connect(test_db_path)
    conn.close()
    
    # Run migrations to create tables
    from infrastructure.database.migrations import run_migrations
    tables = run_migrations(
        db_path=test_db_path,
        tables_dir=str(project_root / "src" / "infrastructure" / "database" / "schema")
    )
    
    print(f"\n✓ Test database created at: {test_db_path}")
    print(f"✓ Created {len(tables)} tables: {', '.join(tables)}")
    
    # Set environment variable for DB_repo to use
    sqlite_url = f"sqlite:///{test_db_path}"
    os.environ["ACCL_DB_PATH"] = sqlite_url
    
    yield sqlite_url
    
    # Cleanup
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
            print(f"\n✓ Test database cleaned up")
        except:
            pass


@pytest.fixture(scope="function")
def db_connection(setup_test_database):
    """Provide a fresh database connection for each test"""
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
        'files', 'test_cases', 'submissions', 'enrollments',
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
def similarity_flag_repo(clean_db):
    return SimilarityFlag_repo(clean_db)


@pytest.fixture
def similarity_comparison_repo(clean_db):
    return SimilarityComparisonRepository(clean_db)


@pytest.fixture
def audit_log_repo(clean_db):
    return AuditLogRepository(clean_db)


# Sample data fixtures
@pytest.fixture
def sample_user(user_repo):
    """Create and return a sample user"""
    user = User(
        id=None,
        name="Test User",
        email="testuser@example.com",
        password="hashed_password_123",
        role="student",
        is_active=True
    )
    saved_user = user_repo.save_user(user)
    return saved_user


@pytest.fixture
def sample_student(user_repo, student_repo):
    """Create and return a sample student"""
    user = User(
        id=None,
        name="John Doe",
        email="john.doe@student.com",
        password="hashed_pass",
        role="student",
        is_active=True
    )
    saved_user = user_repo.save_user(user)
    
    student = Student(
        id=saved_user.get_id(),
        name=saved_user.name,
        email=saved_user.email,
        password=saved_user.get_password_hash(),
        created_at=saved_user.created_at,
        updated_at=saved_user.updated_at,
        student_number="S12345",
        program="Computer Science",
        year_level=2
    )
    saved_student = student_repo.save_student(student)
    return saved_student


@pytest.fixture
def sample_instructor(user_repo, instructor_repo):
    """Create and return a sample instructor"""
    user = User(
        id=None,
        name="Dr. Smith",
        email="dr.smith@instructor.com",
        password="hashed_pass",
        role="instructor",
        is_active=True
    )
    saved_user = user_repo.save_user(user)
    
    instructor = Instructor(
        id=saved_user.get_id(),
        name=saved_user.name,
        email=saved_user.email,
        password=saved_user.get_password_hash(),
        created_at=saved_user.created_at,
        updated_at=saved_user.updated_at,
        instructor_code="INST001",
        bio="Experienced CS professor",
        office_hours="Mon/Wed 2-4pm"
    )
    saved_instructor = instructor_repo.save(instructor)
    return saved_instructor


@pytest.fixture
def sample_course(sample_instructor, course_repo):
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
        created_at=None,
        status="active",
        updated_at=None,
        credits=3
    )
    saved_course = course_repo.create(course)
    return saved_course


@pytest.fixture
def sample_assignment(sample_course, assignment_repo):
    """Create and return a sample assignment"""
    assignment = Assignment(
        id=None,
        course_id=sample_course.get_id(),
        title="Homework 1",
        description="Write a Python function",
        release_date="2024-01-01",
        due_date="2024-01-15",
        max_points=100,
        is_published=True,
        allow_late_submissions=True,
        late_submission_penalty=0.1,
        created_at=None,
        updated_at=None
    )
    saved_assignment = assignment_repo.create(assignment)
    return saved_assignment


@pytest.fixture
def sample_submission(sample_student, sample_assignment, submission_repo):
    """Create and return a sample submission"""
    submission = Submission(
        id=None,
        assignment_id=sample_assignment.get_id(),
        student_id=sample_student.get_id(),
        version=1,
        language="python",
        status="pending",
        score=0.0,
        is_late=False,
        created_at=None,
        updated_at=None,
        grade_at=None
    )
    saved_submission = submission_repo.create(submission)
    return saved_submission
