import pytest
from datetime import datetime, timedelta


class TestStudentWorkflow:
    """Test suite for student end-to-end workflows"""

    def test_enroll_and_submit_assignment(self, clean_db, sample_student,
                                           sample_course, sample_assignment,
                                           enrollment_repo, submission_repo):
        """Test student enrolling in course and submitting assignment"""
        from core.entities.enrollment import Enrollment
        from core.entities.submission import Submission

        # Enroll in course
        enrollment = Enrollment(
            student_id=sample_student.get_id(),
            course_id=sample_course.get_id(),
            status="enrolled",
            enrolled_at=datetime.now(),
            dropped_at=None,
            final_grade=None
        )
        saved_enrollment = enrollment_repo.enroll(enrollment)

        # Verify enrollment
        assert saved_enrollment.status == "enrolled"

        # Submit assignment (version 1)
        submission = Submission(
            id=None,
            assignment_id=sample_assignment.get_id(),
            student_id=sample_student.get_id(),
            version=1,
            language="python",
            status="pending",
            score=None,
            is_late=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            grade_at=None
        )
        saved_submission = submission_repo.create(submission)

        # Verify submission
        assert saved_submission.version == 1
        assert saved_submission.status == "pending"

    def test_resubmit_assignment(self, clean_db, sample_student,
                                 sample_assignment, enrollment_repo,
                                 submission_repo, sample_course):
        """Test student resubmitting assignment (version increment)"""
        from core.entities.enrollment import Enrollment
        from core.entities.submission import Submission

        # Enroll
        enrollment_repo.enroll(Enrollment(
            student_id=sample_student.get_id(),
            course_id=sample_course.get_id(),
            status="enrolled",
            enrolled_at=datetime.now(),
            dropped_at=None,
            final_grade=None
        ))

        # First submission
        submission1 = submission_repo.create(Submission(
            id=None, assignment_id=sample_assignment.get_id(),
            student_id=sample_student.get_id(), version=1,
            language="python", status="graded", score=75,
            is_late=False, created_at=datetime.now(),
            updated_at=datetime.now(), grade_at=datetime.now()
        ))

        # Second submission (resubmit)
        submission2 = submission_repo.create(Submission(
            id=None, assignment_id=sample_assignment.get_id(),
            student_id=sample_student.get_id(), version=2,
            language="python", status="pending", score=None,
            is_late=False, created_at=datetime.now(),
            updated_at=datetime.now(), grade_at=None
        ))

        # Verify version increment
        assert submission2.version == 2
        assert submission2.version > submission1.version

    def test_view_grades_and_complete_course(self, clean_db, sample_student,
                                              sample_course, sample_assignment,
                                              enrollment_repo, submission_repo):
        """Test student viewing grades and completing course"""
        from core.entities.enrollment import Enrollment
        from core.entities.submission import Submission

        # Enroll
        enrollment = enrollment_repo.enroll(Enrollment(
            student_id=sample_student.get_id(),
            course_id=sample_course.get_id(),
            status="enrolled",
            enrolled_at=datetime.now(),
            dropped_at=None,
            final_grade=None
        ))

        # Submit and grade assignment
        submission = submission_repo.create(Submission(
            id=None, assignment_id=sample_assignment.get_id(),
            student_id=sample_student.get_id(), version=1,
            language="python", status="graded", score=92,
            is_late=False, created_at=datetime.now(),
            updated_at=datetime.now(), grade_at=datetime.now()
        ))

        # Complete course
        enrollment.status = "completed"
        enrollment.final_grade = 92.0
        completed_enrollment = enrollment_repo.update(enrollment)

        # Verify completion
        assert completed_enrollment.status == "completed"
        assert completed_enrollment.final_grade == 92.0

        # Verify can view submission
        submissions = submission_repo.list_by_student(sample_student.get_id())
        assert len(submissions) >= 1
