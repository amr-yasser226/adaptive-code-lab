from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from web.utils import login_required, get_service
from core.exceptions.validation_error import ValidationError
from datetime import datetime

student_bp = Blueprint('student', __name__)

@student_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    student_service = get_service('student_service')
    assignment_repo = get_service('assignment_repo')
    user_repo = get_service('user_repo')
    
    current_user = user_repo.get_by_id(user_id)
    
    submissions = student_service.get_student_submissions(user_id)
    for s in submissions:
        s.assignment = assignment_repo.get_by_id(s.get_assignment_id())
    
    all_assignments = assignment_repo.get_all()
    active_assignments = [a for a in all_assignments if a.is_published]

    total_submissions = len(submissions)
    passed_tests = 0 
    total_tests = 0
    
    stats = {
        'active_assignments': len(active_assignments),
        'total_submissions': total_submissions,
        'passed_tests': passed_tests,
        'total_tests': total_tests,
        'average_score': 0, # Placeholder
        'total_assignments': len(all_assignments),
        'pending_submissions': 0,
        'class_average': 0,
        'plagiarism_flags': 0
    }
    
    return render_template('dashboard.html',
        user=current_user,
        assignments=active_assignments,
        submissions=submissions,
        current_user=current_user,
        stats=stats)

@student_bp.route('/assignments')
@login_required
def assignments():
    user_id = session['user_id']
    assignment_repo = get_service('assignment_repo')
    student_service = get_service('student_service')
    
    all_assignments = assignment_repo.get_all()
    published_assignments = [a for a in all_assignments if a.is_published]
    submissions = student_service.get_student_submissions(user_id)
    
    user_submissions = {s.assignment_id: s for s in submissions}
    
    pagination = type('Pagination', (), {
        'pages': 1, 'page': 1, 'has_prev': False, 'has_next': False,
        'prev_num': 1, 'next_num': 1, 'iter_pages': lambda: [1]
    })()
    
    return render_template('assignments.html',
        user={'role': 'student'}, # Placeholder
        assignments=published_assignments,
        user_submissions=user_submissions,
        current_user={'role': 'student'},
        pagination=pagination)

@student_bp.route('/assignment/<assignment_id>')
@login_required
def assignment_detail(assignment_id):
    user_id = session['user_id']
    assignment_repo = get_service('assignment_repo')
    student_service = get_service('student_service')
    
    assignment = assignment_repo.get_by_id(assignment_id)
    if not assignment:
        flash('Assignment not found', 'error')
        return redirect(url_for('student.assignments'))
        
    submissions = student_service.get_student_submissions(user_id)
    user_submission = next((s for s in submissions if str(s.get_assignment_id()) == str(assignment_id)), None)
    
    return render_template('assignment_detail.html',
        user={'role': 'student'},
        assignment=assignment,
        user_submission=user_submission,
        current_user={'role': 'student'})

@student_bp.route('/submit/<assignment_id>', methods=['GET', 'POST'])
@login_required
def submit_code(assignment_id):
    user_id = session['user_id']
    assignment_repo = get_service('assignment_repo')
    student_service = get_service('student_service')
    
    assignment = assignment_repo.get_by_id(assignment_id)
    if not assignment:
        flash('Assignment not found', 'error')
        return redirect(url_for('student.assignments'))
        
    if request.method == 'POST':
        code = request.form.get('code', '')
        
        try:
            submission = student_service.submit_assignment(user_id, assignment_id, code)
            flash('Code submitted successfully!', 'success')

            return redirect(url_for('student.dashboard')) 
        except Exception as e:
            flash(str(e), 'error')
            
    return render_template('submit_code.html',
        user={'role': 'student'},
        assignment=assignment,
        current_user={'role': 'student'})

@student_bp.route('/results/<submission_id>')
@login_required
def submission_results(submission_id):
    user_id = session['user_id']
    submission_repo = get_service('submission_repo')
    assignment_repo = get_service('assignment_repo')
    result_repo = get_service('result_repo')
    
    # Actually fetch the submission from repository
    submission = submission_repo.get_by_id(submission_id)
    
    if not submission:
        flash('Submission not found', 'error')
        return redirect(url_for('student.dashboard'))
    
    if str(submission.get_student_id()) != str(user_id):
        flash('Unauthorized access', 'error')
        return redirect(url_for('student.dashboard'))
        
    assignment = assignment_repo.get_by_id(submission.get_assignment_id())
    
    # Fetch test results for this submission
    test_results = result_repo.find_by_submission(submission_id) if result_repo else []
    
    return render_template('submission_results.html',
        user={'role': 'student'},
        submission=submission,
        assignment=assignment,
        test_results=test_results,
        current_user={'role': 'student'})

@student_bp.route('/profile')
@login_required
def profile():
    user_id = session['user_id']
    student_service = get_service('student_service')
    user_repo = get_service('user_repo')
    
    # Try to get student, fall back to basic user info
    try:
        student = student_service.get_student(user_id)
        submissions = student_service.get_student_submissions(user_id)
    except Exception:
        # User exists but may not have a student record
        student = user_repo.get_by_id(user_id)
        submissions = []
    
    # Calculate stats
    avg_score = 0
    if submissions:
        scores = [s.score for s in submissions if hasattr(s, 'score') and s.score is not None]
        avg_score = sum(scores) / len(scores) if scores else 0
    
    # Create a user-like object for current_user template variable
    current_user = {
        'name': getattr(student, 'name', 'User'),
        'email': getattr(student, 'email', ''),
        'role': session.get('user_role', 'student')
    }
    
    from markupsafe import Markup
    
    class StubField:
        def __init__(self, name, type="text"):
            self.name = name
            self.type = type
            self.errors = []
            
        def __call__(self, **kwargs):
            attrs = [f'type="{self.type}"', f'name="{self.name}"']
            for k, v in kwargs.items():
                if k == "class_": k = "class"
                attrs.append(f'{k}="{v}"')
            return Markup(f'<input {" ".join(attrs)}>')
    
    class StubForm:
        current_password = StubField("current_password", "password")
        new_password = StubField("new_password", "password")
        confirm_password = StubField("confirm_password", "password")
        csrf_token = Markup('<input type="hidden" name="csrf_token" value="">')
        email_on_grade = StubField("email_on_grade", "checkbox")
        email_on_hint = StubField("email_on_hint", "checkbox")
        email_on_deadline = StubField("email_on_deadline", "checkbox")
    
    stats = {
        'average_score': avg_score,
        'class_average': 75.0,
        'assignments_completed': len([s for s in submissions if hasattr(s, 'status') and s.status == 'completed']) if submissions else 0,
        'total_assignments': 10
    }
    
    return render_template('profile.html',
        user=student,
        current_user=type('User', (), current_user)(),
        form=StubForm(),
        notification_form=StubForm(),
        stats=stats,
        submissions_count=len(submissions) if submissions else 0,
        avg_score=avg_score)

@student_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    user_id = session['user_id']
    auth_service = get_service('auth_service')
    
    current_password = request.form.get('current_password', '').strip()
    new_password = request.form.get('new_password', '').strip()
    confirm_password = request.form.get('confirm_password', '').strip()
    
    # Validate input
    if not current_password or not new_password:
        flash('Please fill in all password fields', 'warning')
        return redirect(url_for('student.profile'))
    
    if new_password != confirm_password:
        flash('New passwords do not match', 'error')
        return redirect(url_for('student.profile'))
    
    if len(new_password) < 8:
        flash('New password must be at least 8 characters', 'error')
        return redirect(url_for('student.profile'))
    
    try:
        auth_service.change_password(user_id, current_password, new_password)
        flash('Password updated successfully!', 'success')
    except Exception as e:
        flash(str(e), 'error')
    
    return redirect(url_for('student.profile'))