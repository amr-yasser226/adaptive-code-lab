import pytest
from core.entities.course import Course


@pytest.mark.repo
@pytest.mark.unit
class TestCourseRepo:
    """Test suite for Course_repo"""
    
    def test_create_course(self, sample_instructor, course_repo):
        """Test creating a new course"""
        course = Course(
            id=None,
            instructor_id=sample_instructor.get_id(),
            code="CS202",
            title="Data Structures",
            description="Learn DS & Algorithms",
            year=2024,
            semester="Spring",
            max_students=40,
            created_at=None,
            status="active",
            updated_at=None,
            credits=4
        )
        
        saved_course = course_repo.create(course)
        
        assert saved_course is not None
        assert saved_course.get_id() is not None
        assert saved_course.code == "CS202"
        assert saved_course.title == "Data Structures"
    
    def test_get_by_id_returns_course(self, sample_course, course_repo):
        """Test retrieving course by ID"""
        retrieved = course_repo.get_by_id(sample_course.get_id())
        
        assert retrieved is not None
        assert retrieved.code == sample_course.code
    
    def test_update_course(self, sample_course, course_repo):
        """Test updating course"""
        sample_course.title = "Advanced Programming"
        sample_course.max_students = 25
        
        updated = course_repo.update(sample_course)
        
        assert updated.title == "Advanced Programming"
        assert updated.max_students == 25
    
    def test_publish_course(self, sample_course, course_repo):
        """Test publishing a course"""
        published = course_repo.publish(sample_course.get_id())
        
        assert published.status == "active"
    
    def test_archive_course(self, sample_course, course_repo):
        """Test archiving a course"""
        archived = course_repo.archive(sample_course.get_id())
        
        assert archived.status == "inactive"
    
    def test_list_by_instructor(self, sample_instructor, course_repo):
        """Test listing courses by instructor"""
        # Create multiple courses
        for i in range(3):
            course = Course(
                id=None,
                instructor_id=sample_instructor.get_id(),
                code=f"CS{100+i}",
                title=f"Course {i}",
                description="Description",
                year=2024,
                semester="Fall",
                max_students=30,
                created_at=None,
                status="active",
                updated_at=None,
                credits=3
            )
            course_repo.create(course)
        
        courses = course_repo.list_by_instructor(sample_instructor.get_id())
        
        assert len(courses) >= 3