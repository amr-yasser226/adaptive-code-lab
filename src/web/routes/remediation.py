import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from web.utils import login_required, student_required, get_service


remediation_bp = Blueprint('remediation', __name__)


@remediation_bp.route('/remediations')
@login_required
@student_required
def list_remediations():
    user_id = session.get('user_id')
    
    remediation_service = get_service('remediation_service')
    
    only_pending = request.args.get('pending', 'false').lower() == 'true'
    try:
        remediations = remediation_service.get_student_remediations(user_id, only_pending)
        
        return render_template(
            'student/remediations.html',
            remediations=remediations,
            only_pending=only_pending
        )
    except (sqlite3.Error, Exception) as e:
        flash(str(e), 'error')
        return redirect(url_for('index'))


@remediation_bp.route('/remediations/<int:remediation_id>')
@login_required
@student_required
def view_remediation(remediation_id):
    user_id = session.get('user_id')
    
    remediation_service = get_service('remediation_service')
    
    # Mark as viewed
    try:
        remediation_service.mark_viewed(user_id, remediation_id)
    except (sqlite3.Error, Exception) as e:
        flash(str(e), 'error')
        return redirect(url_for('remediation.list_remediations'))
    
    # Get remediation details
    remediations = remediation_service.get_student_remediations(user_id)
    current_rem = next((r for r in remediations if r['id'] == remediation_id), None)
    
    if not current_rem:
        flash('Remediation not found', 'error')
        return redirect(url_for('remediation.list_remediations'))
    
    return render_template(
        'student/remediation_detail.html',
        remediation=current_rem
    )


@remediation_bp.route('/remediations/<int:remediation_id>/complete', methods=['POST'])
@login_required
@student_required
def complete_remediation(remediation_id):
    user_id = session.get('user_id')
    
    remediation_service = get_service('remediation_service')
    
    try:
        remediation_service.mark_completed(user_id, remediation_id)
        flash('Remediation marked as completed!', 'success')
    except (sqlite3.Error, Exception) as e:
        flash(str(e), 'error')
    
    return redirect(url_for('remediation.list_remediations'))


# API endpoints for AJAX calls
@remediation_bp.route('/api/remediations')
@login_required
def api_list_remediations():
    user_id = session.get('user_id')
    
    remediation_service = get_service('remediation_service')
    
    only_pending = request.args.get('pending', 'false').lower() == 'true'
    try:
        remediations = remediation_service.get_student_remediations(user_id, only_pending)
        
        return jsonify({
            'success': True,
            'remediations': remediations,
            'count': len(remediations)
        })
    except (sqlite3.Error, Exception) as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@remediation_bp.route('/api/remediations/<int:remediation_id>/view', methods=['POST'])
@login_required
def api_mark_viewed(remediation_id):
    user_id = session.get('user_id')
    
    remediation_service = get_service('remediation_service')
    
    try:
        remediation_service.mark_viewed(user_id, remediation_id)
        return jsonify({'success': True})
    except (sqlite3.Error, Exception) as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@remediation_bp.route('/api/remediations/<int:remediation_id>/complete', methods=['POST'])
@login_required
def api_mark_completed(remediation_id):
    user_id = session.get('user_id')
    
    remediation_service = get_service('remediation_service')
    
    try:
        remediation_service.mark_completed(user_id, remediation_id)
        return jsonify({'success': True})
    except (sqlite3.Error, Exception) as e:
        return jsonify({'success': False, 'error': str(e)}), 400
