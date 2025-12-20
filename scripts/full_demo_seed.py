import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

DB_PATH = Path(__file__).parent.parent / 'data' / 'Accl_DB.db'


def get_connection():
    return sqlite3.connect(str(DB_PATH))


def seed_users(cursor):
    """FR-01: Create users with all roles"""
    print("\n[1/10] Creating test users (FR-01)...")
    password_hash = generate_password_hash('testpassword123')
    admin_hash = generate_password_hash('adminpassword123')
    
    users = [
        ('Alice Instructor', 'alice@accl.edu', password_hash, 'instructor'),
        ('Bob Student', 'bob@accl.edu', password_hash, 'student'),
        ('Charlie Student', 'charlie@accl.edu', password_hash, 'student'),
        ('Diana Student', 'diana@accl.edu', password_hash, 'student'),
        ('Admin User', 'admin@accl.edu', admin_hash, 'admin'),
    ]
    
    for name, email, pwd, role in users:
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO users (name, email, password_hash, role, is_active, created_at)
                VALUES (?, ?, ?, ?, 1, datetime('now'))
            ''', (name, email, pwd, role))
            print(f"    ✓ Created: {name} ({role})")
        else:
            print(f"    - Exists: {name}")
    
    return {
        'instructor': get_user_id(cursor, 'alice@accl.edu'),
        'student1': get_user_id(cursor, 'bob@accl.edu'),
        'student2': get_user_id(cursor, 'charlie@accl.edu'),
        'student3': get_user_id(cursor, 'diana@accl.edu'),
        'admin': get_user_id(cursor, 'admin@accl.edu'),
    }


def get_user_id(cursor, email):
    cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
    row = cursor.fetchone()
    return row[0] if row else None


def seed_courses(cursor, user_ids):
    """FR-02: Create courses with instructor"""
    print("\n[2/10] Creating courses (FR-02)...")
    
    courses = [
        ('CS101', 'Introduction to Programming', 'Learn Python basics', 'active', 3),
        ('CS201', 'Data Structures', 'Arrays, Lists, Trees', 'active', 3),
    ]
    
    for code, title, desc, status, credits in courses:
        cursor.execute('SELECT id FROM courses WHERE code = ?', (code,))
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO courses (code, title, description, instructor_id, year, semester, status, credits, created_at)
                VALUES (?, ?, ?, ?, '2025', 'Fall', ?, ?, datetime('now'))
            ''', (code, title, desc, user_ids['instructor'], status, credits))
            print(f"    ✓ Created: {code} - {title}")
        else:
            print(f"    - Exists: {code}")
    
    cursor.execute('SELECT id FROM courses WHERE code = ?', ('CS101',))
    return cursor.fetchone()[0]


def seed_assignments(cursor, course_id):
    """FR-02, FR-12: Create assignments with deadlines"""
    print("\n[3/10] Creating assignments (FR-02, FR-12)...")
    
    now = datetime.now()
    assignments = [
        ('Hello World', 'Print "Hello, World!" to stdout', now - timedelta(days=7), now + timedelta(days=7), 100),
        ('Sum Calculator', 'Calculate sum of numbers 1-N', now - timedelta(days=3), now + timedelta(days=14), 100),
        ('Fibonacci', 'Generate first N Fibonacci numbers', now + timedelta(days=1), now + timedelta(days=21), 100),
    ]
    
    assignment_ids = []
    for title, desc, release, due, points in assignments:
        cursor.execute('SELECT id FROM assignments WHERE title = ? AND course_id = ?', (title, course_id))
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO assignments 
                (course_id, title, description, release_date, due_date, max_points, is_published, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 1, datetime('now'))
            ''', (course_id, title, desc, release.strftime('%Y-%m-%d %H:%M:%S'), 
                  due.strftime('%Y-%m-%d %H:%M:%S'), points))
            cursor.execute('SELECT id FROM assignments WHERE title = ? AND course_id = ?', (title, course_id))
            print(f"    ✓ Created: {title}")
        else:
            print(f"    - Exists: {title}")
        
        cursor.execute('SELECT id FROM assignments WHERE title = ? AND course_id = ?', (title, course_id))
        assignment_ids.append(cursor.fetchone()[0])
    
    return assignment_ids


def seed_test_cases(cursor, assignment_ids):
    """FR-02, FR-05: Create test cases for grading"""
    print("\n[4/10] Creating test cases (FR-05)...")
    
    # Schema: assignment_id, name, stdin, descripion (typo in DB), expected_out, 
    #         timeout_ms, memory_limit_mb, points, is_visible, sort_order
    test_cases = [
        (assignment_ids[0], 'test_output', '', 'Check stdout', 'Hello, World!', 5000, 128, 100, 1, 1),
        (assignment_ids[1], 'test_sum_5', '5', 'Sum of 1-5', '15', 5000, 128, 50, 1, 1),
        (assignment_ids[1], 'test_sum_10', '10', 'Sum of 1-10', '55', 5000, 128, 50, 0, 2),  # Hidden
        (assignment_ids[2], 'test_fib_5', '5', 'First 5 Fib', '0 1 1 2 3', 5000, 128, 50, 1, 1),
        (assignment_ids[2], 'test_fib_10', '10', 'First 10 Fib', '0 1 1 2 3 5 8 13 21 34', 5000, 128, 50, 0, 2),
    ]
    
    count = 0
    for aid, name, stdin, desc, expected, timeout, memory, points, visible, order in test_cases:
        cursor.execute('SELECT id FROM test_cases WHERE assignment_id = ? AND name = ?', (aid, name))
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO test_cases 
                (assignment_id, name, stdin, descripion, expected_out, timeout_ms, memory_limit_mb, points, is_visible, sort_order, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            ''', (aid, name, stdin, desc, expected, timeout, memory, points, visible, order))
            count += 1
    
    print(f"    ✓ Created {count} new test cases")


def seed_enrollments(cursor, course_id, user_ids):
    """Enroll students in course"""
    print("\n[5/10] Enrolling students...")
    
    count = 0
    for key in ['student1', 'student2', 'student3']:
        cursor.execute('SELECT student_id FROM enrollments WHERE student_id = ? AND course_id = ?', 
                       (user_ids[key], course_id))
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO enrollments (student_id, course_id, status, enrolled_at)
                VALUES (?, ?, 'enrolled', datetime('now'))
            ''', (user_ids[key], course_id))
            count += 1
    
    print(f"    ✓ Enrolled {count} students")


def seed_submissions(cursor, assignment_ids, user_ids):
    """FR-03, FR-07: Create submissions including similar code"""
    print("\n[6/10] Creating submissions (FR-03, FR-07)...")
    
    code_hello = 'print("Hello, World!")'
    code_sum = '''n = int(input())
total = sum(range(1, n + 1))
print(total)'''
    
    submissions = [
        (user_ids['student1'], assignment_ids[0], code_hello, 'graded', 100),
        (user_ids['student2'], assignment_ids[0], code_hello, 'graded', 100),
        (user_ids['student1'], assignment_ids[1], code_sum, 'graded', 100),
        (user_ids['student3'], assignment_ids[1], 'print("testing")', 'submitted', 0),
    ]
    
    count = 0
    for student_id, assignment_id, code, status, score in submissions:
        cursor.execute('SELECT id FROM submissions WHERE student_id = ? AND assignment_id = ?',
                       (student_id, assignment_id))
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO submissions 
                (student_id, assignment_id, content, status, score, created_at)
                VALUES (?, ?, ?, ?, ?, datetime('now'))
            ''', (student_id, assignment_id, code, status, score))
            count += 1
    
    print(f"    ✓ Created {count} submissions")


def seed_notifications(cursor, user_ids):
    """FR-13: Create sample notifications"""
    print("\n[7/10] Creating notifications (FR-13)...")
    
    # Schema: user_id, message, type, is_read, created_at, read_at, link
    # type CHECK: 'info', 'warning', 'alert'
    notifications = [
        (user_ids['student1'], 'Your Hello World submission scored 100/100', 'info'),
        (user_ids['student2'], 'Sum Calculator assignment is now available', 'info'),
        (user_ids['instructor'], 'Potential plagiarism detected in submission', 'alert'),
    ]
    
    count = 0
    for user_id, message, ntype in notifications:
        cursor.execute('''
            INSERT INTO notifications 
            (user_id, message, type, is_read, created_at)
            VALUES (?, ?, ?, 0, datetime('now'))
        ''', (user_id, message, ntype))
        count += 1
    
    print(f"    ✓ Created {count} notifications")


def seed_audit_logs(cursor, user_ids):
    """FR-14: Create audit log entries"""
    print("\n[8/10] Creating audit logs (FR-14)...")
    
    logs = [
        (user_ids['admin'], 'create', 'user', user_ids['student1'], 'Created bob@accl.edu'),
        (user_ids['instructor'], 'create', 'assignment', 1, 'Created Hello World'),
    ]
    
    count = 0
    for actor_id, action, entity_type, entity_id, details in logs:
        cursor.execute("""
            INSERT INTO audit_logs (actor_user_id, action, entity_type, entity_id, details, created_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, (actor_id, action, entity_type, entity_id, details))
        count += 1
    
    print(f"    ✓ Created {count} audit entries")
def seed_drafts(cursor, user_ids, assignment_ids):
    """FR-15: Create draft submissions"""
    print("\n[9/10] Creating drafts (FR-15)...")
    
    draft_code = '''# Work in progress
def calculate_fibonacci(n):
    # TODO: implement
    pass'''
    
    cursor.execute('SELECT id FROM drafts WHERE user_id = ? AND assignment_id = ?',
                   (user_ids['student1'], assignment_ids[2]))
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO drafts 
            (user_id, assignment_id, content, saved_at)
            VALUES (?, ?, ?, datetime('now'))
        ''', (user_ids['student1'], assignment_ids[2], draft_code))
        print("    ✓ Created 1 draft")
    else:
        print("    - Draft exists")


def seed_similarity_flags(cursor, user_ids, assignment_ids):
    """FR-07: Create similarity flags"""
    print("\n[10/10] Creating similarity flags (FR-07)...")
    
    # Get submissions for same assignment
    cursor.execute('''
        SELECT id FROM submissions WHERE assignment_id = ? LIMIT 1
    ''', (assignment_ids[0],))
    row = cursor.fetchone()
    if row:
        cursor.execute('''
            INSERT INTO similarity_flags 
            (submission_id, similarity_score, is_reviewed, created_at)
            VALUES (?, ?, 0, datetime('now'))
        ''', (row[0], 0.95))
        print("    ✓ Created similarity flag (95% match)")


def print_summary(user_ids, course_id, assignment_ids):
    """Print summary of created data"""
    print("\n" + "=" * 70)
    print("✅ FULL DEMO DATA SEEDING COMPLETE!")
    print("=" * 70)
    print("\n📋 TEST CREDENTIALS:")
    print("-" * 55)
    print("| Role       | Email              | Password          |")
    print("-" * 55)
    print("| Instructor | alice@accl.edu     | testpassword123   |")
    print("| Student 1  | bob@accl.edu       | testpassword123   |")
    print("| Student 2  | charlie@accl.edu   | testpassword123   |")
    print("| Student 3  | diana@accl.edu     | testpassword123   |")
    print("| Admin      | admin@accl.edu     | adminpassword123  |")
    print("-" * 55)
    print("\n📚 DATA SUMMARY:")
    print(f"  • Course ID: {course_id}")
    print(f"  • Assignment IDs: {assignment_ids}")
    print("\n🚀 Start server: python run.py")
    print("🌐 Open: http://localhost:5000")
    print("=" * 70)


def main():
    print("=" * 70)
    print("ACCL Full Demo Seed Script")
    print("Creates test data for ALL 16 Functional Requirements")
    print("=" * 70)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        user_ids = seed_users(cursor)
        course_id = seed_courses(cursor, user_ids)
        assignment_ids = seed_assignments(cursor, course_id)
        seed_test_cases(cursor, assignment_ids)
        seed_enrollments(cursor, course_id, user_ids)
        seed_submissions(cursor, assignment_ids, user_ids)
        seed_notifications(cursor, user_ids)
        seed_audit_logs(cursor, user_ids)
        seed_drafts(cursor, user_ids, assignment_ids)
        seed_similarity_flags(cursor, user_ids, assignment_ids)
        
        conn.commit()
        print_summary(user_ids, course_id, assignment_ids)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    main()
