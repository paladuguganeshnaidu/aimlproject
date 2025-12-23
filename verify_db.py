from app import app, db
from models import User, Attendance, Class, Enrollment

def verify_system():
    with app.app_context():
        # Check Users
        all_users = User.query.all()
        print(f"DEBUG: All Users: {[u.email for u in all_users]}")
        teacher = User.query.filter_by(email='teacher@test.com').first()
        if not student: return "FAIL: Student not found"
        
        # Check Class
        math_class = Class.query.filter_by(class_name='Math 101').first()
        if not math_class: return "FAIL: Class not found"
        
        # Check Enrollment
        enrollment = Enrollment.query.filter_by(student_id=student.id, class_id=math_class.id).first()
        if not enrollment: return "FAIL: Enrollment not found"
        
        # Check Attendance
        attendance = Attendance.query.filter_by(student_id=student.id, class_id=math_class.id).first()
        if not attendance: return "FAIL: No attendance record found"
        if attendance.status != "Present": return f"FAIL: Attendance status is {attendance.status}"
        
        return "SUCCESS: All data verified in DB"

if __name__ == "__main__":
    print(verify_system())
