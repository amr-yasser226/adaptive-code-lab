from flask import Blueprint, request, redirect, url_for, flash, render_template

from web.utils import login_required, admin_required, get_service ,get_current_user
from core.exceptions.auth_error import AuthError
from core.exceptions.validation_error import ValidationError

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    return render_template("admin/dashboard.html")


@admin_bp.route("/users/<int:user_id>/manage", methods=["POST"])
@login_required
@admin_required
def manage_user_account(user_id):
    action = request.form.get("action")

    admin_service = get_service("admin_service")
    auth_service = get_service("auth_service")

    try:
        admin_service.manage_user_account(
            admin_user=get_current_user(),
            target_user_id=user_id,
            action=action
        )
        flash("User account updated successfully", "success")

    except (AuthError, ValidationError) as e:
        flash(str(e), "error")

    return redirect(url_for("admin.dashboard"))




@admin_bp.route("/reports/<string:report_type>")
@login_required
@admin_required
def generate_report(report_type):
    admin_service = get_service("admin_service")
    auth_service = get_service("auth_service")

    try:
        data = admin_service.generate_report(
            admin_user=get_current_user(),
            report_type=report_type
        )

        return render_template(
            "admin/report.html",
            report_type=report_type,
            data=data
        )

    except ValidationError as e:
        flash(str(e), "error")
        return redirect(url_for("admin.dashboard"))



@admin_bp.route("/settings", methods=["POST"])
@login_required
@admin_required
def configure_system_setting():
    key = request.form.get("key")
    value = request.form.get("value")

    admin_service = get_service("admin_service")
    auth_service = get_service("auth_service")

    try:
        admin_service.configure_system_setting(
            admin_user=get_current_user(),
            key=key,
            value=value
        )
        flash("System setting updated successfully", "success")

    except ValidationError as e:
        flash(str(e), "error")

    return redirect(url_for("admin.dashboard"))





@admin_bp.route("/db/export", methods=["POST"])
@login_required
@admin_required
def export_db_dump():
    output_path = request.form.get("output_path")

    admin_service = get_service("admin_service")


    try:
        admin_service.export_db_dump(
            admin_user=get_current_user(),
            output_path=output_path
        )
        flash("Database exported successfully", "success")

    except ValidationError as e:
        flash(str(e), "error")

    return redirect(url_for("admin.dashboard"))

