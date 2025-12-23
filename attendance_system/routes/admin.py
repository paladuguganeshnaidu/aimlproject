from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User, Class, Enrollment, bcrypt

admin_bp = Blueprint('admin', __name__)

def is_admin():
    return session.get('role') == 'admin'

@admin_bp.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not is_admin():
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login_teacher')) # Redirect somewhere safe

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add_user':
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            role = request.form.get('role')
            
            hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = User(name=name, email=email, password_hash=hashed_pw, role=role)
            db.session.add(new_user)
            db.session.commit()
            flash(f'User {name} created!', 'success')
            
        elif action == 'add_class':
            class_name = request.form.get('class_name')
            teacher_id = request.form.get('teacher_id')
            new_class = Class(class_name=class_name, teacher_id=teacher_id)
            db.session.add(new_class)
            db.session.commit()
            flash(f'Class {class_name} created!', 'success')
            
        elif action == 'assign_student':
            student_id = request.form.get('student_id')
            class_id = request.form.get('class_id')
            
            # Check if already enrolled
            exists = Enrollment.query.filter_by(student_id=student_id, class_id=class_id).first()
            if not exists:
                enrollment = Enrollment(student_id=student_id, class_id=class_id)
                db.session.add(enrollment)
                db.session.commit()
                flash('Student enrolled!', 'success')
            else:
                flash('Student already enrolled.', 'warning')

    teachers = User.query.filter_by(role='teacher').all()
    students = User.query.filter_by(role='student').all()
    classes = Class.query.all()
    
    return render_template('admin.html', teachers=teachers, students=students, classes=classes)
