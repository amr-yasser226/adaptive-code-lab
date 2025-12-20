import sqlite3
import os
from flask import Blueprint, request, redirect, url_for, flash, render_template, send_file
from web.utils import login_required, admin_required, get_service, get_current_user
from core.exceptions.auth_error import AuthError
from core.exceptions.validation_error import ValidationError
from web.routes.instructor import analytics
from web.routes.profile_shared import profile_view, profile_update_logic

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    return render_template("admin/dashboard.html")

@admin_bp.route("/analytics")
@login_required
@admin_required
def admin_analytics():
    return analytics()

@admin_bp.route("/users/manage", methods=["POST"])
@login_required
@admin_required
def manage_user_account():
    user_id = request.form.get("user_id")
    action = request.form.get("action")

    if not user_id or not action:
        flash("User ID and action are required", "error")
        return redirect(url_for("admin.dashboard"))

    admin_service = get_service("admin_service")

    try:
        admin_service.manage_user_account(
            admin_user=get_current_user(),
            target_user_id=int(user_id),
            action=action
        )
        flash("User account updated successfully", "success")

    except (AuthError, ValidationError, sqlite3.Error) as e:
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

    except (ValidationError, sqlite3.Error) as e:
        flash(str(e), "error")
        return redirect(url_for("admin.dashboard"))



@admin_bp.route("/settings", methods=["POST"])
@login_required
@admin_required
def configure_system_setting():
    key = request.form.get("key")
    value = request.form.get("value")

    admin_service = get_service("admin_service")

    try:
        admin_service.configure_system_setting(
            admin_user=get_current_user(),
            key=key,
            value=value
        )
        flash("System setting updated successfully", "success")

    except (ValidationError, sqlite3.Error) as e:
        flash(str(e), "error")

@admin_bp.route('/profile')
@login_required
@admin_required
def profile():
    return profile_view()

@admin_bp.route('/profile/update', methods=['POST'])
@login_required
@admin_required
def update_profile():
    return profile_update_logic('admin')





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
        return redirect(url_for("admin.dashboard", download_path=output_path))

    except (ValidationError, sqlite3.Error) as e:
        flash(str(e), "error")

    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/db/download")
@login_required
@admin_required
def download_db():
    output_path = request.args.get("path")
    if not output_path:
        flash("No file path provided", "error")
        return redirect(url_for("admin.dashboard"))
    
    # Security: Ensure we are only sending files from the root or backups
    filename = os.path.basename(output_path)
    if not (filename.endswith('.db') or filename.endswith('.sqlite')):
         flash("Invalid file type", "error")
         return redirect(url_for("admin.dashboard"))

    try:
        abs_path = os.path.abspath(output_path)
        if not os.path.exists(abs_path):
             flash("File not found on server", "error")
             return redirect(url_for("admin.dashboard"))
             
        return send_file(abs_path, as_attachment=True)
    except Exception as e:
        flash(f"Download failed: {str(e)}", "error")
        return redirect(url_for("admin.dashboard"))
