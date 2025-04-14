from flask import Flask
import os
from database import init_db
from routes.auth import auth_bp
from routes.student import student_bp
from routes.faculty import faculty_bp
from routes.admin import admin_bp
from flask_login import LoginManager
from models import User,TeamLeader

# Explicitly set the template folder
template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../templates')

app = Flask(__name__, template_folder=template_folder, static_folder='student_uploads', static_url_path='/uploads/student')
app.config['SECRET_KEY'] = '112233445566778899'  # Replace with a strong secret key

init_db(app)

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(student_bp, url_prefix='/student')
app.register_blueprint(faculty_bp, url_prefix='/faculty')
app.register_blueprint(admin_bp, url_prefix='/admin')

login_manager = LoginManager()
login_manager.init_app(app)

from models import User

# def load_user(user_id):
#     print(f"User loader called with user_id: {user_id}")
#     user = User.get(user_id)
#     print(f"User loaded: {user}")
#     return user

@login_manager.user_loader
def load_user(user_id):
    user = User.get(user_id)  # Your User.get method
    if user:
        return user
    else:
        tl = TeamLeader.get_tl(user_id) #Or TeamLeader.get, adjust as needed
        if tl:
            return tl
        else:
            return None

if __name__ == '__main__':
    app.run(debug=True)