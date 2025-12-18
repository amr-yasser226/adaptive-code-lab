from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from web.utils import login_required, instructor_required, admin_required, get_service, get_current_user
from core.exceptions.validation_error import ValidationError
from core.exceptions.auth_error import AuthError

enrollment_bp = Blueprint('enrollment', __name__, url_prefix='/enrollments')


@enrollment_bp.route('/my')
@login_required
def my_enrollments():
    user_id = session.get('user_id')
    enrollment_service = get_service('enrollment_service')
    try:
        enrollments = enrollment_service.list_by_student(user_id)
        return render_template('enrollments/my.html', enrollments=enrollments)
    except Exception as e:
        flash(str(e), 'error')
        return redirect(url_for('index'))


@enrollment_bp.route('/course/<int:course_id>')
@login_required
def course_enrollments(course_id):
    enrollment_service = get_service('enrollment_service')
    try:
        enrollments = enrollment_service.list_by_course(course_id)
        return render_template('enrollments/course.html', enrollments=enrollments, course_id=course_id)
    except Exception as e:
        flash(str(e), 'error')
        return redirect(url_for('index'))


@enrollment_bp.route('/course/<int:course_id>/enroll', methods=['POST'])
@login_required
def enroll_in_course(course_id):
    enrollment_service = get_service('enrollment_service')
    try:
        student = get_current_user()
        enrollment_service.enroll_student(student, course_id)
        flash('Enrolled successfully', 'success')
    except (ValidationError, AuthError) as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(str(e), 'error')
    return redirect(request.referrer or url_for('course.course_detail', course_id=course_id))


@enrollment_bp.route('/course/<int:course_id>/drop', methods=['POST'])
@login_required
def drop_course(course_id):
    enrollment_service = get_service('enrollment_service')
    try:
        student = get_current_user()
        enrollment_service.drop_course(student, course_id)
        flash('Dropped course', 'success')
    except (ValidationError, AuthError) as e:
        flash(str(e), 'error')
    return redirect(request.referrer or url_for('course.course_detail', course_id=course_id))


@enrollment_bp.route('/<int:student_id>/<int:course_id>/complete', methods=['POST'])
@login_required
@instructor_required
def complete_student_course(student_id, course_id):
    enrollment_repo = get_service('enrollment_repo')
    enrollment_service = get_service('enrollment_service')
    try:
        enrollment = enrollment_repo.get(student_id, course_id)
        if not enrollment:
            flash('Enrollment not found', 'error')
            return redirect(request.referrer or url_for('course.course_detail', course_id=course_id))

        final_grade = request.form.get('final_grade')
        try:
            final_grade = float(final_grade) if final_grade is not None else None
        except ValueError:
            flash('Invalid grade value', 'error')
            return redirect(request.referrer or url_for('course.course_detail', course_id=course_id))

        enrollment_service.complete_course(enrollment, final_grade)
        flash('Marked as completed', 'success')
    except (ValidationError, AuthError) as e:
        flash(str(e), 'error')
    return redirect(request.referrer or url_for('course.course_detail', course_id=course_id))


@enrollment_bp.route('/<int:student_id>/<int:course_id>/manage', methods=['POST'])
@login_required
@admin_required
def manage_enrollment(student_id, course_id):
    action = request.form.get('action')
    enrollment_repo = get_service('enrollment_repo')
    try:
        enrollment = enrollment_repo.get(student_id, course_id)
        if not enrollment:
            flash('Enrollment not found', 'error')
            return redirect(request.referrer or url_for('course.list_courses'))

        if action == 'drop':
            enrollment.status = 'dropped'
            enrollment.dropped_at = None
            enrollment_repo.update(enrollment)
            flash('Enrollment dropped', 'success')
        elif action == 'complete':
            final_grade = request.form.get('final_grade')
            try:
                enrollment.final_grade = float(final_grade) if final_grade is not None else None
            except ValueError:
                flash('Invalid grade', 'error')
                return redirect(request.referrer or url_for('course.list_courses'))
            enrollment.status = 'completed'
            enrollment_repo.update(enrollment)
            flash('Enrollment updated', 'success')
        else:
            flash('Unknown action', 'error')

    except Exception as e:
        flash(str(e), 'error')

    return redirect(request.referrer or url_for('course.list_courses'))
