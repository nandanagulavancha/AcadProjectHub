from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, current_user, login_required
from models import User, TeamLeader, generate_temporary_password  # Import password generator
from werkzeug.security import check_password_hash, generate_password_hash
from database import mongo
from datetime import datetime, timedelta
import secrets
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bson.objectid import ObjectId

auth_bp = Blueprint('auth', __name__, template_folder='../templates')

def send_temporary_password_email(to_email, username, password, role):
    subject = f"Your Temporary Password for ProjectEduHub"
    body = f"""
    Hello {username},

    You requested a password reset for your AcadProjectHub account. A temporary password has been generated for you:

    Temporary Password: {password}

    Please log in {url_for('auth.login', _external=True)} with this temporary password and change it immediately for security reasons.

    Thank you,
    The ProjectEduHub Team
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = current_app.config['MAIL_DEFAULT_SENDER']
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']) as server:
            server.starttls()
            server.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
            server.sendmail(current_app.config['MAIL_DEFAULT_SENDER'], to_email, msg.as_string())
        print(f"Temporary password email sent to {to_email} for {role}")
        return True
    except Exception as e:
        print(f"Error sending temporary password email to {to_email} for {role}: {e}")
        return False

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
                print("Team leader logged in")
                return redirect(url_for('student.dashboard'))  # Redirect to team leader dashboard
            else:
                print("Invalid team leader credentials")
                flash('Invalid username or password', 'danger')


        user = User.get_by_username(username) #get user by username
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

@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.get_by_email(email)
        team_leader = TeamLeader.get_by_email(email)

        if user:
            temp_password = generate_temporary_password()
            hashed_password = generate_password_hash(temp_password)
            mongo.db.users.update_one({'email': email}, {'$set': {'password': hashed_password}})
            if send_temporary_password_email(email, user.username, temp_password, 'user'):
                flash('A temporary password has been sent to your email address. Please log in and change it.', 'info')
                return redirect(url_for('auth.login'))
            else:
                flash('Failed to send temporary password. Please try again.', 'danger')
        elif team_leader:
            temp_password = generate_temporary_password()
            hashed_password = generate_password_hash(temp_password)
            mongo.db.team_leaders.update_one({'email': email}, {'$set': {'password': hashed_password}})
            if send_temporary_password_email(email, team_leader.username, temp_password, 'team_leader'):
                flash('A temporary password has been sent to your email address. Please log in and change it.', 'info')
                return redirect(url_for('auth.login'))
            else:
                flash('Failed to send temporary password. Please try again.', 'danger')
        else:
            flash('No account found with that email address.', 'warning')
            return render_template('forgot_password.html')
    return render_template('forgot_password.html')

@auth_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return render_template('change_password.html')

        user = None
        if isinstance(current_user, User):
            user = User.get(current_user.id)
            if user and check_password_hash(user.password, current_password):
                hashed_password = generate_password_hash(new_password)
                mongo.db.users.update_one({'_id': ObjectId(user.id)}, {'$set': {'password': hashed_password}})
                flash('Your password has been changed successfully.', 'success')
                return redirect(url_for('auth.login')) # Or a profile/settings page
            else:
                flash('Incorrect current password.', 'danger')
                return render_template('change_password.html')
        elif isinstance(current_user, TeamLeader):
            tl = TeamLeader.get_tl(current_user.id)
            if tl and check_password_hash(tl.password, current_password):
                hashed_password = generate_password_hash(new_password)
                mongo.db.team_leaders.update_one({'_id': ObjectId(tl.id)}, {'$set': {'password': hashed_password}})
                flash('Your password has been changed successfully.', 'success')
                return redirect(url_for('auth.login')) # Or a profile/settings page
            else:
                flash('Incorrect current password.', 'danger')
                return render_template('change_password.html')
        else:
            flash('Something went wrong. Please try again.', 'danger')
            return render_template('change_password.html')

    return render_template('change_password.html')