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
    
    submissions = student_service.get_student_submissions(user_id)
    
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
        user={'role': 'student', 'id': user_id, 'name': 'Student'}, # TODO: Fetch real user object
        assignments=active_assignments,
        submissions=submissions,
        current_user={'role': 'student', 'id': user_id, 'name': 'Student'},
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
    user_submission = next((s for s in submissions if str(s.assignment_id) == str(assignment_id)), None)
    
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
    
    submission = None 
    
    if not submission:
        flash('Submission not found', 'error')
        return redirect(url_for('student.dashboard'))
    
    if str(submission.student_id) != str(user_id):
        flash('Unauthorized access', 'error')
        return redirect(url_for('student.dashboard'))
        
    assignment = assignment_repo.get_by_id(submission.assignment_id)
    
    test_results = [] # submission.test_results
    
    return render_template('submission_results.html',
        user={'role': 'student'},
        submission=submission,
        assignment=assignment,
        current_user={'role': 'student'})

@student_bp.route('/profile')
@login_required
def profile():
    user_id = session['user_id']
    student_service = get_service('student_service')
    # auth_service = get_service('auth_service') # to get user details
    
    submissions = student_service.get_student_submissions(user_id)
    avg_score = 0 # Calculate from submissions
    
    return render_template('profile.html',
        user={'role': 'student', 'name': 'Student'}, # TODO: real user
        submissions_count=len(submissions),
        avg_score=avg_score,
        current_user={'role': 'student'})

@student_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    # Placeholder for profile update
    flash('Profile update not implemented in this refactor phase', 'warning')
    return redirect(url_for('student.profile'))