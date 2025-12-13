import os
import sys
from datetime import timedelta
from pathlib import Path
from flask import Flask, render_template

# Add src folder to sys.path to ensure 'core' and 'infrastructure' are importable as top-level modules
# This aligns with how repositories and services import each other.
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import Services and Repositories (Standardized to remove 'src.' prefix)
from infrastructure.database.connection import DatabaseManager
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.repositories.student_repository import StudentRepository
from infrastructure.repositories.instructor_repository import InstructorRepository
from infrastructure.repositories.assignment_repository import AssignmentRepository
from infrastructure.repositories.submission_repository import SubmissionRepository
from infrastructure.repositories.course_repository import CourseRepository
from infrastructure.repositories.enrollment_repository import EnrollmentRepository
from infrastructure.repositories.similarity_flag_repository import SimilarityFlagRepository

from core.services.auth_service import AuthService
from core.services.student_service import StudentService
from core.services.instructor_service import InstructorService

from web.routes.auth import auth_bp
from web.routes.student import student_bp
from web.routes.instructor import instructor_bp
from web.routes.api import api_bp

def create_app(test_config=None):
    """Application Factory (Bonus #2)"""
    app = Flask(__name__, 
        template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
        static_folder=os.path.join(os.path.dirname(__file__), 'static'))

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'adaptive-code-lab-secret-key-2024')
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

    if test_config:
        app.config.update(test_config)

    # Initialize Database Singleton (Bonus #4)
    # This ensures the DB connection logic is ready
    db_manager = DatabaseManager.get_instance()
    db_connection = db_manager.get_connection()

    # --- Dependency Injection Setup ---
    # 1. Initialize Repositories (Inject DB connection)
    user_repo = UserRepository(db_connection)
    student_repo = StudentRepository(db_connection)
    instructor_repo = InstructorRepository(db_connection)
    assignment_repo = AssignmentRepository(db_connection)
    submission_repo = SubmissionRepository(db_connection)
    course_repo = CourseRepository(db_connection)
    enrollment_repo = EnrollmentRepository(db_connection)
    flag_repo = SimilarityFlagRepository(db_connection)

    # 2. Initialize Services with Dependencies
    auth_service = AuthService(user_repo)
    
    student_service = StudentService(
        student_repo=student_repo,
        course_repo=course_repo,
        enrollment_repo=enrollment_repo,
        assignment_repo=assignment_repo,
        submission_repo=submission_repo
    )
    
    instructor_service = InstructorService(
        instructor_repo=instructor_repo,
        course_repo=course_repo,
        assignment_repo=assignment_repo,
        submission_repo=submission_repo,
        enrollment_repo=enrollment_repo,
        flag_repo=flag_repo
    )

    # 3. Store Services in App Context
    app.extensions['services'] = {
        'auth_service': auth_service,
        'student_service': student_service,
        'instructor_service': instructor_service,
        'user_repo': user_repo,
        'assignment_repo': assignment_repo, # Exposed for direct read access
        'submission_repo': submission_repo,
        'course_repo': course_repo,
        'enrollment_repo': enrollment_repo
    }

    # --- Register Blueprints (Bonus #1) ---
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(instructor_bp)
    app.register_blueprint(api_bp)

    # --- Routes ---
    @app.route('/')
    def index():
        from flask import session, redirect, url_for
        if 'user_id' in session:
            role = session.get('user_role')
            if role == 'student':
                return redirect(url_for('student.dashboard'))
            elif role == 'instructor':
                return redirect(url_for('instructor.dashboard'))
        return render_template('index.html', user=None)

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template('500.html'), 500
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)

