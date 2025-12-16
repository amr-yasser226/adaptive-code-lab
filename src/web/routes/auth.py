from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from core.exceptions.auth_error import AuthError
from web.utils import get_service

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        auth_service = get_service('auth_service')
        try:
            user = auth_service.login(email, password)
            session['user_id'] = user.get_id()
            session['user_role'] = user.role
            session.permanent = remember
            flash(f'Welcome, {user.name}!', 'success')
            
            if user.role == 'student':
                return redirect(url_for('student.dashboard'))
            elif user.role == 'instructor':
                return redirect(url_for('instructor.dashboard'))
            else:
                return redirect(url_for('index'))
                
        except AuthError as e:
            flash(str(e), 'error')
            
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'student')
        
        auth_service = get_service('auth_service')
        try:
            auth_service.register(name, email, password, role)
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except AuthError as e:
            flash(str(e), 'error')
            
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))
