from flask import Flask
import os
from database import init_db, mongo
from routes.auth import auth_bp
from routes.student import student_bp
from routes.faculty import faculty_bp
from routes.admin import admin_bp
from flask_login import LoginManager
from models import User, TeamLeader
from werkzeug.security import generate_password_hash

template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../templates')

app = Flask(__name__, template_folder=template_folder, static_folder='student_uploads', static_url_path='/uploads/student')


app.config['SECRET_KEY'] = '112233445566778899'  
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'nanda190506@gmail.com'
app.config['MAIL_PASSWORD'] = 'qffh rmzw fesm kpyz'
app.config['MAIL_DEFAULT_SENDER'] = 'nanda190506@gmail.com'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'student_uploads')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

init_db(app)

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(student_bp, url_prefix='/student')
app.register_blueprint(faculty_bp, url_prefix='/faculty')
app.register_blueprint(admin_bp, url_prefix='/admin')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    user = User.get(user_id)
    if user:
        return user
    return TeamLeader.get_tl(user_id)

def create_default_admin():
    """Creates a default admin user if one doesn't exist in the database."""
    try:
        with app.app_context():
            if not mongo.db.users.find_one({'username': 'admin'}):
                hashed_password = generate_password_hash('admin')
                mongo.db.users.insert_one({
                    'username': 'admin',
                    'email': 'admin1@example.com',
                    'password': hashed_password,
                    'role': 'admin'
                })
                print("Default admin user created.")
            else:
                print("Admin user already exists.")
    except Exception as e:
        print(f"Error creating default admin: {e}")

if __name__ == '__main__':
    create_default_admin()
    app.run(debug=True, port=3000)