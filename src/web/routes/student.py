import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from web.utils import login_required, get_service
from core.exceptions.validation_error import ValidationError
from datetime import datetime
from web.routes.profile_shared import profile_view, profile_update_logic

student_bp = Blueprint('student', __name__)

@student_bp.route('/profile')
@login_required
def profile():
    return profile_view()

@student_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    return profile_update_logic('student')

@student_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    student_service = get_service('student_service')
    assignment_repo = get_service('assignment_repo')
    user_repo = get_service('user_repo')
    result_repo = get_service('result_repo')
    enrollment_repo = get_service('enrollment_repo')
    peer_review_repo = get_service('peer_review_repo')
    
    current_user = user_repo.get_by_id(user_id)
    
    # Check enrollments
    enrollments = enrollment_repo.list_by_student(user_id)
    enrolled_courses = [e for e in enrollments if e.status == 'enrolled']
    
    # Get pending peer reviews
    all_reviews = peer_review_repo.list_by_reviewer(user_id)
    pending_reviews = [r for r in all_reviews if not r.is_submitted]
    # Attach submission and assignment to each pending review for display
    for r in pending_reviews:
        r.submission = get_service('submission_repo').get_by_id(r.get_submission_id())
        if r.submission:
            r.submission.assignment = assignment_repo.get_by_id(r.submission.get_assignment_id())
    
    # Get parameters
    filter_type = request.args.get('filter', 'all')
    search_query = request.args.get('search', '').lower()
    sort_by = request.args.get('sort', 'due_date')

    submissions = student_service.get_student_submissions(user_id)
    user_submissions = {s.get_assignment_id(): s for s in submissions}
    
    for s in submissions:
        s.assignment = assignment_repo.get_by_id(s.get_assignment_id())
    
    all_assignments = assignment_repo.get_all()
    # Student only sees published assignments
    visible_assignments = [a for a in all_assignments if a.is_published]
    
    now = datetime.now()
    
    assignments_data = []
    for a in visible_assignments:
        sub = user_submissions.get(a.get_id())
        
        # Determine status
        if sub:
            status = 'completed' if sub.status in ['graded', 'submitted'] else 'in_progress'
        else:
            # Handle string or datetime due_date
            due_date = a.due_date
            if isinstance(due_date, str):
                try:
                    due_date = datetime.fromisoformat(due_date.replace('Z', ''))
                except ValueError:
                    due_date = now # Fallback
            
            if due_date < now:
                status = 'overdue'
            else:
                status = 'pending' # Or in_progress if explicitly started

        # Apply search
        if search_query and search_query not in a.title.lower() and search_query not in (a.description or '').lower():
            continue
            
        # Apply filter
        if filter_type != 'all' and status != filter_type:
            # Note: 'in_progress' in tabs might mean pending/incomplete
            if filter_type == 'in_progress' and status not in ['pending', 'in_progress']:
                continue
            elif filter_type == 'completed' and status != 'completed':
                continue
            elif filter_type == 'overdue' and status != 'overdue':
                continue
            elif filter_type not in ['in_progress', 'completed', 'overdue']:
                pass

        assignments_data.append({
            'entity': a,
            'status': status,
            'score': sub.score if sub else None,
            'submission': sub
        })

    # Apply sorting
    if sort_by == 'title':
        assignments_data.sort(key=lambda x: x['entity'].title)
    elif sort_by == 'due_date':
        assignments_data.sort(key=lambda x: x['entity'].due_date)
    else:
        assignments_data.sort(key=lambda x: x['entity'].due_date)

    # Simplified stats for display
    stats = {
        'total_assignments': len(visible_assignments),
        'active_assignments': len([a for a in assignments_data if a['status'] in ['pending', 'in_progress']]),
        'passed_tests': len([a for a in assignments_data if a['status'] == 'completed']),
        'pending_submissions': len([a for a in assignments_data if a['status'] == 'overdue']),
        'average_score': round(sum(a['score'] for a in assignments_data if a['score']) / len([a for a in assignments_data if a['score']]), 1) if [a for a in assignments_data if a['score']] else 0,
        'total_submissions': len(submissions)
    }
    
    return render_template('dashboard.html',
        user=current_user,
        assignments=[a['entity'] for a in assignments_data],
        assignments_with_status=assignments_data,
        submissions=submissions,
        recent_submissions=sorted(submissions, key=lambda s: s.created_at if s.created_at else datetime.min, reverse=True)[:5],
        pending_reviews=pending_reviews,
        enrolled_courses=enrolled_courses,
        current_user=current_user,
        stats=stats)

@student_bp.route('/assignments')
@login_required
def assignments():
    user_id = session['user_id']
    assignment_repo = get_service('assignment_repo')
    student_service = get_service('student_service')
    user_repo = get_service('user_repo')
    
    current_user = user_repo.get_by_id(user_id)
    
    # Get parameters
    search_query = request.args.get('search', '').lower()
    status_filter = request.args.get('status', '') # active, closed
    sort_by = request.args.get('sort', 'due_date')
    
    all_assignments = assignment_repo.get_all()
    published_assignments = [a for a in all_assignments if a.is_published]
    submissions = student_service.get_student_submissions(user_id)
    user_submissions = {s.get_assignment_id(): s for s in submissions}
    
    now = datetime.now()
    filtered_assignments = []
    for a in published_assignments:
        # Resolve due_date if string
        due_date = a.due_date
        if isinstance(due_date, str):
            try:
                due_date = datetime.fromisoformat(due_date.replace('Z', ''))
            except (ValueError, AttributeError):
                due_date = now
        
        is_overdue = due_date < now
        
        # Apply search
        if search_query and search_query not in a.title.lower() and search_query not in (a.description or '').lower():
            continue
            
        # Apply status filter
        if status_filter == 'active' and is_overdue:
            continue
        if status_filter == 'closed' and not is_overdue:
            continue
            
        # Inject submission status for template
        a.student_submission = user_submissions.get(a.get_id())
        a.is_overdue = is_overdue
        
        filtered_assignments.append(a)
        
    # Apply sorting
    if sort_by == 'name':
        filtered_assignments.sort(key=lambda x: x.title)
    elif sort_by == 'recent':
        filtered_assignments.sort(key=lambda x: x.created_at if x.created_at else datetime.min, reverse=True)
    else: # due_date
        filtered_assignments.sort(key=lambda x: x.due_date)
    
    pagination = type('Pagination', (), {
        'pages': 1, 'page': 1, 'has_prev': False, 'has_next': False,
        'prev_num': 1, 'next_num': 1, 'iter_pages': lambda: [1]
    })()
    
    return render_template('assignments.html',
        user=current_user,
        assignments=filtered_assignments,
        user_submissions=user_submissions,
        current_user=current_user,
        pagination=pagination)

@student_bp.route('/assignment/<assignment_id>')
@login_required
def assignment_detail(assignment_id):
    user_id = session['user_id']
    assignment_repo = get_service('assignment_repo')
    student_service = get_service('student_service')
    user_repo = get_service('user_repo')
    
    current_user = user_repo.get_by_id(user_id)
    assignment = assignment_repo.get_by_id(assignment_id)
    if not assignment:
        flash('Assignment not found', 'error')
        return redirect(url_for('student.assignments'))
        
    submissions = student_service.get_student_submissions(user_id)
    # The template expects 'latest_submission'
    latest_submission = next((s for s in sorted(submissions, key=lambda x: x.version, reverse=True) if str(s.get_assignment_id()) == str(assignment_id)), None)
    
    return render_template('assignment_detail.html',
        user=current_user,
        assignment=assignment,
        latest_submission=latest_submission,
        current_user=current_user)

@student_bp.route('/submit/<assignment_id>', methods=['GET', 'POST'])
@login_required
def submit_code(assignment_id):
    user_id = session['user_id']
    assignment_repo = get_service('assignment_repo')
    student_service = get_service('student_service')
    user_repo = get_service('user_repo')
    
    current_user = user_repo.get_by_id(user_id)
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
        except (sqlite3.Error, ValidationError, Exception) as e:
            flash(str(e), 'error')
            
    submissions = student_service.get_student_submissions(user_id)
    previous_submissions = sorted(
        [s for s in submissions if str(s.get_assignment_id()) == str(assignment_id)],
        key=lambda x: x.version,
        reverse=True
    )
            
    return render_template('submit_code.html',
        user=current_user,
        assignment=assignment,
        previous_submissions=previous_submissions,
        current_user=current_user)

@student_bp.route('/results/<submission_id>')
@login_required
def submission_results(submission_id):
    user_id = session['user_id']
    submission_repo = get_service('submission_repo')
    assignment_repo = get_service('assignment_repo')
    result_repo = get_service('result_repo')
    
    user_repo = get_service('user_repo')
    current_user = user_repo.get_by_id(user_id)
    
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
        user=current_user,
        submission=submission,
        assignment=assignment,
        test_results=test_results,
        current_user=current_user)
