from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import User, Team, Announcement, TemplateFile, Deadline, generate_temporary_password  # Import the relevant models and password generator
from database import mongo  # Import your MongoDB connection

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    faculty_users = User.get_all_faculty()
    return render_template('admin_dashboard.html', faculty_users=faculty_users)

@admin_bp.route('/create_faculty', methods=['GET', 'POST'])
@login_required
def create_faculty():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        faculty_roll_no = request.form['faculty_roll_no']

        # Check for existing faculty with same email, username, or roll number
        existing_user = mongo.db.users.find_one({
            '$or': [
                {'email': email},
                {'username': username},
                {'faculty_roll_no': faculty_roll_no}
            ]
        })

        if existing_user:
            if existing_user['email'] == email:
                flash('A faculty with this email already exists.', 'error')
            elif existing_user['username'] == username:
                flash('A faculty with this username already exists.', 'error')
            else:
                flash('A faculty with this Faculty ID already exists.', 'error')
            return redirect(url_for('admin.dashboard'))

        # Generate a temporary password
        temp_password = generate_temporary_password()

        User.create(username=username, email=email, password=temp_password, role='faculty', name=name, faculty_roll_no=faculty_roll_no)
        flash(f'Faculty account for {name} created. Credentials sent to {email}.', 'success')
        return redirect(url_for('admin.dashboard'))
    
    # If it's a GET request, redirect to the dashboard
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/delete_faculty', methods=['GET', 'POST'])
@login_required
def delete_faculty():
    """
    Deletes a faculty member and reassigns their students to a new faculty member.
    Also deletes announcements, template files, and deadlines associated with the faculty.
    """
    faculty_users = User.get_all_faculty()
    if request.method == 'POST':
        faculty_id_to_delete = request.form['new_faculty_id']
        new_faculty_id = request.form['reassign_faculty_id']  # Get the ID of the new faculty
        print(f"Faculty ID to delete: {faculty_id_to_delete}, New faculty ID: {new_faculty_id}")
        print("faculty_users:", faculty_users)
        if faculty_id_to_delete == new_faculty_id:
            flash('Cannot reassign students to the same faculty being deleted.', 'error')
            return render_template('delete_faculty.html', faculty_users=faculty_users)

        # 1. Reassign teams to the new faculty
        teams_to_update = Team.get_all(faculty_id_to_delete)
        # get teams by faculty id
        print(teams_to_update)
        for team in teams_to_update:
            print(team['_id'])
            Team.update_faculty_id(team['_id'], new_faculty_id)

        # 2. Delete announcements, template files, and deadlines
        Announcement.delete_by_faculty_id(faculty_id_to_delete)
        TemplateFile.delete_by_faculty_id(faculty_id_to_delete)
        Deadline.delete_by_faculty_id(faculty_id_to_delete)

        # 3. Delete the faculty user
        User.delete(faculty_id_to_delete)

        flash('Faculty deleted and teams reassigned.', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('delete_faculty.html',  faculty_users=faculty_users)

@admin_bp.route('/faculty_details/<faculty_id>')
@login_required
def faculty_details(faculty_id):
    faculty = User.get(faculty_id)
    return render_template('faculty_details.html', faculty=faculty)