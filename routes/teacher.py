from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from models import db, Class, User, Enrollment, Attendance
from datetime import datetime
import pandas as pd
import io

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

@teacher_bp.route('/class/<int:class_id>/history')
def view_history(class_id):
    if not is_teacher():
        return redirect(url_for('auth.login_teacher'))
        
    course = Class.query.get_or_404(class_id)
    if course.teacher_id != session.get('user_id'):
        flash("You are not the teacher of this class", "danger")
        return redirect(url_for('teacher.dashboard'))

    # Fetch all attendance records for this class
    # Join with User to get student names
    history = db.session.query(Attendance, User).join(User, Attendance.student_id == User.id)\
        .filter(Attendance.class_id == class_id)\
        .order_by(Attendance.date.desc(), User.name).all()
    
    return render_template('class_history.html', course=course, history=history)

@teacher_bp.route('/class/<int:class_id>/export')
def export_attendance(class_id):
    if not is_teacher():
        return redirect(url_for('auth.login_teacher'))

    course = Class.query.get_or_404(class_id)
    if course.teacher_id != session.get('user_id'):
        return redirect(url_for('teacher.dashboard'))

    # Query data
    records = db.session.query(Attendance.date, User.name, User.email, Attendance.status)\
        .join(User, Attendance.student_id == User.id)\
        .filter(Attendance.class_id == class_id)\
        .order_by(Attendance.date.desc(), User.name).all()

    # Convert to DataFrame
    data = [{
        'Date': r[0],
        'Student Name': r[1],
        'Email': r[2],
        'Status': r[3]
    } for r in records]

    df = pd.DataFrame(data)

    # Export to Excel in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Attendance')
    
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'Attendance_{course.class_name}_{datetime.now().strftime("%Y%m%d")}.xlsx'
    )
