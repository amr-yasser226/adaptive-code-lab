import pytest
from datetime import datetime
from Backend.Model.Student_model import Student
from Backend.Model.Course_model import Course
from Backend.Model.Assignment_model import Assignment
from Backend.Model.Enrollment_model import Enrollment
from Backend.Model.Submission_model import Submission


@pytest.mark.model
@pytest.mark.unit
class TestStudentModelNewFunctions:
    """Test suite for new Student model functions"""
    
    def test_enroll_course_success(self, sample_student, sample_course, 
                                    course_repo, enrollment_repo):
        """Test successful course enrollment"""
        enrolled = sample_student.Enroll_course(
            sample_course.get_id(),
            course_repo,
            enrollment_repo
        )
        
        assert enrolled is not None
        assert enrolled.get_student_id() == sample_student.get_id()
        assert enrolled.get_course_id() == sample_course.get_id()
        assert enrolled.status == "enrolled"
    
    def test_enroll_course_nonexistent_course(self, sample_student, 
                                               course_repo, enrollment_repo):
        """Test enrolling in a non-existent course raises exception"""
        with pytest.raises(Exception, match="Course does not exist"):
            sample_student.Enroll_course(99999, course_repo, enrollment_repo)
    
    def test_enroll_course_already_enrolled(self, sample_student, sample_course,
                                             course_repo, enrollment_repo):
        """Test enrolling in already enrolled course raises exception"""
        # First enrollment
        sample_student.Enroll_course(
            sample_course.get_id(),
            course_repo,
            enrollment_repo
        )
        
        # Try to enroll again
        with pytest.raises(Exception, match="already enrolled"):
            sample_student.Enroll_course(
                sample_course.get_id(),
                course_repo,
                enrollment_repo
            )
    
    def test_submit_assignment_success(self, sample_student, sample_assignment,
                                        sample_course, assignment_repo, 
                                        submission_repo, enrollment_repo):
        """Test successful assignment submission"""
        # Enroll student first
        enrollment = Enrollment(
            student_id=sample_student.get_id(),
            course_id=sample_course.get_id(),
            status="enrolled",
            final_grade=None,
            enrolled_at=datetime.now(),
            dropped_at=None
        )
        enrollment_repo.enroll(enrollment)
        
        # Submit assignment
        submission = sample_student.Submit_assignment(
            sample_assignment.get_id(),
            "print('hello')",
            assignment_repo,
            submission_repo,
            enrollment_repo
        )
        
        assert submission is not None
        assert submission.get_student_id() == sample_student.get_id()
        assert submission.get_assignment_id() == sample_assignment.get_id()
        assert submission.version == 1
    
    def test_submit_assignment_nonexistent_assignment(self, sample_student,
                                                       assignment_repo,
                                                       submission_repo,
                                                       enrollment_repo):
        """Test submitting to non-existent assignment raises exception"""
        with pytest.raises(Exception, match="Assignment does not exist"):
            sample_student.Submit_assignment(
                99999,
                "code",
                assignment_repo,
                submission_repo,
                enrollment_repo
            )
    
    def test_submit_assignment_not_enrolled(self, sample_student, 
                                             sample_assignment,
                                             assignment_repo, submission_repo,
                                             enrollment_repo):
        """Test submitting when not enrolled raises exception"""
        with pytest.raises(Exception, match="not enrolled"):
            sample_student.Submit_assignment(
                sample_assignment.get_id(),
                "code",
                assignment_repo,
                submission_repo,
                enrollment_repo
            )
    
    def test_submit_assignment_increments_version(self, sample_student,
                                                   sample_assignment,
                                                   sample_course,
                                                   assignment_repo,
                                                   submission_repo,
                                                   enrollment_repo):
        """Test that resubmission increments version number"""
        # Enroll student
        enrollment = Enrollment(
            student_id=sample_student.get_id(),
            course_id=sample_course.get_id(),
            status="enrolled",
            final_grade=None,
            enrolled_at=datetime.now(),
            dropped_at=None
        )
        enrollment_repo.enroll(enrollment)
        
        # First submission
        sub1 = sample_student.Submit_assignment(
            sample_assignment.get_id(),
            "code v1",
            assignment_repo,
            submission_repo,
            enrollment_repo
        )
        
        # Second submission
        sub2 = sample_student.Submit_assignment(
            sample_assignment.get_id(),
            "code v2",
            assignment_repo,
            submission_repo,
            enrollment_repo
        )
        
        assert sub1.version == 1
        assert sub2.version == 2
    
    def test_view_gpa_no_grades(self, sample_student, submission_repo, 
                                 course_repo):
        """Test GPA calculation with no grades returns 0.0"""
        gpa = sample_student.View_GPA(submission_repo, course_repo)
        assert gpa == 0.0
    
    def test_view_gpa_with_grades(self, sample_student, sample_course,
                                   sample_assignment, submission_repo,
                                   course_repo):
        """Test GPA calculation with graded submissions"""
        # Create and grade a submission
        submission = Submission(
            id=None,
            assignment_id=sample_assignment.get_id(),
            student_id=sample_student.get_id(),
            version=1,
            language="python",
            status="graded",
            score=85.0,
            is_late=False,
            created_at=None,
            updated_at=None,
            grade_at=datetime.now()
        )
        saved_submission = submission_repo.create(submission)
        
        # Update with grade
        saved_submission.score = 85.0
        saved_submission.grade_at = datetime.now()
        submission_repo.update(saved_submission)
        
        gpa = sample_student.View_GPA(submission_repo, course_repo)
        
        # GPA = (85 * 3 credits) / 3 credits = 85.0
        assert gpa == 85.0
    
    def test_get_submissions(self, sample_student, sample_assignment,
                              submission_repo):
        """Test retrieving all student submissions"""
        # Create multiple submissions
        for i in range(3):
            submission = Submission(
                id=None,
                assignment_id=sample_assignment.get_id(),
                student_id=sample_student.get_id(),
                version=i+1,
                language="python",
                status="pending",
                score=0.0,
                is_late=False,
                created_at=None,
                updated_at=None,
                grade_at=None
            )
            submission_repo.create(submission)
        
        submissions = sample_student.get_submissions(submission_repo)
        assert len(submissions) >= 3
    
    def test_drop_course_success(self, sample_student, sample_course,
                                  enrollment_repo):
        """Test successful course drop"""
        # Enroll first
        enrollment = Enrollment(
            student_id=sample_student.get_id(),
            course_id=sample_course.get_id(),
            status="enrolled",
            final_grade=None,
            enrolled_at=datetime.now(),
            dropped_at=None
        )
        enrollment_repo.enroll(enrollment)
        
        # Drop course
        dropped = sample_student.Drop_course(
            sample_course.get_id(),
            enrollment_repo
        )
        
        assert dropped.status == "dropped"
        assert dropped.dropped_at is not None
    
    def test_drop_course_not_enrolled(self, sample_student, sample_course,
                                       enrollment_repo):
        """Test dropping course when not enrolled raises exception"""
        with pytest.raises(Exception, match="not enrolled"):
            sample_student.Drop_course(
                sample_course.get_id(),
                enrollment_repo
            )