from flask import Blueprint, render_template, request, redirect, url_for, flash, session, make_response, Response
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
    user_repo = get_service('user_repo')
    assignment_repo = get_service('assignment_repo')
    submission_repo = get_service('submission_repo')
    flag_repo = get_service('flag_repo')
    enrollment_repo = get_service('enrollment_repo')
    course_repo = get_service('course_repo')
    
    current_user = user_repo.get_by_id(user_id)
    
    # Get real stats from repositories
    courses = course_repo.list_by_instructor(user_id)
    all_assignments = assignment_repo.get_all()
    # Filter assignments for instructor's courses
    instructor_course_ids = [c.get_id() for c in courses]
    instructor_assignments = [a for a in all_assignments if a.get_course_id() in instructor_course_ids]
    active_assignments = [a for a in instructor_assignments if a.is_published]
    all_submissions = submission_repo.get_all() if hasattr(submission_repo, 'get_all') else []
    
    # Get enrolled students count (unique students)
    total_students = len(set(s.get_student_id() for s in all_submissions)) if all_submissions else 0
    
    # Get pending submissions (status = 'pending')
    pending_submissions = [s for s in all_submissions if getattr(s, 'status', '') == 'pending']
    for s in pending_submissions:
        s.student = user_repo.get_by_id(s.get_student_id())
        s.assignment = assignment_repo.get_by_id(s.get_assignment_id())
    
    # Get flagged submissions
    all_flags = flag_repo.get_all() if hasattr(flag_repo, 'get_all') else []
    flagged_count = len([f for f in all_flags if not getattr(f, 'is_dismissed', True)])
    
    stats = {
        'total_assignments': len(all_assignments),
        'active_assignments': len(active_assignments),
        'passed_tests': 0,
        'pending_submissions': len(pending_submissions),
        'class_average': 0,
        'plagiarism_flags': flagged_count,
        'total_students': total_students
    }
    
    # Get recent submissions (last 5)
    recent_submissions = sorted(all_submissions, key=lambda s: getattr(s, 'created_at', datetime.min), reverse=True)[:5]
    for s in recent_submissions:
        s.student = user_repo.get_by_id(s.get_student_id())
        s.assignment = assignment_repo.get_by_id(s.get_assignment_id())
    
    # Get flagged submissions
    flagged_submissions = [s for s in all_submissions if any(
        getattr(f, 'submission_id', None) == s.get_id() for f in all_flags if not getattr(f, 'is_dismissed', True)
    )][:5]
    
    return render_template('dashboard.html',
        user=current_user,
        stats=stats,
        courses=courses,
        assignments=instructor_assignments,
        submissions=recent_submissions,
        recent_submissions=recent_submissions,
        flagged_submissions=flagged_submissions)

@instructor_bp.route('/analytics')
@login_required
@instructor_required
def analytics():
    user_id = session['user_id']
    user_repo = get_service('user_repo')
    assignment_repo = get_service('assignment_repo')
    submission_repo = get_service('submission_repo')
    
    current_user = user_repo.get_by_id(user_id)
    
    # Read filter parameters
    filter_assignment = request.args.get('assignment', '')
    filter_date_range = request.args.get('date_range', 'all')
    
    # Fetch real data
    all_assignments = assignment_repo.get_all()
    all_submissions = submission_repo.get_all() if hasattr(submission_repo, 'get_all') else []
    
    # Apply assignment filter
    if filter_assignment:
        try:
            filter_id = int(filter_assignment)
            all_submissions = [s for s in all_submissions if s.get_assignment_id() == filter_id]
        except ValueError:
            pass  # Invalid filter, show all
    
    # Apply date range filter
    if filter_date_range != 'all':
        from datetime import timedelta
        now = datetime.now()
        if filter_date_range == 'week':
            cutoff = now - timedelta(days=7)
        elif filter_date_range == 'month':
            cutoff = now - timedelta(days=30)
        elif filter_date_range == 'semester':
            cutoff = now - timedelta(days=120)
        else:
            cutoff = None
        
        if cutoff:
            filtered = []
            for s in all_submissions:
                if s.created_at:
                    try:
                        # Handle both string and datetime
                        created = s.created_at if hasattr(s.created_at, 'timestamp') else datetime.fromisoformat(str(s.created_at)[:19])
                        if created >= cutoff:
                            filtered.append(s)
                    except:
                        filtered.append(s)  # Keep if can't parse
                else:
                    filtered.append(s)
            all_submissions = filtered
    
    # Calculate real stats
    total_students = len(set(s.get_student_id() for s in all_submissions)) if all_submissions else 0
    total_submissions = len(all_submissions)
    
    # Calculate average score
    scores = [s.score for s in all_submissions if hasattr(s, 'score') and s.score is not None]
    class_average = sum(scores) / len(scores) if scores else 0.0
    
    # Submission rate (submissions / (students * assignments))
    submission_rate = 0.0
    if total_students > 0 and len(all_assignments) > 0:
        expected = total_students * len(all_assignments)
        submission_rate = (total_submissions / expected * 100) if expected > 0 else 0.0
    
    stats = {
        'class_average': round(class_average, 1),
        'total_students': total_students,
        'total_submissions': total_submissions,
        'submission_rate': round(submission_rate, 1)
    }
    
    # Build assignment stats
    assignment_stats = []
    for assignment in all_assignments:
        assignment_submissions = [s for s in all_submissions if s.get_assignment_id() == assignment.get_id()]
        sub_scores = [s.score for s in assignment_submissions if hasattr(s, 'score') and s.score is not None]
        avg_score = sum(sub_scores) / len(sub_scores) if sub_scores else 0.0
        pass_count = len([s for s in sub_scores if s >= 50])
        pass_rate = (pass_count / len(sub_scores) * 100) if sub_scores else 0.0
        
        assignment_stats.append({
            'id': assignment.get_id(),
            'title': assignment.title,
            'due_date': assignment.due_date,
            'submission_count': len(assignment_submissions),
            'student_count': total_students,
            'average_score': round(avg_score, 1),
            'pass_rate': round(pass_rate, 1),
            'median_submission_time': 'N/A'
        })
    
    # Performance tiers based on real scores
    performance_tiers = {
        'excellent': len([s for s in scores if s >= 90]),
        'good': len([s for s in scores if 70 <= s < 90]),
        'average': len([s for s in scores if 50 <= s < 70]),
        'needs_improvement': len([s for s in scores if s < 50])
    }
    
    return render_template('analytics.html',
        user=current_user,
        stats=stats, 
        assignment_stats=assignment_stats,
        performance_tiers=performance_tiers,
        assignments=all_assignments)

@instructor_bp.route('/analytics/export')
@login_required
@instructor_required
def export_csv():
    submission_repo = get_service('submission_repo')
    assignment_repo = get_service('assignment_repo')
    user_repo = get_service('user_repo')
    
    all_submissions = submission_repo.get_all() if hasattr(submission_repo, 'get_all') else []
    
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Student ID', 'Student Name', 'Assignment', 'Score', 'Status', 'Submitted At'])
    
    for sub in all_submissions:
        student = user_repo.get_by_id(sub.get_student_id())
        assignment = assignment_repo.get_by_id(sub.get_assignment_id())
        cw.writerow([
            sub.get_student_id(),
            student.name if student else 'Unknown',
            assignment.title if assignment else 'Unknown',
            sub.score if hasattr(sub, 'score') else 'N/A',
            sub.status if hasattr(sub, 'status') else 'N/A',
            str(sub.created_at)[:16] if sub.created_at else 'N/A'
        ])
    
    # Create proper CSV response with filename
    filename = f"grades_export_{datetime.now().strftime('%Y%m%d')}.csv"
    return Response(
        si.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Type': 'text/csv; charset=utf-8'
        }
    )

@instructor_bp.route('/analytics/assignment/<assignment_id>')
@login_required
@instructor_required
def assignment_detail(assignment_id):
    assignment_repo = get_service('assignment_repo')
    submission_repo = get_service('submission_repo')
    user_repo = get_service('user_repo')
    
    assignment = assignment_repo.get_by_id(assignment_id)
    if not assignment:
        flash('Assignment not found', 'error')
        return redirect(url_for('instructor.analytics'))
    
    # Get all submissions for this assignment
    all_submissions = submission_repo.get_all() if hasattr(submission_repo, 'get_all') else []
    assignment_submissions = [s for s in all_submissions if str(s.assignment_id) == str(assignment_id)]
    
    # Calculate stats for template (FIX BUG #2)
    scores = [s.score for s in assignment_submissions if hasattr(s, 'score') and s.score is not None]
    stats = {
        'total_submissions': len(assignment_submissions),
        'average_score': sum(scores) / len(scores) if scores else 0,
        'pass_rate': (len([s for s in scores if s >= 50]) / len(scores) * 100) if scores else 0
    }
    
    return render_template('assignment_detail.html',
        user={'role': 'instructor'},
        assignment=assignment,
        submissions=assignment_submissions,
        stats=stats,
        current_user={'role': 'instructor'})

@instructor_bp.route('/plagiarism')
@login_required
@instructor_required
def plagiarism_dashboard():
    flag_repo = get_service('flag_repo')
    submission_repo = get_service('submission_repo')
    user_repo = get_service('user_repo')
    
    # Get all unreviewed similarity flags
    all_flags = flag_repo.list_unreviewed() if hasattr(flag_repo, 'list_unreviewed') else []
    
    # Build flagged pairs with details
    flagged_pairs = []
    for flag in all_flags:
        if getattr(flag, 'is_dismissed', False):
            continue
        
        submission = submission_repo.get_by_id(flag.submission_id) if hasattr(flag, 'submission_id') else None
        student = user_repo.get_by_id(submission.student_id) if submission else None
        
        flagged_pairs.append({
            'id': flag.get_id(),
            'submission_id': getattr(flag, 'submission_id', None),
            'student_name': student.name if student else 'Unknown',
            'similarity_score': getattr(flag, 'similarity_score', 0),
            'matched_submission_id': getattr(flag, 'matched_submission_id', None),
            'status': getattr(flag, 'status', 'pending'),
            'created_at': getattr(flag, 'created_at', None)
        })
    
    return render_template('plagiarism_report.html',
        user={'role': 'instructor'},
        flagged_pairs=flagged_pairs)

@instructor_bp.route('/plagiarism/compare/<pair_id>')
@login_required
@instructor_required
def plagiarism_compare(pair_id):
    flag_repo = get_service('flag_repo')
    submission_repo = get_service('submission_repo')
    user_repo = get_service('user_repo')
    
    # Get the similarity flag
    flag = flag_repo.get_by_id(pair_id)
    if not flag:
        flash('Comparison not found', 'error')
        return redirect(url_for('instructor.plagiarism_dashboard'))
    
    # Get both submissions
    submission1 = submission_repo.get_by_id(flag.submission_id) if hasattr(flag, 'submission_id') else None
    submission2 = submission_repo.get_by_id(flag.matched_submission_id) if hasattr(flag, 'matched_submission_id') else None
    
    student1 = user_repo.get_by_id(submission1.student_id) if submission1 else None
    student2 = user_repo.get_by_id(submission2.student_id) if submission2 else None
    
    return render_template('plagiarism_compare.html',
        user={'role': 'instructor'},
        flag=flag,
        submission1=submission1,
        submission2=submission2,
        student1=student1,
        student2=student2,
        similarity_score=getattr(flag, 'similarity_score', 0))

@instructor_bp.route('/plagiarism/review/<flag_id>', methods=['POST'])
@login_required
@instructor_required
def plagiarism_review(flag_id):
    instructor_id = session['user_id']
    instructor_service = get_service('instructor_service')
    
    action = request.form.get('action') # approve, dismiss, escalate
    notes = request.form.get('notes')
    
    try:
        updated_flag = instructor_service.review_similarity(
            instructor_id=instructor_id,
            flag_id=flag_id,
            action=action,
            notes=notes
        )
        flash(f'Successfully {action}ed similarity flag.', 'success')
    except Exception as e:
        flash(f'Error reviewing flag: {str(e)}', 'error')
        
    return redirect(url_for('instructor.plagiarism_dashboard'))
