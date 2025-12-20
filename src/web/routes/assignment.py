from flask import (
    Blueprint,
    request,
    redirect,
    url_for,
    flash,
    render_template
)

from web.utils import login_required, instructor_required, get_service, get_current_user
from core.exceptions.auth_error import AuthError
from core.exceptions.validation_error import ValidationError

assignment_bp = Blueprint("assignment", __name__, url_prefix="/assignments")


@assignment_bp.route("/create", methods=["GET", "POST"])
@login_required
@instructor_required
def create_assignment():
    assignment_service = get_service("assignment_service")

    if request.method == "POST":
        try:
            assignment_service.create_assignment(
                instructor=get_current_user(),
                course_id=request.form.get("course_id", type=int),
                title=request.form.get("title"),
                description=request.form.get("description"),
                release_date=request.form.get("release_date"),
                due_date=request.form.get("due_date"),
                max_points=request.form.get("max_points", type=int),
                allow_late_submissions=bool(request.form.get("allow_late")),
                late_submission_penalty=request.form.get("late_penalty"),
                is_published=bool(request.form.get("is_published"))
            )
            flash("Assignment created successfully", "success")
            return redirect(url_for("instructor.dashboard"))

        except (AuthError, ValidationError) as e:
            flash(str(e), "error")

    return render_template("assignment/create.html")

@assignment_bp.route("/<int:assignment_id>/publish", methods=["POST"])
@login_required
@instructor_required
def publish_assignment(assignment_id):
    assignment_service = get_service("assignment_service")

    try:
        assignment_service.publish_assignment(
            instructor=get_current_user(),
            assignment_id=assignment_id
        )
        flash("Assignment published", "success")

    except (AuthError, ValidationError) as e:
        flash(str(e), "error")

    return redirect(request.referrer or url_for("instructor.dashboard"))


@assignment_bp.route("/<int:assignment_id>/unpublish", methods=["POST"])
@login_required
@instructor_required
def unpublish_assignment(assignment_id):
    assignment_service = get_service("assignment_service")

    try:
        assignment_service.unpublish_assignment(
            instructor=get_current_user(),
            assignment_id=assignment_id
        )
        flash("Assignment unpublished", "success")

    except (AuthError, ValidationError) as e:
        flash(str(e), "error")

    return redirect(request.referrer or url_for("instructor.dashboard"))


@assignment_bp.route("/<int:assignment_id>/extend", methods=["POST"])
@login_required
@instructor_required
def extend_deadline(assignment_id):
    assignment_service = get_service("assignment_service")
    new_due_date = request.form.get("new_due_date")

    try:
        assignment_service.extend_deadline(
            instructor=get_current_user(),
            assignment_id=assignment_id,
            new_due_date=new_due_date
        )
        flash("Deadline extended", "success")

    except (AuthError, ValidationError) as e:
        flash(str(e), "error")

    return redirect(request.referrer or url_for("instructor.dashboard"))

@assignment_bp.route("/course/<int:course_id>")
@login_required
def list_assignments(course_id):
    assignment_service = get_service("assignment_service")

    try:
        assignments = assignment_service.list_assignments_for_course(
            user=get_current_user(),
            course_id=course_id
        )
        return render_template(
            "assignment/list.html",
            assignments=assignments,
            course_id=course_id
        )

    except ValidationError as e:
        flash(str(e), "error")
        return redirect(url_for("index"))


@assignment_bp.route("/<int:assignment_id>/submissions")
@login_required
@instructor_required
def view_submissions(assignment_id):
    assignment_service = get_service("assignment_service")

    try:
        submissions = assignment_service.get_submissions(
            instructor=get_current_user(),
            assignment_id=assignment_id
        )
        return render_template(
            "assignment/submissions.html",
            submissions=submissions,
            assignment_id=assignment_id
        )

    except (AuthError, ValidationError) as e:
        flash(str(e), "error")
        return redirect(url_for("instructor.dashboard"))

@assignment_bp.route("/<int:assignment_id>/stats")
@login_required
@instructor_required
def assignment_statistics(assignment_id):
    assignment_service = get_service("assignment_service")

    try:
        stats = assignment_service.calculate_statistics(
            instructor=get_current_user(),
            assignment_id=assignment_id
        )
        return render_template(
            "assignment/statistics.html",
            stats=stats,
            assignment_id=assignment_id
        )

    except (AuthError, ValidationError) as e:
        flash(str(e), "error")
        return redirect(url_for("instructor.dashboard"))
