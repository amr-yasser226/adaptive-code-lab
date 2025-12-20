import os
import sys
from datetime import timedelta
from pathlib import Path
from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

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
from infrastructure.repositories.test_case_repository import TestCaseRepository
from infrastructure.repositories.notification_repository import NotificationRepository
from infrastructure.repositories.peer_review_repository import PeerReviewRepository
from infrastructure.repositories.admin_repository import AdminRepository
from infrastructure.repositories.result_repository import ResultRepository
from infrastructure.repositories.sandbox_job_repository import SandboxJobRepository
from infrastructure.repositories.remediation_repository import RemediationRepository
from infrastructure.repositories.file_repository import FileRepository
from infrastructure.repositories.audit_log_repository import AuditLogRepository
from infrastructure.repositories.draft_repository import DraftRepository

from infrastructure.repositories.settings_repository import SettingsRepository
from infrastructure.repositories.hint_repository import HintRepository
from infrastructure.ai.groq_client import GroqClient


from core.services.auth_service import AuthService
from core.services.student_service import StudentService
from core.services.instructor_service import InstructorService
from core.services.test_case_service import TestCaseService
from core.services.assignment_service import AssignmentService
from core.services.notification_service import NotificationService
from core.services.peer_review_service import PeerReviewService
from core.services.admin_service import AdminService
from core.services.sandbox_service import SandboxService
from core.services.remediation_service import RemediationService
from core.services.file_service import FileService
from core.services.audit_log_service import AuditLogService
from core.services.draft_service import DraftService
from core.services.hint_service import HintService
from core.services.enrollment_service import EnrollmentService


from web.routes.auth import auth_bp
from web.routes.student import student_bp
from web.routes.instructor import instructor_bp
from web.routes.api import api_bp
from web.routes.admin import admin_bp
from web.routes.peer_review import peer_review_bp
from web.routes.notification import notification_bp
from web.routes.assignment import assignment_bp
from web.routes.remediation import remediation_bp
from web.routes.file import files_bp
from web.routes.course import course_bp
from web.routes.enrollment import enrollment_bp
from web.routes.audit_log import audit_bp
from web.routes.hint import hint_bp
from web.routes.test_case import test_case_bp
from web.routes.submission import submission_bp
from web.routes.result import result_bp


def create_app(test_config=None):
    """Application Factory (Bonus #2)"""
    app = Flask(__name__, 
        template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
        static_folder=os.path.join(os.path.dirname(__file__), 'static'))

    # Security: Enforce SECRET_KEY is set
    secret_key = os.getenv('SECRET_KEY')
    if not secret_key:
        raise RuntimeError(
            "SECRET_KEY environment variable must be set! "
            "Generate one with: python -c 'import secrets; print(secrets.token_hex(32))'"
        )
    app.config['SECRET_KEY'] = secret_key
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
    
    # Session security flags
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    # Enable in production with HTTPS
    if os.getenv('ENV') == 'production' or os.getenv('FLASK_ENV') == 'production':
        app.config['SESSION_COOKIE_SECURE'] = True

    if test_config:
        app.config.update(test_config)

    # --- Custom Jinja2 Filters ---
    from datetime import datetime as dt
    def format_date(value, fmt='%b %d, %Y'):
        """Safely format a date value (string or datetime) to a string."""
        if value is None:
            return 'N/A'
        if isinstance(value, str):
            # Try parsing common formats
            for parse_fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S']:
                try:
                    value = dt.strptime(value, parse_fmt)
                    break
                except ValueError:
                    continue
            else:
                return value  # Return as-is if unparseable
        return value.strftime(fmt)
    
    app.jinja_env.filters['format_date'] = format_date
    
    # --- Context Processors ---
    @app.context_processor
    def inject_user():
        from flask import session
        from web.utils import get_current_user
        try:
            user = get_current_user() if 'user_id' in session else None
        except Exception:
            user = None
        return dict(current_user=user)

    @app.context_processor
    def inject_settings():
        from web.utils import get_service
        try:
            settings_repo = get_service('settings_repo')
            settings = {s['key']: s['value'] for s in settings_repo.list_all()}
        except Exception:
            settings = {}
        return dict(site_settings=settings)

    @app.context_processor
    def inject_notifications():
        from web.utils import get_service, get_current_user
        from flask import session
        try:
            if 'user_id' in session:
                user = get_current_user()
                notification_service = get_service('notification_service')
                unread = notification_service.get_user_notifications(user, only_unread=True)
                return dict(unread_notifications_count=len(unread))
        except Exception:
            pass
        return dict(unread_notifications_count=0)

    # Initialize CSRF Protection
    csrf = CSRFProtect(app)
    
    # Exempt API routes from CSRF for programmatic access
    from web.routes.api import api_bp
    csrf.exempt(api_bp)
    
    # Initialize Rate Limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )

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
    test_case_repo = TestCaseRepository(db_connection)
    notification_repo = NotificationRepository(db_connection)
    peer_review_repo = PeerReviewRepository(db_connection)
    admin_repo = AdminRepository(db_connection)
    result_repo = ResultRepository(db_connection)
    sandbox_job_repo = SandboxJobRepository(db_connection)
    remediation_repo = RemediationRepository(db_connection)
    file_repo = FileRepository(db_connection)
    audit_repo = AuditLogRepository(db_connection)
    draft_repo = DraftRepository(db_connection)
    hint_repo= HintRepository(db_connection)
    settings_repo = SettingsRepository(db_connection)


    # 2. Initialize Services with Dependencies
    groq_client = GroqClient()
    auth_service = AuthService(user_repo)
    sandbox_service = SandboxService(
        sandbox_job_repo=sandbox_job_repo,
        submission_repo=submission_repo,
        groq_client=groq_client
    )
    student_service = StudentService(
        student_repo=student_repo,
        course_repo=course_repo,
        enrollment_repo=enrollment_repo,
        assignment_repo=assignment_repo,
        submission_repo=submission_repo,
        sandbox_service=sandbox_service,
        test_case_repo=test_case_repo,
        result_repo=result_repo
    )
    instructor_service = InstructorService(
        instructor_repo=instructor_repo,
        course_repo=course_repo,
        assignment_repo=assignment_repo,
        submission_repo=submission_repo,
        enrollment_repo=enrollment_repo,
        flag_repo=flag_repo,
        user_repo=user_repo  # Added to fix course creation bug
    )
    test_case_service = TestCaseService(
        testcase_repo=test_case_repo,
        assignment_repo=assignment_repo,
        course_repo=course_repo
    )
    assignment_service = AssignmentService(
        assignment_repo=assignment_repo,
        course_repo=course_repo,
        submission_repo=submission_repo
    )
    notification_service = NotificationService(notification_repo=notification_repo)

    file_service = FileService(file_repo=file_repo, submission_repo=submission_repo)

    audit_service = AuditLogService(audit_repo=audit_repo)

    peer_review_service = PeerReviewService(
        peer_review_repo=peer_review_repo,
        submission_repo=submission_repo,
        enrollment_repo=enrollment_repo,
        assignment_repo=assignment_repo,
        course_repo=course_repo
    )
    admin_service = AdminService(
        user_repo=user_repo,
        admin_repo=admin_repo,
        course_repo=course_repo,
        enrollment_repo=enrollment_repo,
        submission_repo=submission_repo,
        db_path=db_manager.db_path,
        settings_repo=settings_repo
    )
    hint_service = HintService(
        hint_repo=hint_repo,
        submission_repo=submission_repo,
        ai_client=groq_client
    )
    draft_service = DraftService(draft_repo=draft_repo)
    
    enrollment_service = EnrollmentService(
        enrollment_repo=enrollment_repo,
        course_repo=course_repo
    )

    remediation_service = RemediationService(
        remediation_repo=remediation_repo,
        result_repo=result_repo,
        submission_repo=submission_repo
    )
    
    sandbox_service = SandboxService(
        sandbox_job_repo=sandbox_job_repo,
        submission_repo=submission_repo,
        groq_client=groq_client
    )
    # 3. Store Services in App Context
    app.extensions['services'] = {
        'auth_service': auth_service,
        'student_service': student_service,
        'instructor_service': instructor_service,
        'test_case_service': test_case_service,
        'assignment_service': assignment_service,
        'notification_service': notification_service,
        'admin_service': admin_service,
        'peer_review_service': peer_review_service,
        'sandbox_service': sandbox_service,
        'remediation_service': remediation_service,
        'hint_service': hint_service,
        'draft_service': draft_service,
        'user_repo': user_repo,
        'student_repo': student_repo,
        'instructor_repo': instructor_repo,
        'assignment_repo': assignment_repo,
        'submission_repo': submission_repo,
        'course_repo': course_repo,
        'enrollment_repo': enrollment_repo,
        'test_case_repo': test_case_repo,
        'flag_repo': flag_repo,
        'file_repo': file_repo,
        'audit_repo': audit_repo,
        'sandbox_job_repo': sandbox_job_repo,
        'remediation_repo': remediation_repo,
        'notification_repo': notification_repo,
        'peer_review_repo': peer_review_repo,
        'admin_repo': admin_repo,
        'result_repo': result_repo,
        'draft_repo': draft_repo,
        'hint_repo': hint_repo,
        'file_service': file_service,
        'audit_service': audit_service,
        'enrollment_service': enrollment_service,
        'settings_repo': settings_repo
    }

    # --- Register Blueprints (Bonus #1) ---
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(instructor_bp, url_prefix='/instructor')
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(peer_review_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(assignment_bp)
    app.register_blueprint(remediation_bp, url_prefix='/student')  # FR-09
    app.register_blueprint(files_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(enrollment_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(hint_bp)
    app.register_blueprint(test_case_bp)
    app.register_blueprint(submission_bp)
    app.register_blueprint(result_bp)

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
            elif role == 'admin' :
                return redirect(url_for('admin.dashboard'))
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

