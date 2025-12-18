from flask import (
    Blueprint,
    request,
    redirect,
    url_for,
    flash,
    render_template,
    send_file,
)
import os
import hashlib

from web.utils import login_required, get_service, get_current_user
from core.exceptions.auth_error import AuthError
from core.exceptions.validation_error import ValidationError

files_bp = Blueprint("files", __name__, url_prefix="/files")


@files_bp.route("/submission/<int:submission_id>")
@login_required
def list_files(submission_id):
    file_service = get_service("file_service")

    try:
        files = file_service.list_files(
            user=get_current_user(),
            submission_id=submission_id,
        )

        return render_template(
            "files/list.html",
            files=files,
            submission_id=submission_id,
        )

    except (AuthError, ValidationError) as e:
        flash(str(e), "error")
        return redirect(request.referrer or "/")


@files_bp.route("/submission/<int:submission_id>/upload", methods=["POST"])
@login_required
def upload_file(submission_id):
    uploaded_file = request.files.get("file")

    if not uploaded_file:
        flash("No file provided", "error")
        return redirect(request.referrer or "/")

    try:
        data = uploaded_file.read()
        size_bytes = len(data)
        checksum = hashlib.sha256(data).hexdigest() if size_bytes > 0 else None
        try:
            uploaded_file.stream.seek(0)
        except Exception:
            pass
    except Exception:
        flash("Failed to read uploaded file", "error")
        return redirect(request.referrer or "/")

    file_service = get_service("file_service")

    try:
        file_service.upload_file(
            user=get_current_user(),
            submission_id=submission_id,
            path=f"submissions/{submission_id}/{uploaded_file.filename}",
            file_name=uploaded_file.filename,
            content_type=uploaded_file.content_type,
            size_bytes=size_bytes,
            checksum=checksum,
            storage_url=None,
        )

        flash("File uploaded successfully", "success")

    except (AuthError, ValidationError) as e:
        flash(str(e), "error")

    return redirect(request.referrer or "/")


@files_bp.route("/<int:file_id>/download")
@login_required
def download_file(file_id):
    file_repo = get_service("file_repo")
    try:
        f = file_repo.get_by_id(file_id)
        if not f:
            flash("File not found", "error")
            return redirect(request.referrer or "/")

        if getattr(f, "storage_url", None):
            return redirect(f.storage_url)

        local_path = getattr(f, "path", None)
        if local_path and os.path.isabs(local_path) and os.path.exists(local_path):
            return send_file(local_path, mimetype=f.content_type, as_attachment=True, download_name=f.file_name)

        app_root = os.getcwd()
        candidate = os.path.join(app_root, local_path) if local_path else None
        if candidate and os.path.exists(candidate):
            return send_file(candidate, mimetype=f.content_type, as_attachment=True, download_name=f.file_name)

        flash("File is not available for download", "error")
        return redirect(request.referrer or "/")

    except Exception as e:
        flash(str(e), "error")
        return redirect(request.referrer or "/")


@files_bp.route("/<int:file_id>/delete", methods=["POST"])
@login_required
def delete_file(file_id):
    file_service = get_service("file_service")

    try:
        file_service.delete_file(user=get_current_user(), file_id=file_id)
        flash("File deleted successfully", "success")

    except (AuthError, ValidationError) as e:
        flash(str(e), "error")

    return redirect(request.referrer or "/")
