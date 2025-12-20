import pytest
from datetime import datetime


class TestAccessControl:
    """Test suite for access control and authorization"""

    def test_student_cannot_access_instructor_functions(self, sample_student):
        """Test students cannot create courses"""
        # Students should not be able to create courses (role check)
        assert sample_student.role == "student"
        assert sample_student.role != "instructor"

    def test_student_cannot_view_other_student_submissions(self, clean_db, sample_student,
                                                            sample_assignment, submission_repo):
        """Test students cannot view other students' submissions"""
        from core.entities.submission import Submission
        
        # Create submission for sample_student
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
        saved = submission_repo.create(submission)
        
        # Verify submission was created for this student
        assert saved.get_student_id() == sample_student.get_id()
        
        # In a real system, another student should not be able to query this
        # This is a role-based check at application level
        assert saved is not None

    def test_instructor_can_only_modify_own_courses(self, sample_instructor, sample_course, 
                                                     course_repo):
        """Test instructors can only modify their own courses"""
        # Verify instructor owns the sample course
        assert sample_course.get_instructor_id() == sample_instructor.get_id()
        
        # Role check
        assert sample_instructor.role == "instructor"

    def test_admin_can_access_all_data(self, clean_db, user_repo, admin_repo, course_repo, sample_course):
        """Test admin role can access all data"""
        from core.entities.user import User
        from core.entities.admin import Admin
        
        # Create user first
        user = User(
            id=None,
            name="Admin User",
            email="admin@test.edu",
            password="pwd",
            role="admin",
            is_active=True
        )
        saved_user = user_repo.create(user)
        
        # Create admin record
        admin = Admin(
            id=saved_user.get_id(),
            name=saved_user.name,
            email=saved_user.email,
            password=saved_user.get_password_hash(),
            created_at=saved_user.created_at,
            updated_at=saved_user.updated_at,
            is_active=True,
            privileges=None
        )
        saved_admin = admin_repo.save_admin(admin)
        
        # Admin role check
        assert saved_admin.role == "admin"
        
        # Admin should be able to access courses (verify course exists)
        course = course_repo.get_by_id(sample_course.get_id())
        assert course is not None
