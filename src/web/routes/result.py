import sqlite3
from flask import Blueprint, jsonify
from web.utils import login_required, get_service

result_bp = Blueprint('result', __name__, url_prefix='/results')


@result_bp.route('/submission/<int:submission_id>')
@login_required
def results_for_submission(submission_id):
    try:
        result_repo = get_service('result_repo')
        results = result_repo.find_by_submission(submission_id) if result_repo else []

        # Convert to simple dicts for JSON
        out = []
        for r in results:
            out.append({
                'id': r.get_id(),
                'test_case_id': r.get_test_case_id(),
                'passed': r.passed if hasattr(r, 'passed') else getattr(r, 'get_passed', lambda: None)(),
                'stdout': getattr(r, 'stdout', '')
            })

        return jsonify({'success': True, 'results': out})
    except (sqlite3.Error, Exception) as e:
        return jsonify({'success': False, 'error': str(e)}), 500
