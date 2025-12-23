from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import User, bcrypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login/teacher', methods=['GET', 'POST'])
def login_teacher():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.role in ['teacher', 'admin'] and bcrypt.check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['role'] = user.role
            session['name'] = user.name
            
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('teacher.dashboard'))
        else:
            flash('Invalid email or password', 'danger')
            
    return render_template('login_teacher.html')

@auth_bp.route('/login/student', methods=['GET', 'POST'])
def login_student():
    if request.method == 'POST':
        email = request.form.get('email') # or roll number if stored in email or separate field. User schema says email.
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email, role='student').first()
        
        if user and bcrypt.check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['role'] = 'student'
            session['name'] = user.name
            return redirect(url_for('student.dashboard'))
        else:
            flash('Invalid credentials', 'danger')

    return render_template('login_student.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login_student'))
