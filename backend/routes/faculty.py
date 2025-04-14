import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, Response
from bson.objectid import ObjectId
from database import mongo
from pymongo import MongoClient
from flask_login import login_required, current_user
from models import Deadline, TemplateFile, Announcement, Team, TeamLeader, Submission, Project
from werkzeug.utils import secure_filename

faculty_bp = Blueprint('faculty', __name__)

# Initialize MongoDB client
mongo_client = MongoClient('mongodb://localhost:27017/')
mongo = mongo_client['ProjectEduHub']

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx', 'pptx', 'xlsx', 'csv', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS






@faculty_bp.route('/dashboard')
@login_required
def dashboard():
    teams = Team.get_all(current_user.id)
    t = {}
    for team in teams:
        t[team['team_lead']] = TeamLeader.get(team['team_lead'])
    deadlines = Deadline.get_all(current_user.id)
    deadlines.sort(key=lambda x: x['date'])
    templates = TemplateFile.get_all(current_user.id)
    announcements = Announcement.get_all(current_user.id)
    announcements.reverse()
    return render_template('faculty_dashboard.html', teams=teams, deadlines=deadlines, templates=templates, announcements=announcements, t=t)


@faculty_bp.route('/create_team_and_leaders', methods=['GET', 'POST'])
@login_required
def create_team_and_leaders():
    if request.method == 'POST':
        name = request.form['name']

        roll_no = request.form['roll_no_1']
        leader_name = request.form['name_1']
        branch = request.form['branch_1']
        section = request.form['section_1']
        email = request.form['email_1']
        username = request.form['username_1']  # Added
        password = request.form['password_1']  # Added
        x = TeamLeader.create(roll_no, leader_name, branch, section, email,username, password)
        

        Team.create(name,x, current_user.id,roll_no)
        

        flash('Team and leader created', 'success')
        return redirect(url_for('faculty.dashboard'))
 

    return render_template('create_team_and_leaders.html')


@faculty_bp.route('/delete_team/<team_id>')
@login_required
def delete_team(team_id):
    team = Team.get(team_id)
    if not team:
        flash('Team not found.', 'error')
        return redirect(url_for('faculty.dashboard'))
    submissions = Submission.get_by_team_id(team_id)
    if submissions:
        Submission.delete(submissions['_id']) 
    TeamLeader.delete(team['team_lead'])
    project = Project.get_by_team_lead_roll_no(team['team_lead_roll'])
    if project:
        # Delete screenshots
        if project.get('screenshot_ids'):
            for file_path in project['screenshot_ids']:
                if os.path.exists(file_path):
                    os.remove(file_path)

        # Delete zip file
        if project.get('zip_file_id'):
            zip_file_path = project['zip_file_id']
            if os.path.exists(zip_file_path):
                os.remove(zip_file_path)
    if project:
        Project.delete(project['_id'])
    Team.delete(team_id)
    flash('Team deleted', 'success')
    return redirect(url_for('faculty.dashboard'))



@faculty_bp.route('/team/<team_id>/project_details')
@login_required
def faculty_project_details(team_id):
    team = Team.get(team_id)
    if not team:
        flash('Team not found.', 'error')
        return redirect(url_for('faculty.dashboard'))
    # print(team)
    project = Project.get_by_team_lead_roll_no(team["team_lead_roll"])
    submissions = Submission.get_by_team_id(team_id)
    # print(submissions)  # Fetch submissions for the team
    print(submissions,"nnn")
    return render_template('faculty_project_details.html', project=project, team_id=team_id, submissions=submissions) # Pass team_id to template



# @faculty_bp.route('/team/<team_id>')
# @login_required
# def team_details(team_id):
#     team = Team.get(team_id)
#     if not team:
#         flash('Team not found.', 'error')
#         return redirect(url_for('faculty_bp.some_faculty_route')) # Redirect to a relevant faculty page

#     submissions = Submission.get_all(team_id)
#     leaders = TeamLeader.get_all_by_team(team_id)
#     project = mongo.db.projects.find_one({'team_id': ObjectId(team_id)}) # Fetch project details
#     return render_template('team_details.html', team=team, submissions=submissions, leaders=leaders, project=project)
# faculty.py
@faculty_bp.route('/team/<team_id>/give_marks', methods=['GET', 'POST'])
@login_required
def give_marks(team_id):
    """
    Handles the awarding of marks.  Creates a submission if one doesn't exist.

    Args:
        team_id (str): The ID of the team.

    Returns:
        A redirect to the faculty project details page.
    """
    team = Team.get(team_id)
    if not team:
        flash('Team not found.', 'error')
        return redirect(url_for('faculty.dashboard'))

    project = Project.get_by_team_lead_roll_no(team["team_lead_roll"])
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('faculty.dashboard'))

    # Get the latest submission or create a new one if none exists
    submissions = (Submission.get_by_team_id(team_id))
    if submissions:
        latest_submission_id = submissions['_id']  # Get the latest submission ID
    else:
        latest_submission_id = Submission.create(team_id)  # Create a new submission

    print(latest_submission_id)
    if request.method == 'POST':
        marks_data = {}
        student_feedback = {}  # Dictionary to store feedback for each student
        for member in project['team_members']:
            roll_no = member['roll_no']
            marks = request.form.get(f'marks_{roll_no}')  # Use get to avoid KeyError
            feedback = request.form.get(f'feedback_{roll_no}') #get feedback for student
            if marks:
                marks_data[roll_no] = marks # Convert each mark to float
                student_feedback[roll_no] = feedback # Store feedback
            else:
                marks_data[roll_no] = "0.0"
                student_feedback[roll_no] = ""
        # print(marks_data)
        # print(student_feedback)
        overall_feedback = request.form.get('overall_feedback')
        # print(overall_feedback)
        Submission.give_marks(latest_submission_id, marks_data, student_feedback,overall_feedback)  # Use the submission ID
        flash('Marks recorded successfully.', 'success')
        return redirect(url_for('faculty.faculty_project_details', team_id=team_id))

    submissions = Submission.get_by_team_id(team_id) # Change Here
    return render_template('faculty_project_details.html', project=project, team=team, submissions=submissions)


@faculty_bp.route('/add_deadline', methods=['GET', 'POST'])
@login_required
def add_deadline():
    if request.method == 'POST':
        title = request.form['title']
        date = request.form['date']
        Deadline.create(title, date, current_user.id)
        flash('Deadline added', 'success')
        return redirect(url_for('faculty.dashboard'))
    return render_template('add_deadline.html')

@faculty_bp.route('/add_announcement', methods=['GET', 'POST'])
@login_required
def add_announcement():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        Announcement.create(title, content, current_user.id)
        flash('Announcement added', 'success')
        return redirect(url_for('faculty.dashboard'))
    return render_template('add_announcement.html')

@faculty_bp.route('/list_announcements')
@login_required
def list_announcements():
    announcements = Announcement.get_all(current_user.id)
    return render_template('list_announcements.html', announcements=announcements)

@faculty_bp.route('/upload_template', methods=['GET', 'POST'])
@login_required
def upload_template():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            try:
                file.save(filepath)
                TemplateFile.create(filename, filepath, current_user.id)
                flash('Template uploaded', 'success')
                return redirect(url_for('faculty.dashboard'))
            except Exception as e:
                flash(f'Error uploading file: {e}', 'error')
                return redirect(request.url)
        else:
            flash('Invalid file type', 'error')
            return redirect(request.url)
    return render_template('upload_template.html')

@faculty_bp.route('/download_template/<file_id>')
@login_required
def download_template(file_id):
    # print(file_id)
    file_data = mongo["template_files"].find_one({'_id': ObjectId(file_id)})
    if file_data:
        filepath = file_data['filepath']
        filename = file_data['filename']
        print(f"Attempting to download file from: {filepath}")  # Debugging
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                file_content = f.read()
            return Response(
                file_content,
                mimetype='application/octet-stream',
                headers={'Content-Disposition': f'attachment; filename={filename}'}
            )
        else:
            flash('File not found on server.', 'error')
            return redirect(url_for('faculty.dashboard'))
    else:
        flash('File record not found.', 'error')
    # TemplateFile.get(file_id)
    return redirect(url_for('faculty.dashboard'))


@faculty_bp.route('/delete_template/<file_id>')
@login_required
def delete_template(file_id):
    
    file_data = mongo["template_files"].find_one({'_id': ObjectId(file_id)})
    print(f"delete_template called with file_id: {file_data}, type: {type(file_data)}") 
    if file_data:
        filepath = file_data['filepath']
        if os.path.exists(filepath):
            os.remove(filepath)
        mongo["template_files"].delete_one({'_id': ObjectId(file_id)})
        flash('Template deleted', 'success')
    else:
        flash('Template record not found.', 'error')
    # TemplateFile.delete(file_id)
    return redirect(url_for('faculty.dashboard'))


@faculty_bp.route('/download_zip/<zip_file_id>')
@login_required
def download_zip(zip_file_id):
    """
    Allows faculty to download submitted zip files.

    Args:
        zip_file_id (str): The ID of the zip file to download (which is the ObjectId of the project).

    Returns:
        A Flask Response object containing the file, or a redirect with an error.
    """
    print(f"download_zip called with zip_file_id: {zip_file_id}, type: {type(zip_file_id)}")
    project = Project.get_by_id(zip_file_id)  # Use Project.get to retrieve project
    if project:
        filepath = project['zip_file_id'] # Access the zip_file_id from the project
        filename = os.path.basename(filepath)  # Get the filename from the filepath
        print(f"Attempting to download zip file from: {filepath}")
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                file_content = f.read()
            return Response(
                file_content,
                mimetype='application/zip',  # Set the correct mimetype for zip files
                headers={'Content-Disposition': f'attachment; filename={filename}'}
            )
        else:
            flash('Zip file not found on server.', 'error')
            return redirect(url_for('faculty.dashboard'))  # Or appropriate faculty route
    else:
        flash('Project record not found.', 'error')
        return redirect(url_for('faculty.dashboard'))  # Or appropriate faculty route

