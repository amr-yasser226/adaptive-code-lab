from flask import Blueprint, render_template, request, redirect, url_for, flash, session, make_response
from web.utils import login_required, instructor_required, get_service
from datetime import datetime
import io
import csv

instructor_bp = Blueprint('instructor', __name__)

@instructor_bp.route('/dashboard')
@login_required
@instructor_required
def dashboard():
    user_id = session['user_id']
    instructor_service = get_service('instructor_service')
    user_repo = get_service('user_repo')
    
    current_user = user_repo.get_by_id(user_id)
    
    # Get stats using service methods (assumed to be implemented)
    # For now, using placeholders if methods don't exist
    total_students = 0 # len(instructor_service.get_all_students())
    active_assignments = 0 # len(instructor_service.get_active_assignments())
    submissions_review = 0 # len(instructor_service.get_pending_submissions())
    flagged_cases = 0 # len(instructor_service.get_flagged_cases())
    
    stats = {
        'total_students': total_students,
        'active_assignments': active_assignments,
        'submissions_review': submissions_review,
        'flagged_cases': flagged_cases
    }
    
    recent_submissions = [] # instructor_service.get_recent_submissions(limit=5)
    flagged_submissions = [] # instructor_service.get_flagged_submissions(limit=5)
    
    return render_template('dashboard.html',
        user=current_user,
        stats=stats,
        recent_submissions=recent_submissions,
        flagged_submissions=flagged_submissions)

@instructor_bp.route('/analytics')
@login_required
@instructor_required
def analytics():
    # Placeholder for analytics logic
    # In a real app, this would fetch data from repositories
    stats = {
        'class_average': 85.5,
        'total_students': 42,
        'total_submissions': 150,
        'submission_rate': 95.0
    }
    
    assignment_stats = [
        {
            'id': 1,
            'title': 'Intro to Python',
            'due_date': datetime.now(),
            'submission_count': 40,
            'student_count': 42,
            'average_score': 88.0,
            'pass_rate': 95.0,
            'median_submission_time': '2 days'
        },
        {
            'id': 2,
            'title': 'Data Structures',
            'due_date': datetime.now(),
            'submission_count': 35,
            'student_count': 42,
            'average_score': 72.5,
            'pass_rate': 65.0,
            'median_submission_time': '4 days'
        }
    ]
    
    performance_tiers = {
        'excellent': 15,
        'good': 12,
        'average': 10,
        'needs_improvement': 5
    }
    
    all_assignments = [] # Fetch relevant assignments for filter
    
    return render_template('analytics.html',
        user={'role': 'instructor'},
        stats=stats, 
        assignment_stats=assignment_stats,
        performance_tiers=performance_tiers,
        assignments=all_assignments)

@instructor_bp.route('/analytics/export')
@login_required
@instructor_required
def export_csv():
    # Placeholder export logic
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Student', 'Assignment', 'Score', 'Date'])
    cw.writerow(['Student A', 'Intro to Python', '90', '2023-10-01'])
    
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=export.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@instructor_bp.route('/analytics/assignment/<assignment_id>')
@login_required
@instructor_required
def assignment_detail(assignment_id):
    # This might need a specific template or reuse existing detail with instructor view
    return redirect(url_for('student.assignment_detail', assignment_id=assignment_id)) # Temporary redirect

@instructor_bp.route('/plagiarism')
@login_required
@instructor_required
def plagiarism_dashboard():
    # Placeholder
    return render_template('plagiarism_report.html',
        user={'role': 'instructor'},
        flagged_pairs=[])

@instructor_bp.route('/plagiarism/compare/<pair_id>')
@login_required
@instructor_required
def plagiarism_compare(pair_id):
    return "Comparison View Placeholder"
