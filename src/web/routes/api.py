import sys
import io
import contextlib
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
    
    assignment_repo = get_service('assignment_repo')
    test_case_service = get_service('test_case_service')
    user_repo = get_service('user_repo')

    current_user = user_repo.get_by_id(user_id)
    assignment = assignment_repo.get_by_id(assignment_id)
    
    if not assignment:
        return jsonify({'success': False, 'error': 'Assignment not found'}), 404

    # Fetch test cases using service (handles visibility permissions)
    try:
        test_cases = test_case_service.list_test_cases(current_user, assignment_id)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

    test_results = []
    passed_count = 0

    if not test_cases:
        # Dry run if no test cases
        try:
            output_buffer = io.StringIO()
            with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(output_buffer):
                exec(code, {'__name__': '__main__'})
            test_results.append({
                'name': 'Syntax Check',
                'passed': True,
                'output': output_buffer.getvalue()
            })
        except Exception as e:
            test_results.append({
                'name': 'Syntax Check',
                'passed': False,
                'output': str(e)
            })
    else:
        for tc in test_cases:
            result = {
                'name': tc.name,
                'passed': False,
                'output': '',
                'expected': tc.expected_out,
                'actual': ''
            }
            
            try:
                # Capture stdout
                output_buffer = io.StringIO()
                # Prepare mock input if needed (stdin)
                input_data = tc.stdin or ''
                sys.stdin = io.StringIO(input_data)
                
                with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(output_buffer):
                    # Create a fresh local scope for each run to avoid state pollution
                    local_scope = {}
                    exec(code, {'__name__': '__main__'}, local_scope)
                
                actual_output = output_buffer.getvalue().strip()
                expected_output = (tc.expected_out or '').strip()
                
                result['actual'] = actual_output
                result['output'] = actual_output
                
                if actual_output == expected_output:
                    result['passed'] = True
                    passed_count += 1
                else:
                    result['passed'] = False
                    
            except Exception as e:
                result['passed'] = False
                result['actual'] = f"Error: {str(e)}"
                result['output'] = f"Error: {str(e)}"
            finally:
                # Reset stdin
                sys.stdin = sys.__stdin__
            
            test_results.append(result)

    score = 0
    if test_cases:
        score = (passed_count / len(test_cases)) * 100

    return jsonify({
        'success': True,
        'test_results': test_results,
        'score': round(score, 2)
    })

@api_bp.route('/api/assignment/<assignment_id>/test-cases')
@login_required
def get_test_cases(assignment_id):
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
                'description': tc.descripion,
                'stdin': tc.stdin,
                'expected_out': tc.expected_out,
                'points': tc.points
            })
            
        return jsonify({
            'success': True,
            'test_cases': cases_list
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
