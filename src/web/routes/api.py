import sqlite3
import os
from flask import Blueprint, jsonify, request, session
from web.utils import login_required, get_service

api_bp = Blueprint('api', __name__)


@api_bp.route('/api/test-code', methods=['POST'])
@login_required
def test_code():
    data = request.get_json()
    code = data.get('code', '')
    language = data.get('language', 'python')
    assignment_id = data.get('assignment_id')
    user_id = session.get('user_id')
    
    sandbox_service = get_service('sandbox_service')
    assignment_repo = get_service('assignment_repo')
    test_case_service = get_service('test_case_service')
    user_repo = get_service('user_repo')

    current_user = user_repo.get_by_id(user_id)
    assignment = assignment_repo.get_by_id(assignment_id)
    
    if not assignment:
        return jsonify({'success': False, 'error': 'Assignment not found'}), 404

    try:
        test_cases = test_case_service.list_test_cases(current_user, assignment_id)
    except (sqlite3.Error, Exception) as e:
        return jsonify({'success': False, 'error': str(e)}), 400

    test_results = []
    passed_count = 0
    ai_feedback = None

    if not test_cases:
        # Dry run - just check if code runs without error
        result = sandbox_service.execute_code(code, language)
        
        test_results.append({
            'name': 'Syntax Check',
            'passed': result['success'],
            'output': result['stdout'] if result['success'] else result['stderr'],
            'runtime_ms': result['runtime_ms']
        })
        
        if result['success']:
            passed_count = 1
        elif sandbox_service.groq_client:
            # Get AI feedback on error
            ai_feedback = sandbox_service.get_ai_feedback(code, result['stderr'])
    else:
        # Run all test cases using sandbox
        results = sandbox_service.run_all_tests(code, test_cases, language)
        
        for tc_result in results['results']:
            test_results.append({
                'name': tc_result['test_name'],
                'passed': tc_result['passed'],
                'output': tc_result['stdout'],
                'expected': tc_result['expected_output'],
                'actual': tc_result['actual_output'],
                'runtime_ms': tc_result['runtime_ms'],
                'timed_out': tc_result['timed_out']
            })
            
            if tc_result['passed']:
                passed_count += 1
        
        # Get AI feedback if there were failures
        if passed_count < len(test_cases) and sandbox_service.groq_client:
            failed_result = next((r for r in results['results'] if not r['passed']), None)
            if failed_result and failed_result.get('stderr'):
                ai_feedback = sandbox_service.get_ai_feedback(code, failed_result['stderr'])

    score = 0
    if test_cases:
        score = (passed_count / len(test_cases)) * 100
    elif passed_count > 0:
        score = 100

    response = {
        'success': True,
        'test_results': test_results,
        'score': round(score, 2),
        'passed_count': passed_count,
        'total_count': len(test_cases) if test_cases else 1
    }
    
    if ai_feedback:
        response['ai_feedback'] = ai_feedback
    
    return jsonify(response)


@api_bp.route('/api/assignment/<assignment_id>/test-cases')
@login_required
def get_test_cases(assignment_id):
    """Get test cases for an assignment."""
    user_id = session.get('user_id')
    user_repo = get_service('user_repo')
    test_case_service = get_service('test_case_service')
    
    current_user = user_repo.get_by_id(user_id)
    
    try:
        test_cases = test_case_service.list_test_cases(current_user, assignment_id)
        # Convert objects to dicts for JSON
        cases_list = []
        for tc in test_cases:
            cases_list.append({
                'name': tc.name,
                'description': tc.description,
                'stdin': tc.stdin,
                'expected_out': tc.expected_out,
                'points': tc.points
            })
            
        return jsonify({
            'success': True,
            'test_cases': cases_list
        })
    except (sqlite3.Error, Exception) as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@api_bp.route('/api/hint', methods=['POST'])
@login_required
def get_hint():
    """
    Get AI-powered hint for code.
    FR-06: Uses Groq client for hint generation.
    """
    data = request.get_json()
    code = data.get('code', '')
    error_message = data.get('error', '')
    
    sandbox_service = get_service('sandbox_service')
    
    if not sandbox_service.groq_client:
        return jsonify({
            'success': False,
            'error': 'AI hints not available (Groq API not configured)'
        }), 503
    
    try:
        hint = sandbox_service.get_ai_feedback(code, error_message)
        return jsonify({
            'success': True,
            'hint': hint
        })
    except (sqlite3.Error, Exception) as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/api/languages')
def get_supported_languages():
    """Get list of supported programming languages."""
    return jsonify({
        'success': True,
        'languages': [
            {'id': 'python', 'name': 'Python 3.10', 'extension': '.py'},
            {'id': 'javascript', 'name': 'JavaScript (Node.js)', 'extension': '.js'},
            {'id': 'java', 'name': 'Java 15', 'extension': '.java'},
            {'id': 'cpp', 'name': 'C++ 10', 'extension': '.cpp'},
            {'id': 'c', 'name': 'C 10', 'extension': '.c'}
        ]
    })


@api_bp.route('/api/drafts', methods=['GET'])
@login_required
def get_draft():
    user_id = session.get('user_id')
    assignment_id = request.args.get('assignment_id')
    if not assignment_id:
        return jsonify({'success': False, 'error': 'assignment_id required'}), 400

    draft_service = get_service('draft_service')
    draft = draft_service.get_latest_draft(user_id, int(assignment_id))
    if not draft:
        return jsonify({'success': True, 'draft': None})

    return jsonify({'success': True, 'draft': draft.to_dict()})


@api_bp.route('/api/drafts', methods=['POST'])
@login_required
def save_draft():
    data = request.get_json() or {}
    assignment_id = data.get('assignment_id')
    content = data.get('content', '')
    language = data.get('language', 'python')

    if not assignment_id:
        return jsonify({'success': False, 'error': 'assignment_id required'}), 400

    user_id = session.get('user_id')
    draft_service = get_service('draft_service')

    try:
        draft = draft_service.save_draft(user_id, int(assignment_id), content, language)
        if not draft:
            return jsonify({'success': False, 'error': 'storage error'}), 500
        return jsonify({'success': True, 'draft': draft.to_dict()})
    except (sqlite3.Error, Exception) as e:
        return jsonify({'success': False, 'error': str(e)}), 500
