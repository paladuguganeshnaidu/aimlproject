from flask import Blueprint, render_template, session, redirect, url_for
from models import Attendance, Class, Enrollment

student_bp = Blueprint('student', __name__)

def is_student():
    return session.get('role') == 'student'

@student_bp.route('/dashboard')
def dashboard():
    if not is_student():
        return redirect(url_for('auth.login_student'))
    
    student_id = session.get('user_id')
    
    # Get all classes student is enrolled in
    enrollments = Enrollment.query.filter_by(student_id=student_id).all()
    
    data = []
    for enrollment in enrollments:
        course = enrollment.enrolled_class
        
        # Total classes held (distinct dates for this class in attendance table)
        # Note: This checks how many days attendance was taken for this class
        total_days_query = Attendance.query.with_entities(Attendance.date).filter_by(class_id=course.id).distinct().all()
        total_classes = len(total_days_query)
        
        # Attended classes
        attended = Attendance.query.filter_by(
            student_id=student_id, 
            class_id=course.id, 
            status='Present'
        ).count()
        
        percentage = 0
        if total_classes > 0:
            percentage = (attended / total_classes) * 100
            
        data.append({
            'class_name': course.class_name,
            'total_classes': total_classes,
            'attended': attended,
            'percentage': round(percentage, 2),
            'warning': percentage < 80
        })
        
    return render_template('student_dashboard.html', attendance_data=data)
