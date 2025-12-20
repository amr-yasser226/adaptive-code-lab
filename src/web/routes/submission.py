import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, flash
from web.utils import login_required, instructor_required, get_service
from core.exceptions.validation_error import ValidationError

submission_bp = Blueprint('submission', __name__, url_prefix='/submissions')


@submission_bp.route('/<int:submission_id>')
@login_required
def view_submission(submission_id):
    submission_repo = get_service('submission_repo')
    result_repo = get_service('result_repo')
    assignment_repo = get_service('assignment_repo')

    submission = submission_repo.get_by_id(submission_id)
    if not submission:
        flash('Submission not found', 'error')
        return redirect(url_for('instructor.dashboard'))

    assignment = assignment_repo.get_by_id(submission.get_assignment_id())
    test_results = result_repo.find_by_submission(submission_id) if result_repo else []

    return render_template('submission/view.html', submission=submission, assignment=assignment, test_results=test_results)


@submission_bp.route('/<int:submission_id>/regrade', methods=['POST'])
@login_required
@instructor_required
def regrade_submission(submission_id):
    sandbox_service = get_service('sandbox_service')
    submission_repo = get_service('submission_repo')
    try:
        submission = submission_repo.get_by_id(submission_id)
        if not submission:
            flash('Submission not found', 'error')
            return redirect(request.referrer or url_for('instructor.dashboard'))

        # Re-run tests (service handles enqueuing or immediate run)
        sandbox_service.regrade_submission(submission)
        flash('Regrade requested', 'success')
    except (sqlite3.Error, Exception) as e:
        flash(str(e), 'error')

    return redirect(request.referrer or url_for('instructor.dashboard'))
