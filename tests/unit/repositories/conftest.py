import pytest
import os
import sys
import sqlite3
from pathlib import Path
from datetime import datetime

# Add src to path
project_root = Path(__file__).parent.parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from Backend.Repository.DB_repo import Database
from Backend.Repository.User_repo import User_repo
from Backend.Repository.Student_repo import Student_repo
from Backend.Repository.Instructor_repo import Instructor_repo
from Backend.Repository.Admin_repo import Admin_repo
from Backend.Repository.Course_repo import Course_repo
from Backend.Repository.Assignments_repo import Assignments_repo
from Backend.Repository.Submission_repo import Submission_repo
from Backend.Repository.Test_cases_repo import Testcase_repo
from Backend.Repository.Result_repo import Result_repo
from Backend.Repository.Enrollment_repo import Enrollment_repo
from Backend.Repository.Notification_repo import Notification_repo
from Backend.Repository.Hint_repo import Hint_repo
from Backend.Repository.File_repo import File_repo
from Backend.Repository.Embedding_repo import Embedding_repo
from Backend.Repository.Peer_review import PeerReview_repo
from Backend.Repository.Similarity_flag_repo import SimilarityFlag_repo
from Backend.Repository.Similarity_Comparison_repo import SimilarityComparison_repo
from Backend.Repository.Audit_Logs_repo import AuditLog_repo

from Backend.Model.User_model import User
from Backend.Model.Student_model import Student
from Backend.Model.Instructor_model import Instructor
from Backend.Model.Admin_model import Admin
from Backend.Model.Course_model import Course
from Backend.Model.Assignmnets_model import Assignmnets
from Backend.Model.Submission_model import Submission
from Backend.Model.TestCase_model import Testcase
from Backend.Model.Results_model import Result
from Backend.Model.Enrollment_model import Enrollment
from Backend.Model.Notification_model import Notification
from Backend.Model.Hint_model import Hint
from Backend.Model.Files_model import File
from Backend.Model.Embedding_model import Embedding
from Backend.Model.Peer_review_model import PeerReview
from Backend.Model.Similarity_flag import SimilarityFlag
from Backend.Model.Similarity_Comparison_model import SimilarityComparison
from Backend.Model.AuditLog_model import AuditLog


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
    from DB.run_migrations import run_migrations
    tables = run_migrations(
        db_path=test_db_path,
        tables_dir=str(project_root / "src" / "DB" / "Tables")
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
    return Admin_repo(clean_db)


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
    return Result_repo(clean_db)


@pytest.fixture
def enrollment_repo(clean_db):
    return Enrollment_repo(clean_db)


@pytest.fixture
def notification_repo(clean_db):
    return Notification_repo(clean_db)


@pytest.fixture
def hint_repo(clean_db):
    return Hint_repo(clean_db)


@pytest.fixture
def file_repo(clean_db):
    return File_repo(clean_db)


@pytest.fixture
def embedding_repo(clean_db):
    return Embedding_repo(clean_db)


@pytest.fixture
def peer_review_repo(clean_db):
    return PeerReview_repo(clean_db)


@pytest.fixture
def similarity_flag_repo(clean_db):
    return SimilarityFlag_repo(clean_db)


@pytest.fixture
def similarity_comparison_repo(clean_db):
    return SimilarityComparison_repo(clean_db)


@pytest.fixture
def audit_log_repo(clean_db):
    return AuditLog_repo(clean_db)


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
        Program="Computer Science",
        year_Level=2
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
        describtion="Learn Python basics",
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
    assignment = Assignmnets(
        id=None,
        course_id=sample_course.get_id(),
        title="Homework 1",
        describtion="Write a Python function",
        releaseDate="2024-01-01",
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