from Backend.Model.User_model import User
from Backend.Model.Course_model import Course
from Backend.Model.Assignmnets_model import Assignmnets
from datetime import datetime

class Instructor(User):
    def __init__(self, id, name, email, password, created_at, updated_at, instructor_code, bio, office_hours, is_Active=True):
        super().__init__(id=id, name=name, email=email, password=password, role="instructor", created_at=created_at, updated_at=updated_at, is_Active=is_Active)
        self.instructor_code = instructor_code
        self.bio = bio
        self.office_hours = office_hours
    
    def create_course(self, course_repo, code, title, description, year, semester, max_students, credits):
        instructor_id = self.get_id()

        # Create new course
        new_course = Course(
            id=None,
            instructor_id=instructor_id,
            code=code,
            title=title,
            describtion=description,
            year=year,
            semester=semester,
            max_students=max_students,
            created_at=datetime.now(),
            status="inactive",  # New courses start as inactive
            updated_at=datetime.now(),
            credits=credits
        )
        
        return course_repo.create(new_course)
    
    def create_assignment(self, course_id, assignment_repo, course_repo, title, description, release_date, due_date, max_points, allow_late_submissions=False, late_submission_penalty=0):
                
        # Verify the course belongs to this instructor
        course = course_repo.get_by_id(course_id)
        if not course:
            raise Exception("Course not found")
        
        instructor_id = self.get_id()
        if course.get_instructor_id() != instructor_id:
            raise Exception("You can only create assignments for your own courses")
        
        # Create new assignment
        new_assignment = Assignmnets(
            id=None,
            course_id=course_id,
            title=title,
            describtion=description,
            releaseDate=release_date,
            due_date=due_date,
            max_points=max_points,
            is_published=False,  # New assignments start unpublished
            allow_late_submissions=allow_late_submissions,
            late_submission_penalty=late_submission_penalty,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        return course.add_assignment(new_assignment, assignment_repo)
    
    def review_similarity(self, flag_id, action, notes):
        pass
    
    def export_grades(self, course_id, course_repo, enrollment_repo):
        course = course_repo.get_by_id(course_id)
        if not course:
            raise Exception("Course not found")
        
        instructor_id = self.get_id()
        if course.get_instructor_id() != instructor_id:
            raise Exception("You can only export grades for your own courses")
        
        enrollments = enrollment_repo.list_by_course(course_id)
        
        grades_data = []
        for enrollment in enrollments:
            grades_data.append({
                'student_id': enrollment.get_student_id(),
                'status': enrollment.status,
                'final_grade': enrollment.final_grade,
                'enrolled_at': enrollment.enrolled_at,
                'dropped_at': enrollment.dropped_at
            })
        
        return grades_data
    
    def get_courses(self, course_repo):
        instructor_id = self.get_id()
        return course_repo.list_by_instructor(instructor_id)