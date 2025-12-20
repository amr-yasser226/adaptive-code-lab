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

notification_bp = Blueprint("notification", __name__, url_prefix="/notifications")

@notification_bp.route("/", methods=["GET"])
@login_required
def list_notifications():
    notification_service = get_service("notification_service")
    only_unread = request.args.get("unread") == "1"

    try:
        notifications = notification_service.get_user_notifications(
            user=get_current_user(),
            only_unread=only_unread
        )

        return render_template(
            "notification/list.html",
            notifications=notifications,
            only_unread=only_unread
        )

    except (AuthError, ValidationError, sqlite3.Error) as e:
        flash(str(e), "error")
        return redirect(url_for("index"))




@notification_bp.route("/<int:notification_id>/read", methods=["POST"])
@login_required
def mark_as_read(notification_id):
    notification_service = get_service("notification_service")

    try:
        notification_service.mark_as_read(
            user=get_current_user(),
            notification_id=notification_id
        )
        flash("Notification marked as read", "success")

    except (AuthError, ValidationError, sqlite3.Error) as e:
        flash(str(e), "error")

    return redirect(request.referrer or url_for("notification.list_notifications"))





@notification_bp.route("/<int:notification_id>/unread", methods=["POST"])
@login_required
def mark_as_unread(notification_id):
    notification_service = get_service("notification_service")

    try:
        notification_service.mark_as_unread(
            user=get_current_user(),
            notification_id=notification_id
        )
        flash("Notification marked as unread", "success")

    except (AuthError, ValidationError, sqlite3.Error) as e:
        flash(str(e), "error")

    return redirect(request.referrer or url_for("notification.list_notifications"))





@notification_bp.route("/<int:notification_id>/delete", methods=["POST"])
@login_required
def delete_notification(notification_id):
    notification_service = get_service("notification_service")

    try:
        notification_service.delete(
            user=get_current_user(),
            notification_id=notification_id
        )
        flash("Notification deleted", "success")

    except (AuthError, ValidationError, sqlite3.Error) as e:
        flash(str(e), "error")

    return redirect(request.referrer or url_for("notification.list_notifications"))
