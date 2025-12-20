import sqlite3
from flask import (
    Blueprint,
    request,
    redirect,
    url_for,
    flash,
    render_template
)

from web.utils import login_required, get_service, get_current_user
from core.exceptions.auth_error import AuthError
from core.exceptions.validation_error import ValidationError

peer_review_bp = Blueprint("peer_review", __name__, url_prefix="/peer-review")


@peer_review_bp.route("/create/<int:submission_id>", methods=["POST"])
@login_required
def create_review(submission_id):
    peer_review_service = get_service("peer_review_service")

    rubric_score = request.form.get("rubric_score")
    comments = request.form.get("comments")

    try:
        peer_review_service.create_review(
            reviewer_student=get_current_user(),
            submission_id=submission_id,
            rubric_score=rubric_score,
            comments=comments
        )
        flash("Peer review created successfully", "success")

    except (AuthError, ValidationError, sqlite3.Error) as e:
        flash(str(e), "error")

    return redirect(request.referrer or url_for("index"))



@peer_review_bp.route("/update/<int:submission_id>", methods=["POST"])
@login_required
def update_review(submission_id):
    peer_review_service = get_service("peer_review_service")

    rubric_score = request.form.get("rubric_score")
    comments = request.form.get("comments")

    try:
        peer_review_service.update_review(
            reviewer_student=get_current_user(),
            submission_id=submission_id,
            rubric_score=rubric_score,
            comments=comments
        )
        flash("Peer review updated successfully", "success")

    except (AuthError, ValidationError, sqlite3.Error) as e:
        flash(str(e), "error")

    return redirect(request.referrer or url_for("index"))



@peer_review_bp.route("/submit/<int:submission_id>", methods=["POST"])
@login_required
def submit_review(submission_id):
    peer_review_service = get_service("peer_review_service")

    try:
        peer_review_service.submit_review(
            reviewer_student=get_current_user(),
            submission_id=submission_id
        )
        flash("Peer review submitted successfully", "success")

    except (AuthError, ValidationError, sqlite3.Error) as e:
        flash(str(e), "error")

    return redirect(request.referrer or url_for("index"))



@peer_review_bp.route("/submission/<int:submission_id>")
@login_required
def list_reviews_for_submission(submission_id):
    peer_review_service = get_service("peer_review_service")

    try:
        reviews = peer_review_service.list_reviews_for_submission(
            user=get_current_user(),
            submission_id=submission_id
        )

        return render_template(
            "peer_review/list.html",
            reviews=reviews,
            submission_id=submission_id
        )

    except (AuthError, ValidationError, sqlite3.Error) as e:
        flash(str(e), "error")
        return redirect(url_for("index"))
