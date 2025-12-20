import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from web.utils import login_required, admin_required, get_service
from core.exceptions.validation_error import ValidationError

audit_bp = Blueprint('audit', __name__, url_prefix='/audit')


@audit_bp.route('/')
@login_required
@admin_required
def recent_audit():
    audit_service = get_service('audit_service')
    try:
        entries = audit_service.list_recent(limit=200)
        return render_template('audit/list.html', entries=entries)
    except (sqlite3.Error, Exception) as e:
        flash(str(e), 'error')
        return redirect(url_for('admin.dashboard'))


@audit_bp.route('/user/<int:user_id>')
@login_required
@admin_required
def audit_by_user(user_id):
    audit_service = get_service('audit_service')
    try:
        entries = audit_service.list_by_user(user_id)
        return render_template('audit/user.html', entries=entries, user_id=user_id)
    except (sqlite3.Error, Exception) as e:
        flash(str(e), 'error')
        return redirect(url_for('audit.recent_audit'))


@audit_bp.route('/<int:audit_id>')
@login_required
@admin_required
def audit_detail(audit_id):
    audit_service = get_service('audit_service')
    try:
        entry = audit_service.get_by_id(audit_id)
        if not entry:
            flash('Audit entry not found', 'error')
            return redirect(url_for('audit.recent_audit'))
        return render_template('audit/detail.html', entry=entry)
    except (sqlite3.Error, Exception) as e:
        flash(str(e), 'error')
        return redirect(url_for('audit.recent_audit'))


@audit_bp.route('/<int:audit_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_audit(audit_id):
    audit_service = get_service('audit_service')
    try:
        success = audit_service.delete(audit_id)
        if success:
            flash('Audit entry deleted', 'success')
        else:
            flash('Failed to delete audit entry', 'error')
    except (sqlite3.Error, Exception) as e:
        flash(str(e), 'error')
    return redirect(request.referrer or url_for('audit.recent_audit'))
