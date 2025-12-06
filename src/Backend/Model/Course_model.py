from Backend.Model.Enrollment_model import Enrollment
from datetime import datetime

class Course:
    def __init__(self, id, instructor_id, code , title ,describtion,year,semester,max_students,created_at,status,updated_at,credits):

        self.__id = id
        self.__instructor_id = instructor_id
        self.code = code
        self.title = title
        self.describtion = describtion
        self.year = year
        self.semester = semester
        self.max_students = max_students
        self.created_at = created_at
        self.status = status
        self.updated_at = updated_at
        self.credits = credits
        
    def get_id(self):
        return self.__id
    
    def get_instructor_id(self):
            return self.__instructor_id
    
    def add_assignment(self, assignment, assignment_repo):
        # Check the Course's status
        Course_status = self.status
        if Course_status != "active":
               raise Exception("Cannot add assignment in inactive course")
        
        # Create assignment
        created_assignment = assignment_repo.create(assignment)
        return created_assignment
    
    def enroll_student(self, student_id, enrollment_repo, student_repo):

        # Check if student
        student = student_repo.get_by_id(student_id)
        if not student:
            raise Exception("Student not found")
        
        # Check the Course's status
        Course_status = self.status
        if Course_status != "active":
            raise Exception("Cannot enroll in inactive course")
        
        # Check if student is already enrolled
        course_id = self.__id
        existing_enrollment = enrollment_repo.get(student_id, course_id)
        if existing_enrollment and existing_enrollment.status == "enrolled":
            raise Exception("Student is already enrolled in this course")
        
        # Allows students that completed the course to be able to enroll again
        enrollments = enrollment_repo.list_by_course(course_id)
        active_enrollments = [e for e in enrollments if e.status == "enrolled"]

        max_students_enrolled = self.max_students
        if len(active_enrollments) >= max_students_enrolled:
            raise Exception("Course is at maximum capacity")
        
        new_enrollment = Enrollment(
            student_id=student_id,
            course_id=course_id,
            status="enrolled",
            enrolled_at=datetime.now(),
            dropped_at=None,
            final_grade=None
        )
        
        return enrollment_repo.enroll(new_enrollment)
    
    def list_assignments(self, assignment_repo):
        course_id = self.__id
        return assignment_repo.list_by_course(course_id)
    
    def get_enrolled_student(self, enrollment_repo):
        course_id = self.__id
        enrollments = enrollment_repo.list_by_course(course_id)
        return [e for e in enrollments if e.status == "enrolled"]

    def archive(self, course_repo):
        course_id = self.__id
        course_repo.archive(course_id)

    def publish(self, course_repo):
        course_id = self.__id
        course_repo.publish(course_id)
    