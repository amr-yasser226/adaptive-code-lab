import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from web.utils import login_required, instructor_required, get_service, get_current_user
from core.exceptions.validation_error import ValidationError
from core.exceptions.auth_error import AuthError
from core.entities.course import Course
from core.entities.enrollment import Enrollment
from datetime import datetime

course_bp = Blueprint('course', __name__, url_prefix='/courses')


@course_bp.route('/')
@login_required
def list_courses():
    user_id = session.get('user_id')
    role = session.get('user_role')
    course_repo = get_service('course_repo')
    enrollment_repo = get_service('enrollment_repo')

    courses = []
    try:
        if role == 'instructor':
            instructor_service = get_service('instructor_service')
            courses = instructor_service.list_instructor_courses(user_id)
        elif role == 'student':
            # Show all courses that are available for enrollment (published or active)
            courses = course_repo.list_all()
            courses = [c for c in courses if c.status in ['published', 'active']]
            # Also fetch enrollment status for each course to show "Enrolled" badge
            enrollments = enrollment_repo.list_by_student(user_id)
            enrolled_course_ids = {e.get_course_id() for e in enrollments if e.status == 'enrolled'}
            return render_template('courses/list.html', courses=courses, enrolled_course_ids=enrolled_course_ids)

        return render_template('courses/list.html', courses=courses)

    except (sqlite3.Error, Exception) as e:
        flash(str(e), 'error')
        return redirect(url_for('index'))


@course_bp.route('/<int:course_id>')
@login_required
def course_detail(course_id):
    course_repo = get_service('course_repo')
    assignment_repo = get_service('assignment_repo')
    enrollment_repo = get_service('enrollment_repo')
    user_id = session.get('user_id')

    try:
        course = course_repo.get_by_id(course_id)
        if not course:
            flash('Course not found', 'error')
            return redirect(url_for('course.list_courses'))

        assignments = assignment_repo.list_by_course(course_id)
        enrollment = enrollment_repo.get(user_id, course_id)
        is_enrolled = enrollment is not None and enrollment.status == 'enrolled'

        return render_template('courses/detail.html', course=course, assignments=assignments, is_enrolled=is_enrolled)

    except (sqlite3.Error, Exception) as e:
        flash(str(e), 'error')
        return redirect(url_for('course.list_courses'))


@course_bp.route('/create', methods=['GET', 'POST'])
@login_required
@instructor_required
def create_course():
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        year = request.form.get('year')
        semester = request.form.get('semester')
        max_students = int(request.form.get('max_students') or 0)
        credits = int(request.form.get('credits') or 0)

        current_user = get_current_user()
        if not current_user:
            flash('User session invalid', 'error')
            return redirect(url_for('auth.login'))

        instructor_service = get_service('instructor_service')
        try:
            new_course = instructor_service.create_course(
                instructor_id=current_user.get_id(),
                code=code,
                title=title,
                description=description,
                year=year,
                semester=semester,
                max_students=max_students,
                credits=credits
            )
            flash('Course created successfully', 'success')
            return redirect(url_for('course.course_detail', course_id=new_course.get_id()))
        except (ValidationError, AuthError, sqlite3.Error) as e:
            flash(str(e), 'error')

    return render_template('courses/create.html')


@course_bp.route('/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
@instructor_required
def edit_course(course_id):
    course_repo = get_service('course_repo')
    try:
        course = course_repo.get_by_id(course_id)
        if not course:
            flash('Course not found', 'error')
            return redirect(url_for('course.list_courses'))

        current_user = get_current_user()
        if not current_user:
            flash('User session invalid', 'error')
            return redirect(url_for('auth.login'))

        if course.get_instructor_id() != current_user.get_id():
            raise AuthError('You are not the owner of this course')

        if request.method == 'POST':
            code = request.form.get('code', course.code).strip()
            title = request.form.get('title', course.title).strip()
            description = request.form.get('description', course.description).strip()
            year = request.form.get('year', course.year)
            semester = request.form.get('semester', course.semester)
            max_students = int(request.form.get('max_students') or course.max_students)
            credits = int(request.form.get('credits') or course.credits)

            updated_course = Course(
                id=course.get_id(),
                instructor_id=course.get_instructor_id(),
                code=code,
                title=title,
                description=description,
                year=year,
                semester=semester,
                max_students=max_students,
                created_at=course.created_at,
                status=course.status,
                updated_at=datetime.now(),
                credits=credits
            )

            saved = course_repo.update(updated_course)
            if not saved:
                flash('Failed to update course', 'error')
            else:
                flash('Course updated', 'success')
                return redirect(url_for('course.course_detail', course_id=course_id))

        return render_template('courses/edit.html', course=course)

    except (ValidationError, AuthError, sqlite3.Error) as e:
        flash(str(e), 'error')
        return redirect(url_for('course.list_courses'))


@course_bp.route('/<int:course_id>/publish', methods=['POST'])
@login_required
@instructor_required
def publish_course(course_id):
    course_repo = get_service('course_repo')
    try:
        course = course_repo.get_by_id(course_id)
        if not course:
            flash('Course not found', 'error')
            return redirect(url_for('course.list_courses'))

        current_user = get_current_user()
        if not current_user or course.get_instructor_id() != current_user.get_id():
            raise AuthError('Not authorized')

        course_repo.publish(course_id)
        flash('Course published', 'success')
        return redirect(url_for('course.course_detail', course_id=course_id))

    except (ValidationError, AuthError, sqlite3.Error) as e:
        flash(str(e), 'error')
        return redirect(url_for('course.list_courses'))


@course_bp.route('/<int:course_id>/archive', methods=['POST'])
@login_required
@instructor_required
def archive_course(course_id):
    course_repo = get_service('course_repo')
    try:
        course = course_repo.get_by_id(course_id)
        if not course:
            flash('Course not found', 'error')
            return redirect(url_for('course.list_courses'))

        current_user = get_current_user()
        if not current_user or course.get_instructor_id() != current_user.get_id():
            raise AuthError('Not authorized')

        course_repo.archive(course_id)
        flash('Course archived', 'success')
        return redirect(url_for('course.list_courses'))
    except (ValidationError, AuthError, sqlite3.Error) as e:
        flash(str(e), 'error')
        return redirect(url_for('course.list_courses'))


@course_bp.route('/<int:course_id>/enroll', methods=['POST'])
@login_required
def enroll(course_id):
    enrollment_repo = get_service('enrollment_repo')
    course_repo = get_service('course_repo')
    user_id = session.get('user_id')

    try:
        course = course_repo.get_by_id(course_id)
        if not course:
            flash('Course not found', 'error')
            return redirect(url_for('course.list_courses'))

        new_enrollment = Enrollment(
            student_id=user_id,
            course_id=course_id,
            status='enrolled',
            enrolled_at=datetime.now(),
            dropped_at=None,
            final_grade=None
        )

        result = enrollment_repo.enroll(new_enrollment)
        if result:
            flash('Enrolled successfully', 'success')
        else:
            flash('Enrollment failed. You might already be enrolled or there was a database error.', 'error')
        
        return redirect(url_for('course.course_detail', course_id=course_id))

    except (ValidationError, AuthError, sqlite3.Error, Exception) as e:
        flash(str(e), 'error')
        return redirect(url_for('course.course_detail', course_id=course_id))
