import sqlite3
from flask import render_template, request, redirect, url_for, flash, session
from web.utils import get_service
from core.exceptions.validation_error import ValidationError
from markupsafe import Markup

def profile_view():
    user_id = session['user_id']
    student_service = get_service('student_service')
    user_repo = get_service('user_repo')
    
    # Get the actual user entity from database
    user = user_repo.get_by_id(user_id)
    
    # Try to get submissions (mostly for students, but harmless if empty for instructors)
    try:
        submissions = student_service.get_student_submissions(user_id)
    except (sqlite3.Error, Exception):
        submissions = []
    
    # Calculate stats
    avg_score = 0
    if submissions:
        scores = [s.score for s in submissions if hasattr(s, 'score') and s.score is not None]
        avg_score = sum(scores) / len(scores) if scores else 0
    
    class StubField:
        def __init__(self, name, type="text"):
            self.name = name
            self.type = type
            self.errors = []
            
        def __call__(self, **kwargs):
            attrs = [f'type="{self.type}"', f'name="{self.name}"']
            for k, v in kwargs.items():
                if k == "class_": k = "class"
                attrs.append(f'{k}="{v}"')
            return Markup(f'<input {" ".join(attrs)}>')
    
    class StubForm:
        current_password = StubField("current_password", "password")
        new_password = StubField("new_password", "password")
        confirm_password = StubField("confirm_password", "password")
        csrf_token = Markup('<input type="hidden" name="csrf_token" value="">')
    
    stats = {
        'average_score': avg_score,
        'total_submissions': len(submissions) if submissions else 0,
        'total_assignments': 10
    }
    
    return render_template('profile.html',
        user=user,
        current_user=user,
        form=StubForm(),
        stats=stats)

def profile_update_logic(role_prefix):
    user_id = session['user_id']
    user_repo = get_service('user_repo')
    
    # Get form data
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    bio = request.form.get('bio', '').strip()
    new_password = request.form.get('new_password', '').strip()
    confirm_password = request.form.get('confirm_password', '').strip()
    
    try:
        # Get current user
        user = user_repo.get_by_id(user_id)
        if not user:
            flash('User not found', 'error')
            return redirect(url_for(f'{role_prefix}.profile'))
        
        # Update profile info if provided
        if name:
            user.name = name
        if email:
            user.email = email
        if bio is not None:
            user.bio = bio
        
        # Handle password change only if new password provided
        if new_password:
            if new_password != confirm_password:
                flash('New passwords do not match', 'error')
                return redirect(url_for(f'{role_prefix}.profile'))
            
            if len(new_password) < 8:
                flash('New password must be at least 8 characters', 'error')
                return redirect(url_for(f'{role_prefix}.profile'))
            
            user.set_password(new_password)
        
        # Save profile changes
        user_repo.update(user)
        flash('Profile updated successfully!', 'success')
            
    except (sqlite3.Error, ValidationError) as e:
        flash(str(e), 'error')
    
    return redirect(url_for(f'{role_prefix}.profile'))
