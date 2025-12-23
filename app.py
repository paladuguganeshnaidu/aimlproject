import os
from flask import Flask, redirect, url_for
from models import db, bcrypt
# Import routes
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.teacher import teacher_bp
from routes.student import student_bp

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_123')
    # Render provides DATABASE_URL, usually requires replacing postgres:// with postgresql://
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(teacher_bp, url_prefix='/teacher')
    app.register_blueprint(student_bp, url_prefix='/student')

    @app.route('/')
    def index():
        return redirect(url_for('auth.login_student')) # Default redirect

    with app.app_context():
        db.create_all()
        # Seed default admin if no users exist
        from models import User
        if not User.query.filter_by(role='admin').first():
            hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin = User(name='Admin User', email='admin@school.com', password_hash=hashed_pw, role='admin')
            db.session.add(admin)
            db.session.commit()
            print("Default admin created: admin@school.com / admin123")

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
