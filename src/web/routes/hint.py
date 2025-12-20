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

hint_bp = Blueprint("hint", __name__, url_prefix="/hints")




@hint_bp.route("/generate/<int:submission_id>", methods=["POST"])
@login_required
def generate_hint(submission_id):
    hint_service = get_service("hint_service")

    try:
        hint_service.generate_hint(submission_id=submission_id)
        flash("Hint generated successfully", "success")

    except (sqlite3.Error, Exception) as e:
        # Service raises generic Exception
        flash(str(e), "error")

    return redirect(request.referrer or url_for("index"))






@hint_bp.route("/submission/<int:submission_id>")
@login_required
def list_hints(submission_id):
    hint_service = get_service("hint_service")

    try:
        hints = hint_service.list_hints_for_submission(
            submission_id=submission_id
        )

        return render_template(
            "hint/list.html",
            hints=hints,
            submission_id=submission_id
        )

    except (sqlite3.Error, Exception) as e:
        flash(str(e), "error")
        return redirect(url_for("index"))





@hint_bp.route("/<int:hint_id>/helpful", methods=["POST"])
@login_required
def mark_hint_helpful(hint_id):
    hint_service = get_service("hint_service")

    try:
        hint_service.mark_hint_helpful(hint_id)
        flash("Thanks for your feedback!", "success")

    except (sqlite3.Error, Exception) as e:
        flash(str(e), "error")

    return redirect(request.referrer or url_for("index"))







@hint_bp.route("/<int:hint_id>/not-helpful", methods=["POST"])
@login_required
def mark_hint_not_helpful(hint_id):
    hint_service = get_service("hint_service")

    try:
        hint_service.mark_hint_not_helpful(hint_id)
        flash("Feedback recorded", "success")

    except (sqlite3.Error, Exception) as e:
        flash(str(e), "error")

    return redirect(request.referrer or url_for("index"))
