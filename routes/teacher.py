from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Class, User, Enrollment, Attendance
from datetime import datetime

teacher_bp = Blueprint('teacher', __name__)

def is_teacher():
    return session.get('role') == 'teacher'

@teacher_bp.route('/dashboard')
def dashboard():
    if not is_teacher():
        return redirect(url_for('auth.login_teacher'))
    
    teacher_id = session.get('user_id')
    classes = Class.query.filter_by(teacher_id=teacher_id).all()
    return render_template('teacher_dashboard.html', classes=classes)

@teacher_bp.route('/class/<int:class_id>', methods=['GET', 'POST'])
def mark_attendance(class_id):
    if not is_teacher():
        return redirect(url_for('auth.login_teacher'))
        
    course = Class.query.get_or_404(class_id)
    if course.teacher_id != session.get('user_id'):
        flash("You are not the teacher of this class", "danger")
        return redirect(url_for('teacher.dashboard'))

    students = [e.student for e in course.enrollments]

    if request.method == 'POST':
        date_str = request.form.get('date')
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        for student in students:
            status = request.form.get(f'status_{student.id}') # present/absent
            if status:
                # Check if attendance already exists for this date/student/class
                existing = Attendance.query.filter_by(
                    student_id=student.id, 
                    class_id=class_id, 
                    date=date_obj
                ).first()
                
                if existing:
                    existing.status = status
                else:
                    new_att = Attendance(
                        student_id=student.id,
                        class_id=class_id,
                        date=date_obj,
                        status=status
                    )
                    db.session.add(new_att)
        
        db.session.commit()
        flash('Attendance updated successfully', 'success')
        return redirect(url_for('teacher.dashboard'))

    today = datetime.utcnow().strftime('%Y-%m-%d')
    return render_template('mark_attendance.html', course=course, students=students, today=today)
