import sqlite3
from flask import Blueprint, request, redirect, url_for, flash, render_template
from web.utils import login_required, instructor_required, get_service, get_current_user
from core.exceptions.validation_error import ValidationError
from core.exceptions.auth_error import AuthError

test_case_bp = Blueprint('test_case', __name__, url_prefix='/test-cases')


@test_case_bp.route('/create/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
@instructor_required
def create_test_case(assignment_id):
    test_case_service = get_service('test_case_service')

    if request.method == 'POST':
        try:
            test_case_service.create_test_case(
                instructor=get_current_user(),
                assignment_id=assignment_id,
                name=request.form.get('name'),
                stdin=request.form.get('stdin'),
                expected_out=request.form.get('expected_out'),
                points=request.form.get('points', type=int, default=0),
                is_visible=bool(request.form.get('is_visible'))
            )
            flash('Test case created', 'success')
            return redirect(request.referrer or url_for('assignment.view_submissions', assignment_id=assignment_id))
        except (ValidationError, AuthError, sqlite3.Error) as e:
            flash(str(e), 'error')

    return render_template('test_case/create.html', assignment_id=assignment_id)


@test_case_bp.route('/<int:testcase_id>/edit', methods=['GET', 'POST'])
@login_required
@instructor_required
def edit_test_case(testcase_id):
    test_case_service = get_service('test_case_service')

    if request.method == 'POST':
        try:
            test_case_service.update_test_case(
                instructor=get_current_user(),
                testcase_id=testcase_id,
                name=request.form.get('name'),
                stdin=request.form.get('stdin'),
                expected_out=request.form.get('expected_out'),
                points=request.form.get('points', type=int, default=0),
                is_visible=bool(request.form.get('is_visible'))
            )
            flash('Test case updated', 'success')
            return redirect(request.referrer or url_for('instructor.dashboard'))
        except (ValidationError, AuthError, sqlite3.Error) as e:
            flash(str(e), 'error')

    # GET: load testcase
    try:
        testcase = get_service('test_case_repo').get_by_id(testcase_id)
        if not testcase:
            flash('Test case not found', 'error')
            return redirect(request.referrer or url_for('instructor.dashboard'))
    except sqlite3.Error as e:
        flash(str(e), 'error')
        return redirect(request.referrer or url_for('instructor.dashboard'))

    return render_template('test_case/edit.html', testcase=testcase)


@test_case_bp.route('/<int:testcase_id>/delete', methods=['POST'])
@login_required
@instructor_required
def delete_test_case(testcase_id):
    try:
        get_service('test_case_service').delete_test_case(get_current_user(), testcase_id)
        flash('Test case deleted', 'success')
    except (sqlite3.Error, Exception) as e:
        flash(str(e), 'error')

    return redirect(request.referrer or url_for('instructor.dashboard'))
