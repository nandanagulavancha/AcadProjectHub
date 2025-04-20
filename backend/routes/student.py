# from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
# from flask_login import login_required, current_user
# from utils.file_handling import save_file
# from bson.objectid import ObjectId
# from models import Deadline, TemplateFile, Announcement, Team, TeamLeader, Submission, Project


# student_bp = Blueprint('student', __name__)


# @student_bp.route('/dashboard', methods=['GET', 'POST'])
# @login_required
# def dashboard():
#     # Assuming current_user is an instance of TeamLeader due to login manager
#     #teams = Team.get_teams_by_student(current_user.id)
#     teams = []
#     templates = []
#     deadlines = []
#     #print(current_user.roll_no)


#     #if not teams:
#      #   flash("You are not assigned to any team.", "warning")
#       #  return render_template('student_dashboard.html', deadlines=deadlines, templates=templates)


#     # Assuming all teams a student is in are under the same faculty for simplicity
#     faculty_id = teams[0]['faculty_id'] if teams else None
#     if faculty_id:
#         deadlines = Deadline.get_all(faculty_id)
#         templates = TemplateFile.get_all(faculty_id)
#         #print(deadlines)
#     else:
#         deadlines = []
#         templates = []


#     return render_template('student_dashboard.html', deadlines=deadlines, templates=templates)


# @student_bp.route('/project-submission', methods=['GET', 'POST'])
# @login_required
# def project_submission():
#     error_message = None
#     if request.method == 'POST':
#         data = request.form
#         files = request.files.getlist('files')
#         screenshot_files = request.files.getlist('screenshots')
#         file_ids = []
#         screenshot_ids = []


#         # team_lead_roll_no = data.get('team_lead_roll_no')  # Removed
#         # team_lead_name = data.get('team_lead_name')      # Removed
#         existing_project = Project.get_by_team_lead_roll_no(data.get('team_lead_roll_no')) #Still use it for validation


#         if existing_project:
#             error_message = "A project has already been submitted for this team lead."
#         elif len(files) != 1 or not files[0].filename.endswith('.zip'):
#             error_message = "Please upload exactly one file in ZIP format."
#         else:
#             zip_file = files[0]
#             zip_file_id = save_file(zip_file, zip_file.filename)
#             file_ids.append(zip_file_id)


#             for screenshot in screenshot_files:
#                 if screenshot and allowed_file(screenshot.filename):
#                     screenshot_id = save_file(screenshot, screenshot.filename)
#                     screenshot_ids.append(screenshot_id)
#                 elif screenshot:
#                     error_message = "Invalid screenshot/video file type."
#                     break


#             if not error_message:
#                 team_members = []
#                 for i in range(1, 5):
#                     member_name = data.get(f'member_name_{i}')
#                     member_roll_no = data.get(f'member_roll_no_{i}')
#                     if member_name and member_roll_no:
#                         team_members.append({'name': member_name, 'roll_no': member_roll_no})


#                 project_id = Project.create(
#                     title=data['title'],
#                     description=data['description'],
#                     team_lead_roll_no=data.get('team_lead_roll_no'), #still use it for validation
#                     team_lead_name=data.get('team_lead_name'), #still use it for validation
#                     team_members=team_members,
#                     category=data['category'],
#                     guide_name=data['guide_name'],
#                     github_link=data['github_link'],
#                     drive_link=data['drive_link'],
#                     zip_file_id=zip_file_id,
#                     screenshot_ids=screenshot_ids
#                 )
#                 flash('Project submitted successfully!', 'success')
#                 return redirect(url_for('student.dashboard')) # Redirect back to dashboard
#     if error_message:
#         flash(error_message, 'error')
#     return render_template('project_submission.html', error_message=error_message)


# def allowed_file(filename):
#     ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov'}  # Add video extensions
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




# @student_bp.route('/project-status')
# @login_required
# def project_status():
#     projects = Project.get_all()
#     student_projects = [
#         project
#         for project in projects
#         if current_user.username in project.get('team_members', [])  # Adjust as needed
#     ]
#     return render_template('project_status.html', projects=student_projects)


# @student_bp.route('/project-details/<project_id>')
# @login_required
# def project_details(project_id):
#     project = Project.get_by_id(project_id)
#     if project and current_user.username in project.get('team_members', []):  # Adjust as needed
#         return render_template('project_view.html', project=project)
#     else:
#         flash('Project not found or you do not have permission.', 'error')
#         return redirect(url_for('student.dashboard'))


# def allowed_file(filename):
#     ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov'}  # Add video extensions
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




# # @student_bp.route('/project-status')
# # @login_required
# # def project_status():
# #     projects = Project.get_all()
# #     student_projects = [
# #         project
# #         for project in projects
# #         if current_user.username in project.get('team_members', [])  # Adjust as needed
# #     ]
# #     return render_template('project_status.html', projects=student_projects)


# # @student_bp.route('/project-details/<project_id>')
# # @login_required
# # def project_details(project_id):
# #     project = Project.get_by_id(project_id)
# #     if project and current_user.username in project.get('team_members', []):  # Adjust as needed
# #         return render_template('project_view.html', project=project)
# #     else:
# #         flash('Project not found or you do not have permission.', 'error')
# #         return redirect(url_for('student.dashboard'))





from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from utils.file_handling import save_file
from bson.objectid import ObjectId
from models import Deadline, TemplateFile, Announcement, Team, TeamLeader, Submission, Project
from werkzeug.utils import secure_filename
import os
from flask import Response, abort

student_bp = Blueprint('student', __name__)
UPLOAD_FOLDER = 'student_uploads'  # Separate folder for student uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'zip'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@student_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Student dashboard: Displays project templates, deadlines,
    individual student marks, and submission status.
    Only accessible to team leaders.
    """
    teams = Team.get_by_team_lead(current_user.id)  # Use the new method
    templates = []
    deadlines = []
    student_marks = {}
    submission_status = "Not Submitted"  # Default status
    submissions = []
    announcements = []
    project = None  # Initialize project as None by default

    if teams:  # Check if teams is not empty
        faculty_id = teams[0]['faculty_id'] 
        deadlines = Deadline.get_all(faculty_id)
        templates = TemplateFile.get_all(faculty_id)
        announcements = Announcement.get_all(faculty_id)
        
        # Get project submission status
        project = Project.get_by_team_lead_roll_no(TeamLeader.get(current_user.id)['roll_no'])
        if project:
            submission_status = "Submitted"
        
        # Calculate marks for each student in the team
        for team in teams:
            submissions = Submission.get_by_team_id(team['_id'])
    else:
        flash("You are not assigned to any team.", "warning")

    return render_template(
        'student_dashboard.html',
        deadlines=deadlines,
        templates=templates,
        student_marks=student_marks,
        submission_status=submission_status,
        project=project,
        submissions=submissions,
        announcements=announcements,
        teams=teams
    )

@student_bp.route('/project-submission', methods=['GET', 'POST'])
@login_required
def project_submission():
    """
    Team leaders submit or edit project details.
    """
    tl = TeamLeader.get(current_user.id)
    error_message = None
    existing_project = Project.get_by_team_lead_roll_no(tl['roll_no'])
    project_data = None

    if existing_project:
        project_data = existing_project

    if request.method == 'POST':
        data = request.form
        files = request.files.getlist('files')
        screenshot_files = request.files.getlist('screenshots')
        file_ids = []
        screenshot_ids = []
        existing_screenshot_ids = existing_project.get('screenshot_ids', []) if existing_project else []

        if existing_project and len(files) > 1:
            error_message = "You can only upload one ZIP file."
        # elif not existing_project and (len(files) > 1 or not files[0].filename.endswith('.zip')):
        #     error_message = "Please upload exactly one file in ZIP format."
        elif len(files) == 1 and files[0].filename.endswith('.zip'):
            zip_file = files[0]
            filename = secure_filename(zip_file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            zip_file.save(filepath)
            zip_file_id = filepath  # Store the filepath instead of relying on external save_file
            file_ids.append(zip_file_id)
        elif existing_project and not files:
            file_ids.append(existing_project.get('zip_file_id')) # Keep existing if no new upload

        for screenshot in screenshot_files:
            if screenshot and allowed_file(screenshot.filename):
                filename = secure_filename(screenshot.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                screenshot.save(filepath)
                screenshot_ids.append(filepath) # Store the filepath
            elif screenshot:
                error_message = "Invalid screenshot/video file type."
                break
        updated_screenshot_ids = existing_screenshot_ids + screenshot_ids

        # Keep existing screenshots if no new ones are uploaded
        if existing_project and not screenshot_files:
            screenshot_ids.extend(existing_project.get('screenshot_ids', []))

        if not error_message:
            team_members = []
            for i in range(1, 5):
                member_name = data.get(f'member_name_{i}')
                member_roll_no = data.get(f'member_roll_no_{i}')
                if member_name and member_roll_no:
                    team_members.append({'name': member_name, 'roll_no': member_roll_no})

            if existing_project:
                # Update existing project
                Project.update(
                    existing_project.get('_id'),
                    title=data['title'],
                    description=data['description'],
                    team_members=team_members,
                    category=data['category'],
                    guide_name=data['guide_name'],
                    github_link=data['github_link'],
                    drive_link=data['drive_link'],
                    zip_file_id=file_ids[0] if file_ids else existing_project.get('zip_file_id'),
                    screenshot_ids=updated_screenshot_ids
                )
                flash('Project updated successfully!', 'success')
                return redirect(url_for('student.dashboard'))
            else:
                # Create a new project
                Project.create(
                    title=data['title'],
                    description=data['description'],
                    team_lead_roll_no=tl['roll_no'],
                    team_lead_name=tl['name'],
                    team_members=team_members,
                    category=data['category'],
                    guide_name=data['guide_name'],
                    github_link=data['github_link'],
                    drive_link=data['drive_link'],
                    zip_file_id=file_ids[0] if file_ids else None,
                    screenshot_ids=screenshot_ids
                )
                flash('Project submitted successfully!', 'success')
                return redirect(url_for('student.dashboard'))

        if error_message:
            flash(error_message, 'error')

    return render_template('project_submission.html', error_message=error_message, project=project_data)

@student_bp.route('/uploads/student/<filename>')
@login_required
def get_student_upload(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'rb') as f:
                image_data = f.read()
                # Determine mimetype based on filename extension
                mimetype = 'image/png'
                if filename.lower().endswith(('.jpg', '.jpeg')):
                    mimetype = 'image/jpeg'
                elif filename.lower().endswith('.gif'):
                    mimetype = 'image/gif'
                elif filename.lower().endswith('.mp4'):
                    mimetype = 'video/mp4'
                elif filename.lower().endswith('.mov'):
                    mimetype = 'video/quicktime'
                return Response(image_data, mimetype=mimetype)
        except FileNotFoundError:
            flash('Image/Video not found.', 'error')
            return abort(404)
        except Exception as e:
            flash(f'Error loading image/video: {e}', 'error')
            return abort(500)
    else:
        flash('Image/Video not found.', 'error')
        return abort(404)


@student_bp.route('/project-status')
@login_required
def project_status():
    """
    Display the submission status of the project.
    """
    project = Project.get_by_team_lead_id(current_user.id)
    status = "Not Submitted"
    if project:
        status = "Submitted"
        return render_template('project_status.html', status=status)
    else:
        return render_template('project_status.html', status=status)


@student_bp.route('/project-details/<project_id>')
@login_required
def project_details(project_id):
    """
    View details of a submitted project.
    """
    teams = Team.get_teams_by_student(current_user.id)
    project = Project.get_by_id(project_id)
    # if project and current_user.id == project.get('team_lead_id'): 
    #      # Only team leader can view
    submissions = []
    for team in teams:
            submissions = Submission.get_by_team_id(team['_id'])
    return render_template('project_details.html', project=project,submissions=submissions)
    # else:
    # flash('Project not found or you do not have permission.', 'error')
    # return redirect(url_for('student.dashboard'))

UPLOAD_FOLDER = 'student_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'zip'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@student_bp.route('/delete_media/<project_id>/<filename>', methods=['GET', 'POST'])
@login_required
def delete_media(project_id, filename):
    project = Project.get_by_id(project_id)
    tl = TeamLeader.get(current_user.id)

    if not project or project.get('team_lead_roll_no') != tl['roll_no']:
        flash('Project not found or you do not have permission to delete.', 'error')
        return redirect(url_for('student.project_submission'))

    filepath_to_delete = os.path.join(UPLOAD_FOLDER, filename)

    if os.path.exists(filepath_to_delete):
        try:
            os.remove(filepath_to_delete)
            Project.delete_media(project_id, filepath_to_delete)
            # flash(message, 'success' if success else 'error')
        except OSError as e:
            flash(f'Error deleting {filename}: {e}', 'error')
    else:
        flash(f'File {filename} not found on the server.', 'warning')

    return redirect(url_for('student.project_submission'))

@student_bp.route('/delete_zip/<project_id>', methods=['POST'])
@login_required
def delete_zip(project_id):
    project = Project.get_by_id(project_id)
    tl = TeamLeader.get(current_user.id)

    if not project or project.get('team_lead_roll_no') != tl['roll_no']:
        flash('Project not found or you do not have permission to delete the ZIP file.', 'error')
        return redirect(url_for('student.project_submission'))

    success, message = Project.delete_zip_file(project_id)
    flash(message, 'success' if success else 'info' if "No ZIP file" in message else 'error')
    return redirect(url_for('student.project_submission'))

@student_bp.route('/download_template/<file_id>')
@login_required
def download_template(file_id):
    """
    Allows students to download template files.  This is analogous to the
    faculty version.

    Args:
        file_id (str): The ID of the template file to download.

    Returns:
        A Flask Response object containing the file, or a redirect with an error.
    """
    file_data = TemplateFile.get(file_id)  # Use TemplateFile.get
    if file_data:
        filepath = file_data.filepath
        filename = file_data.filename
        print(f"Attempting to download file from: {filepath}")
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
            return redirect(url_for('student.dashboard'))  # Redirect to student dashboard
    else:
        flash('File record not found.', 'error')
        return redirect(url_for('student.dashboard'))  # Redirect to student dashboard

@student_bp.route('/download_zip/<zip_file_id>')
@login_required
def download_zip(zip_file_id):
    """
    Allows students to download submitted zip files.

    Args:
        zip_file_id (str): The ID of the zip file to download (which is the ObjectId of the project).

    Returns:
        A Flask Response object containing the file, or a redirect with an error.
    """
    project = Project.get_by_id(zip_file_id)
    if project:
        filepath = project['zip_file_id']
        filename = os.path.basename(filepath)
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                file_content = f.read()
            return Response(
                file_content,
                mimetype='application/zip',
                headers={'Content-Disposition': f'attachment; filename={filename}'}
            )
        else:
            flash('Zip file not found on server.', 'error')
            return redirect(url_for('student.dashboard'))
    else:
        flash('Project record not found.', 'error')
        return redirect(url_for('student.dashboard'))
