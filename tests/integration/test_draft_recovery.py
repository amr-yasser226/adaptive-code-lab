import pytest
from web.app import create_app
from core.entities.user import User
from core.entities.course import Course
from core.entities.assignment import Assignment
from datetime import datetime


def test_draft_save_and_recover(setup_test_database):
    # create app after test DB env is set
    app = create_app({'TESTING': True, 'WTF_CSRF_ENABLED': False})
    client = app.test_client()

    with app.app_context():
        user_repo = app.extensions['services']['user_repo']
        course_repo = app.extensions['services']['course_repo']
        assignment_repo = app.extensions['services']['assignment_repo']

        # Create student user
        student = User(id=None, name='Student One', email='s1@test.edu', password=User.hash_password('pass'), role='student')
        saved_student = user_repo.create(student)

        # Create instructor user
        instructor = User(id=None, name='Instructor', email='i1@test.edu', password=User.hash_password('pass'), role='instructor')
        saved_instr = user_repo.create(instructor)

        # Insert instructor profile row
        user_repo.db.execute("INSERT OR IGNORE INTO instructors (id, instructor_code, bio, office_hours) VALUES (:id, :code, :bio, :hours)", {
            'id': saved_instr.get_id(), 'code': 'I001', 'bio': 'Bio', 'hours': 'MWF'
        })
        user_repo.db.commit()

        # Create course
        course = Course(id=None, instructor_id=saved_instr.get_id(), code='T100', title='Test Course', description='Desc', year=2025, semester='Fall', max_students=30, created_at=datetime.now(), status='active', updated_at=datetime.now(), credits=3)
        saved_course = course_repo.create(course)

        # Create assignment
        assignment = Assignment(id=None, course_id=saved_course.get_id(), title='Draft Test', description='Desc', release_date=datetime.now(), due_date=datetime.now(), max_points=100, is_published=1, allow_late_submissions=0, late_submission_penalty=0.0, created_at=datetime.now(), updated_at=datetime.now())
        saved_assignment = assignment_repo.create(assignment)

    # simulate login as student
    with client.session_transaction() as sess:
        sess['user_id'] = saved_student.get_id()
        sess['user_role'] = 'student'

    # Save draft
    resp = client.post('/api/drafts', json={'assignment_id': saved_assignment.get_id(), 'content': 'print(1)'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['draft']['content'] == 'print(1)'

    # Simulate page refresh: GET latest draft
    resp2 = client.get(f"/api/drafts?assignment_id={saved_assignment.get_id()}")
    assert resp2.status_code == 200
    data2 = resp2.get_json()
    assert data2['success'] is True
    assert data2['draft']['content'] == 'print(1)'
