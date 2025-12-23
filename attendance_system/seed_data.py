from app import app, db, bcrypt
from models import User, Class, Enrollment, Attendance

def seed_data():
    with app.app_context():
        print("Dropping existing tables...")
        db.drop_all()
        db.create_all()
        print("Tables recreated.")

        # --- 1. Create Teachers ---
        teachers_data = [
            ("DS Teacher", "ds.teacher@mail.com", "Data Structures"),
            ("DBMS Teacher", "dbms.teacher@mail.com", "DBMS"),
            ("Full Stack Teacher", "fs.teacher@mail.com", "Full Stack"),
            ("AI Teacher", "ai.teacher@mail.com", "Artificial Intelligence")
        ]

        teacher_objs = {} # Map subject to teacher user obj
        hashed_pw_teacher = bcrypt.generate_password_hash('Teacher@123').decode('utf-8')

        for name, email, subject in teachers_data:
            user = User(name=name, email=email, password_hash=hashed_pw_teacher, role='teacher')
            db.session.add(user)
            db.session.commit() # Commit to get ID
            teacher_objs[subject] = user
            print(f"Created Teacher: {name} ({email})")

        # --- 2. Create Classes (3 Sections per Subject) ---
        # Subject -> { 'A': class_obj, 'B': class_obj, 'C': class_obj }
        classes_map = {
            "Data Structures": {},
            "DBMS": {},
            "Full Stack": {},
            "Artificial Intelligence": {}
        }

        sections = ['A', 'B', 'C']
        
        for subject, teacher_user in teacher_objs.items():
            for section in sections:
                class_name = f"{subject} - Class {section}"
                new_class = Class(class_name=class_name, teacher_id=teacher_user.id)
                db.session.add(new_class)
                db.session.commit()
                classes_map[subject][section] = new_class
                print(f"Created Class: {class_name}")

        # --- 3. Create Students & Enrollments ---
        hashed_pw_student = bcrypt.generate_password_hash('Student@123').decode('utf-8')
        
        # Pattern from image: 1->B, 2->C, 3->A
        section_pattern = {1: 'B', 2: 'C', 0: 'A'}

        for i in range(1, 21):
            name = f"Student{i}"
            email = f"student{i}@mail.com"
            
            # Determine section
            section_key = i % 3
            student_section = section_pattern[section_key]

            student = User(name=name, email=email, password_hash=hashed_pw_student, role='student')
            db.session.add(student)
            db.session.commit()

            # Enroll in ALL 4 subjects for their section
            subjects = ["Data Structures", "DBMS", "Full Stack", "Artificial Intelligence"]
            for subj in subjects:
                target_class = classes_map[subj][student_section]
                enrollment = Enrollment(student_id=student.id, class_id=target_class.id)
                db.session.add(enrollment)
            
            print(f"Created {name} ({email}) - Assigned to Class {student_section}")

        # --- 4. Identify Admin ---
        hashed_pw_admin = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin = User(name='Admin', email='admin@school.com', password_hash=hashed_pw_admin, role='admin')
        db.session.add(admin)
        
        db.session.commit()
        print("\nDATA SEEDING COMPLETE!")
        print("------------------------------------------------")
        print("Teachers: Teacher@123")
        print("Students: Student@123")
        print("Admin:    admin123")

if __name__ == "__main__":
    seed_data()
