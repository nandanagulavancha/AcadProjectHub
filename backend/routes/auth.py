from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from models import User,TeamLeader
from werkzeug.security import check_password_hash
from bson.objectid import ObjectId

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    print("Login route accessed")
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        print(f"Username: {username}, Role: {role}")

        if role == 'student':
            tl = TeamLeader.get_tl(username)  # Assuming you have this method in TeamLeader
            print(f"Team leader found: {tl}")
            if tl and check_password_hash(tl.password, password):  # and password check
                login_user(tl)  # Log in the team leader
                # session['role'] = 'team_leader'  # Store role in session
                print("Team leader logged in")
                return redirect(url_for('student.dashboard'))  # Redirect to team leader dashboard
            else:
                print("Invalid team leader credentials")
                flash('Invalid username or password', 'danger')


        user = User.get(username) #get user by username
        if user:
            print(f"User found: {user.username}, Role: {user.role}")
            if check_password_hash(user.password, password) and user.role == role:
                print("Password and role match")
                login_user(user) #flask_login loads by user object
                print(f"User logged in: {current_user.username}")
                if role == 'student':
                    return redirect(url_for('student.dashboard'))
                if role == 'faculty':
                    return redirect(url_for('faculty.dashboard'))
                elif role == 'admin':
                    return redirect(url_for('admin.dashboard'))
            else:
                print("Password or role mismatch")
                flash('Invalid username, password, or role')
        else:
            print("User not found")
            flash('Invalid username, password, or role')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    print("Logout route accessed")
    logout_user()
    print("User logged out")
    return redirect(url_for('auth.login'))