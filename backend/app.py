from flask import Flask
import os
from database import init_db, mongo  # Import mongo from database.py
from routes.auth import auth_bp
from routes.student import student_bp
from routes.faculty import faculty_bp
from routes.admin import admin_bp
from flask_login import LoginManager
from models import User, TeamLeader
from werkzeug.security import generate_password_hash  # Import for password hashing


# Explicitly set the template folder
template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../templates')

app = Flask(__name__, template_folder=template_folder, static_folder='student_uploads', static_url_path='/uploads/student')
app.config['SECRET_KEY'] = '112233445566778899'  # Replace with a strong secret key

init_db(app)  # Initialize the database


app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(student_bp, url_prefix='/student')
app.register_blueprint(faculty_bp, url_prefix='/faculty')
app.register_blueprint(admin_bp, url_prefix='/admin')

login_manager = LoginManager()
login_manager.init_app(app)



@login_manager.user_loader
def load_user(user_id):
    user = User.get(user_id)  # Your User.get method
    if user:
        return user
    else:
        tl = TeamLeader.get_tl(user_id)  # Or TeamLeader.get, adjust as needed
        if tl:
            return tl
        else:
            return None


def create_default_admin():
    """
    Creates a default admin user if one doesn't exist in the database.
    """
    with app.app_context():  # Ensure we're in the Flask application context
        if not mongo.db.users.find_one({'username': 'admin'}):
            hashed_password = generate_password_hash('admin')  # Hash the password
            mongo.db.users.insert_one({
                'username': 'admin',
                'email': 'admin1@example.com',
                'password': hashed_password,
                'role': 'admin'
            })
            print("Default admin user created.")  # Optional: Print a message to the console
        else:
            print("Admin user already exists.")



if __name__ == '__main__':
    #check_db_connection() #removed this as it was causing an error.
    create_default_admin()  # Create the default admin user on startup
    app.run(debug=True)
