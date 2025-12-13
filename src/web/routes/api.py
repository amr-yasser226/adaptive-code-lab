from flask import Blueprint, jsonify, request
from web.utils import login_required, get_service

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/test-code', methods=['POST'])
@login_required
def test_code():
    data = request.get_json()
    code = data.get('code', '')
    language = data.get('language', 'python')
    assignment_id = data.get('assignment_id')
    
    assignment_repo = get_service('assignment_repo')
    assignment = assignment_repo.get_by_id(assignment_id)
    
    if not assignment:
        return jsonify({'success': False, 'error': 'Assignment not found'}), 404

    test_results = [] # TODO: specific execution logic
    
    return jsonify({
        'success': True,
        'test_results': test_results,
        'score': 0
    })

@api_bp.route('/api/assignment/<assignment_id>/test-cases')
@login_required
def get_test_cases(assignment_id):
    assignment_repo = get_service('assignment_repo')
    assignment = assignment_repo.get_by_id(assignment_id)
    
    if not assignment:
        return jsonify({'success': False, 'error': 'Assignment not found'}), 404
        
    return jsonify({
        'success': True,
        'test_cases': assignment.test_cases if hasattr(assignment, 'test_cases') else []
    })
