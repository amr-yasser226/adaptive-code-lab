import pytest
from datetime import datetime, timedelta


class TestInstructorWorkflow:
    """Test suite for instructor end-to-end workflows"""

    def test_create_course_and_assignment(self, clean_db, sample_instructor,
                                          course_repo, assignment_repo):
        """Test instructor creating a course and adding assignments"""
        from core.entities.course import Course
        from core.entities.assignment import Assignment

        # Create course
        course = Course(
            id=None,
            instructor_id=sample_instructor.get_id(),
            code="CS201",
            title="Data Structures",
            description="Advanced programming",
            year=2024,
            semester="Spring",
            max_students=25,
            created_at=datetime.now(),
            status="active",
            updated_at=datetime.now(),
            credits=4
        )
        saved_course = course_repo.create(course)

        # Publish course
        saved_course.status = "active"
        course_repo.update(saved_course)

        # Create assignment
        assignment = Assignment(
            id=None,
            course_id=saved_course.get_id(),
            title="Assignment 1",
            description="Implement a linked list",
            release_date=datetime.now(),
            due_date=datetime.now() + timedelta(days=14),
            max_points=150,
            is_published=False,
            allow_late_submissions=True,
            late_submission_penalty=0.15,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        saved_assignment = assignment_repo.create(assignment)

        # Publish assignment
        saved_assignment.is_published = True
        final_assignment = assignment_repo.update(saved_assignment)

        # Verify workflow
        assert saved_course.status == "active"
        assert final_assignment.is_published is True
        assert final_assignment.get_course_id() == saved_course.get_id()

    def test_manage_enrollments_and_grades(self, clean_db, sample_instructor,
                                            sample_student, sample_course,
                                            enrollment_repo):
        """Test instructor viewing enrollments and exporting grades"""
        from core.entities.enrollment import Enrollment

        # Enroll student
        enrollment = Enrollment(
            student_id=sample_student.get_id(),
            course_id=sample_course.get_id(),
            status="enrolled",
            enrolled_at=datetime.now(),
            dropped_at=None,
            final_grade=None
        )
        saved_enrollment = enrollment_repo.enroll(enrollment)

        # Complete course with grade
        saved_enrollment.status = "completed"
        saved_enrollment.final_grade = 88.5
        final_enrollment = enrollment_repo.update(saved_enrollment)

        # Verify
        assert final_enrollment.status == "completed"
        assert final_enrollment.final_grade == 88.5

        # List enrollments for course
        enrollments = enrollment_repo.list_by_course(sample_course.get_id())
        assert len(enrollments) >= 1
