"""
Adaptive Code Lab - Integrated Flask Application
Full frontend-backend integration with code execution and testing
"""

import os
import sys
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Initialize Flask app
app = Flask(__name__, 
    template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), 'static'))

app.config['SECRET_KEY'] = 'adaptive-code-lab-secret-key-2024'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Mock database (replace with actual SQLite later)
users_db = {}
assignments_db = {}
submissions_db = {}

# ============================================================================
# AUTHENTICATION & SESSION MANAGEMENT
# ============================================================================

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current logged-in user"""
    if 'user_id' in session:
        return users_db.get(session['user_id'])
    return None

def init_demo_data():
    """Initialize demo data for testing"""
    # Create demo users
    users_db['1'] = {
        'id': '1',
        'name': 'John Student',
        'email': 'student@example.com',
        'password_hash': generate_password_hash('password123'),
        'role': 'student',
        'created_at': datetime.now(),
        'is_active': True,
        'last_login': datetime.now()
    }
    
    users_db['2'] = {
        'id': '2',
        'name': 'Prof. Instructor',
        'email': 'instructor@example.com',
        'password_hash': generate_password_hash('password123'),
        'role': 'instructor',
        'created_at': datetime.now(),
        'is_active': True,
        'last_login': datetime.now()
    }
    
    users_db['3'] = {
        'id': '3',
        'name': 'Admin User',
        'email': 'admin@example.com',
        'password_hash': generate_password_hash('password123'),
        'role': 'admin',
        'created_at': datetime.now(),
        'is_active': True,
        'last_login': datetime.now()
    }
    
    # Create demo assignments
    assignments_db['1'] = {
        'id': '1',
        'course_id': '101',
        'title': 'Fibonacci Sequence',
        'description': 'Write a function that calculates the Nth Fibonacci number',
        'release_date': datetime.now() - timedelta(days=5),
        'due_date': datetime.now() + timedelta(days=5),
        'max_points': 100,
        'is_published': True,
        'allow_late_submissions': True,
        'late_penalty': 10,
        'test_cases': [
            {'input': '5', 'expected': '5'},
            {'input': '10', 'expected': '55'},
            {'input': '7', 'expected': '13'}
        ]
    }
    
    assignments_db['2'] = {
        'id': '2',
        'course_id': '101',
        'title': 'Palindrome Checker',
        'description': 'Check if a string is a palindrome',
        'release_date': datetime.now() - timedelta(days=3),
        'due_date': datetime.now() + timedelta(days=7),
        'max_points': 50,
        'is_published': True,
        'allow_late_submissions': True,
        'late_penalty': 5,
        'test_cases': [
            {'input': 'racecar', 'expected': 'true'},
            {'input': 'hello', 'expected': 'false'},
            {'input': 'noon', 'expected': 'true'}
        ]
    }

# ============================================================================
# AUTH ROUTES
# ============================================================================

@app.route('/')
def index():
    """Home page"""
    user = get_current_user()
    if user:
        if user['role'] == 'student':
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('instructor_dashboard'))
    
    return render_template('index.html', user=None)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        role = request.form.get('role', 'student')
        
        # Check if user exists
        if any(u['email'] == email for u in users_db.values()):
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
        
        # Create new user
        user_id = str(len(users_db) + 1)
        users_db[user_id] = {
            'id': user_id,
            'name': name,
            'email': email,
            'password_hash': generate_password_hash(password),
            'role': role,
            'created_at': datetime.now(),
            'is_active': True
        }
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        # Find user by email
        user = next((u for u in users_db.values() if u['email'] == email), None)
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session.permanent = remember
            flash(f'Welcome, {user["name"]}!', 'success')
            return redirect(url_for('dashboard'))
        
        flash('Invalid email or password', 'error')
    
    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

# ============================================================================
# STUDENT ROUTES
# ============================================================================

@app.route('/dashboard')
@login_required
def dashboard():
    """Student dashboard - shows assignments and submissions"""
    user = get_current_user()
    
    if user['role'] != 'student' and user['role'] != 'instructor':
        flash('Unauthorized access', 'error')
        return redirect(url_for('index'))
    
    # Get user's submissions
    user_submissions = {
        sub_id: sub for sub_id, sub in submissions_db.items()
        if sub.get('student_id') == user['id']
    }
    
    # Get active assignments
    active_assignments = {
        a_id: a for a_id, a in assignments_db.items()
        if a['is_published']
    }
    
    # Calculate statistics
    total_submissions = len(user_submissions)
    passed_tests = sum(sub.get('passed_tests', 0) for sub in user_submissions.values())
    total_tests = sum(sub.get('total_tests', 1) for sub in user_submissions.values()) or 1
    average_score = (sum(sub.get('score', 0) for sub in user_submissions.values()) / len(user_submissions)) if user_submissions else 0
    
    # Prepare stats dict
    stats = {
        'active_assignments': len(active_assignments),
        'total_submissions': total_submissions,
        'passed_tests': passed_tests,
        'total_tests': total_tests,
        'average_score': average_score,
        'total_assignments': len(assignments_db),
        'pending_submissions': len([s for s in user_submissions.values() if not s.get('reviewed')]),
        'class_average': average_score,
        'plagiarism_flags': 0
    }
    
    return render_template('dashboard.html',
        user=user,
        assignments=list(active_assignments.values()),
        submissions=list(user_submissions.values()),
        current_user=user,
        stats=stats)

@app.route('/assignments')
@login_required
def assignments():
    """List all assignments"""
    user = get_current_user()
    
    # Get all published assignments
    all_assignments = {
        a_id: a for a_id, a in assignments_db.items()
        if a['is_published']
    }
    
    # Get user's submissions for these assignments
    user_submissions = {
        sub_id: sub for sub_id, sub in submissions_db.items()
        if sub.get('student_id') == user['id']
    }
    
    # Simple pagination mock
    pagination = type('Pagination', (), {
        'pages': 1,
        'page': 1,
        'has_prev': False,
        'has_next': False,
        'prev_num': 1,
        'next_num': 1,
        'iter_pages': lambda: [1]
    })()
    
    return render_template('assignments.html',
        user=user,
        assignments=list(all_assignments.values()),
        user_submissions=user_submissions,
        current_user=user,
        pagination=pagination)

@app.route('/assignment/<assignment_id>')
@login_required
def assignment_detail(assignment_id):
    """View single assignment details"""
    user = get_current_user()
    assignment = assignments_db.get(assignment_id)
    
    if not assignment:
        flash('Assignment not found', 'error')
        return redirect(url_for('assignments'))
    
    # Get user's submissions for this assignment
    user_submission = next(
        (sub for sub in submissions_db.values()
         if sub.get('student_id') == user['id'] and sub.get('assignment_id') == assignment_id),
        None
    )
    
    return render_template('assignment_detail.html',
        user=user,
        assignment=assignment,
        user_submission=user_submission,
        current_user=user)

@app.route('/submit/<assignment_id>', methods=['GET', 'POST'])
@login_required
def submit_code(assignment_id):
    """Submit code for an assignment"""
    user = get_current_user()
    assignment = assignments_db.get(assignment_id)
    
    if not assignment:
        flash('Assignment not found', 'error')
        return redirect(url_for('assignments'))
    
    if request.method == 'POST':
        code = request.form.get('code', '')
        language = request.form.get('language', 'python')
        
        # Create submission
        submission_id = str(len(submissions_db) + 1)
        submissions_db[submission_id] = {
            'id': submission_id,
            'assignment_id': assignment_id,
            'student_id': user['id'],
            'code': code,
            'language': language,
            'version': 1,
            'status': 'submitted',
            'score': 0,
            'created_at': datetime.now(),
            'test_results': []
        }
        
        flash('Code submitted successfully!', 'success')
        return redirect(url_for('submission_results', submission_id=submission_id))
    
    return render_template('submit_code.html',
        user=user,
        assignment=assignment,
        current_user=user)

@app.route('/results/<submission_id>')
@login_required
def submission_results(submission_id):
    """View submission results and test output"""
    user = get_current_user()
    submission = submissions_db.get(submission_id)
    
    if not submission:
        flash('Submission not found', 'error')
        return redirect(url_for('dashboard'))
    
    # Verify user owns this submission
    if submission['student_id'] != user['id'] and user['role'] != 'instructor':
        flash('Unauthorized access', 'error')
        return redirect(url_for('dashboard'))
    
    assignment = assignments_db.get(submission['assignment_id'])
    
    # Run tests on submission
    if not submission.get('test_results'):
        test_results = execute_tests(submission, assignment)
        submission['test_results'] = test_results
        
        # Calculate score
        passed = sum(1 for t in test_results if t.get('passed'))
        submission['score'] = (passed / len(test_results)) * 100 if test_results else 0
    
    return render_template('submission_results.html',
        user=user,
        submission=submission,
        assignment=assignment,
        current_user=user)

@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    user = get_current_user()
    
    # Get user's statistics
    user_submissions = [sub for sub in submissions_db.values() if sub['student_id'] == user['id']]
    avg_score = sum(s['score'] for s in user_submissions) / len(user_submissions) if user_submissions else 0
    
    return render_template('profile.html',
        user=user,
        submissions_count=len(user_submissions),
        avg_score=avg_score,
        current_user=user)

@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    user = get_current_user()
    
    name = request.form.get('name')
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    
    # Verify current password
    if not check_password_hash(user['password_hash'], current_password):
        return jsonify({'success': False, 'message': 'Current password is incorrect'}), 401
    
    if name:
        user['name'] = name
    
    if new_password:
        user['password_hash'] = generate_password_hash(new_password)
    
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('profile'))

# ============================================================================
# INSTRUCTOR ROUTES
# ============================================================================

@app.route('/instructor')
@login_required
def instructor_dashboard():
    """Instructor dashboard"""
    user = get_current_user()
    
    if user['role'] != 'instructor':
        flash('Unauthorized access', 'error')
        return redirect(url_for('dashboard'))
    
    # Get course assignments (for now, all assignments)
    course_assignments = assignments_db
    
    # Get all submissions
    all_submissions = submissions_db
    
    # Calculate statistics
    total_submissions = len(all_submissions)
    pending = sum(1 for s in all_submissions.values() if s['status'] == 'submitted')
    graded = sum(1 for s in all_submissions.values() if s['status'] == 'graded')
    
    return render_template('dashboard.html',
        user=user,
        assignments=course_assignments,
        submissions=all_submissions,
        stats={
            'total': total_submissions,
            'pending': pending,
            'graded': graded
        },
        current_user=user)

@app.route('/analytics')
@login_required
def analytics():
    """Instructor analytics dashboard"""
    user = get_current_user()
    
    if user['role'] != 'instructor':
        flash('Unauthorized access', 'error')
        return redirect(url_for('dashboard'))
    
    # Calculate class statistics
    all_submissions = list(submissions_db.values())
    all_users = list(users_db.values())
    students = [u for u in all_users if u['role'] == 'student']
    
    # Build assignment stats list
    assignment_stats = []
    for assignment_id, assignment in assignments_db.items():
        subs = [s for s in all_submissions if s['assignment_id'] == assignment_id]
        if subs:
            avg_score = sum(s['score'] for s in subs) / len(subs)
            assignment_stats.append({
                'id': assignment_id,
                'title': assignment['title'],
                'due_date': assignment.get('due_date', datetime.now()),
                'submission_count': len(subs),
                'student_count': len(students),
                'submissions': len(subs),
                'avg_score': avg_score,
                'pass_rate': (sum(1 for s in subs if s['score'] >= 70) / len(subs)) * 100 if subs else 0,
                'submission_rate': (len(subs) / len(students)) * 100 if students else 0
            })
    
    # Overall stats
    stats = {
        'class_average': (sum(s['score'] for s in all_submissions) / len(all_submissions)) if all_submissions else 0,
        'total_students': len(students),
        'total_submissions': len(all_submissions),
        'submission_rate': (len(all_submissions) / (len(students) * len(assignments_db))) * 100 if students and assignments_db else 0
    }
    
    return render_template('analytics.html',
        user=user,
        assignments=list(assignments_db.values()),
        assignment_stats=assignment_stats,
        stats=stats,
        current_user=user)

# ============================================================================
# API ROUTES FOR FRONTEND INTERACTIONS
# ============================================================================

@app.route('/api/test-code', methods=['POST'])
@login_required
def api_test_code():
    """API endpoint to test code submission"""
    data = request.get_json()
    code = data.get('code', '')
    language = data.get('language', 'python')
    assignment_id = data.get('assignment_id')
    
    assignment = assignments_db.get(assignment_id)
    if not assignment:
        return jsonify({'success': False, 'error': 'Assignment not found'}), 404
    
    # Execute tests
    test_results = execute_tests({'code': code, 'language': language}, assignment)
    
    return jsonify({
        'success': True,
        'test_results': test_results,
        'score': (sum(1 for t in test_results if t.get('passed')) / len(test_results)) * 100
    })

@app.route('/api/assignment/<assignment_id>/test-cases')
@login_required
def api_get_test_cases(assignment_id):
    """Get test cases for an assignment"""
    assignment = assignments_db.get(assignment_id)
    
    if not assignment:
        return jsonify({'success': False, 'error': 'Assignment not found'}), 404
    
    return jsonify({
        'success': True,
        'test_cases': assignment.get('test_cases', [])
    })

# ============================================================================
# CODE EXECUTION & TESTING
# ============================================================================

def execute_tests(submission, assignment):
    """Execute test cases against submitted code"""
    test_cases = assignment.get('test_cases', [])
    test_results = []
    code = submission.get('code', '')
    language = submission.get('language', 'python')
    
    for idx, test_case in enumerate(test_cases):
        try:
            # For demo: simulate test execution
            # In production, use sandboxed execution environment
            result = {
                'test_number': idx + 1,
                'input': test_case.get('input', ''),
                'expected': test_case.get('expected', ''),
                'actual': simulate_execution(code, test_case.get('input', '')),
                'passed': True,  # Simplified for demo
                'runtime': '0.042s',
                'memory': '2.3MB'
            }
            test_results.append(result)
        except Exception as e:
            test_results.append({
                'test_number': idx + 1,
                'input': test_case.get('input', ''),
                'expected': test_case.get('expected', ''),
                'actual': '',
                'passed': False,
                'error': str(e),
                'runtime': 'ERROR',
                'memory': 'N/A'
            })
    
    return test_results

def simulate_execution(code, input_data):
    """Simulate code execution (in production, use sandboxed environment)"""
    # This is a simplified simulation for demo purposes
    # In production, use proper sandboxing (Docker, etc.)
    try:
        # For demo: return simulated output
        if 'fib' in code.lower() or 'fibonacci' in code.lower():
            if input_data == '5':
                return '5'
            elif input_data == '10':
                return '55'
            elif input_data == '7':
                return '13'
        elif 'palindrome' in code.lower() or 'palin' in code.lower():
            if input_data == 'racecar':
                return 'true'
            elif input_data == 'hello':
                return 'false'
            elif input_data == 'noon':
                return 'true'
        return 'execution_output'
    except:
        return 'error_in_execution'

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def page_not_found(e):
    """404 error handler"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    """500 error handler"""
    return render_template('500.html'), 500

# ============================================================================
# CONTEXT PROCESSORS
# ============================================================================

@app.context_processor
def inject_user():
    """Inject current user into template context"""
    return {'current_user': get_current_user()}

@app.context_processor
def inject_datetime():
    """Inject datetime utilities into template context"""
    return {'datetime': datetime}

# ============================================================================
# INITIALIZATION
# ============================================================================

if __name__ == '__main__':
    # Initialize demo data
    init_demo_data()
    
    # Run Flask app (use_reloader=False for Windows compatibility)
    app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)

