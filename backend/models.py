from flask_login import UserMixin
from database import mongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

import csv
import jinja2
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import current_app  # To access Flask app configurations
from flask_login import UserMixin
from database import mongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
import secrets
import string
import os

def generate_temporary_password(length=12):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(length))

def send_credentials_email(to_email, username, password, role):
    try:
        msg = MIMEMultipart()
        msg['From'] = current_app.config['MAIL_DEFAULT_SENDER'] # Get sender from Flask config
        msg['To'] = to_email
        msg['Subject'] = f'Your {role.capitalize()} Account Credentials for ProjectEduHub'

        body = f"""
        Hello {username},

        Your {role.capitalize()} account has been created on AcadProjectHub with the following credentials:

        Username: {username}
        Password: {password}

        Please log in to https://rdsj78xb-3000.inc1.devtunnels.ms/auth/login and change your password as soon as possible for security reasons.

        Thank you,
        The ProjectEduHub Team
        """
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']) as server:
            server.starttls()
            server.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
            server.sendmail(current_app.config['MAIL_DEFAULT_SENDER'], to_email, msg.as_string())
        print(f"Credentials email sent to {to_email} for {role}")

    except Exception as e:
        print(f"Error sending credentials email to {to_email} for {role}: {e}")


# from database import mongo
# from bson.objectid import ObjectId

# class Team:
#     @staticmethod
#     def create(name,team_lead_id, faculty_id,leader_roll_no):
#         return mongo.db.teams.insert_one({'name': name,'team_lead':team_lead_id, 'faculty_id': ObjectId(faculty_id),'team_lead_roll':leader_roll_no}).inserted_id

#     @staticmethod
#     def get_all(faculty_id):
#         teams = list(mongo.db.teams.find({'faculty_id': ObjectId(faculty_id)}))
#         for team in teams:
#             team['_id'] = str(team['_id'])
#         return teams

#     @staticmethod
#     def get(team_id):
#         team = mongo.db.teams.find_one({'_id': ObjectId(team_id)})
#         if team:
#             team['_id'] = str(team['_id'])
#         return team

#     @staticmethod
#     def update_faculty_id(team_id, new_faculty_id):
#         """
#         Updates the faculty_id for a given team.

#         Args:
#             team_id (str): The ID of the team to update.
#             new_faculty_id (str): The new faculty ID.
#         """
#         print(f"Updating faculty_id for team {team_id} to {new_faculty_id}")
#         mongo.db.teams.update_one(
#             {"_id": ObjectId(team_id)},  # Filter by team ID
#             {"$set": {"faculty_id": new_faculty_id}}  # Set the new faculty ID
#         )

#     @staticmethod
#     def delete(team_id):
#         mongo.db.team_leaders.delete_many({'team_id': ObjectId(team_id)})
#         mongo.db.submissions.delete_many({'team_id': ObjectId(team_id)})
#         mongo.db.teams.delete_one({'_id': ObjectId(team_id)})

#     @staticmethod
#     def get_teams_by_student(team_lead_id):  # New method
#         teams = mongo.db.teams.find({'team_lead': team_lead_id})
#           # Adjust query as needed
#         return teams

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database import mongo
from bson.objectid import ObjectId

class User(UserMixin):
    def __init__(self, id, username, email, password, role, name=None, faculty_roll_no=None):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.role = role
        self.name = name
        self.faculty_roll_no = faculty_roll_no

    @staticmethod
    def get(identifier):
        try:
            if isinstance(identifier, str):
                if ObjectId.is_valid(identifier):
                    user_data = mongo.db.users.find_one({'_id': ObjectId(identifier)})
                else:
                    user_data = mongo.db.users.find_one({'username': identifier})
            else:
                user_data = mongo.db.users.find_one({'username': identifier})

            if user_data:
                return User(
                    id=str(user_data['_id']),
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    role=user_data['role'],
                    name=user_data.get('name'),
                    faculty_roll_no=user_data.get('faculty_roll_no')
                )
        except Exception as e:
            print(f"Error in User.get: {e}")
        return None

    @staticmethod
    def get_by_username(username):
        user = mongo.db.users.find_one({'username': username})
        if not user:
            return None
        return User(
            id=str(user['_id']),
            username=user['username'],
            email=user['email'],
            password=user['password'],
            role=user['role'],
            name=user.get('name'),
            faculty_roll_no=user.get('faculty_roll_no')
        )
    
    @staticmethod
    def get_by_email(email):
        user = mongo.db.users.find_one({'email': email})
        if not user:
            return None
        return User(
            id=str(user['_id']),
            username=user['username'],
            email=user['email'],
            password=user['password'],
            role=user['role'],
            name=user.get('name'),
            faculty_roll_no=user.get('faculty_roll_no')
        )

    @staticmethod
    def create(username, email, password=None, role=None, name=None, faculty_roll_no=None):
        if not password:
            password = generate_temporary_password()
            hashed_password = generate_password_hash(password)
        else:
            hashed_password = generate_password_hash(password)

        result = mongo.db.users.insert_one({
            'username': username,
            'email': email,
            'password': hashed_password,
            'role': role,
            'name': name,
            'faculty_roll_no': faculty_roll_no
        })
        user_id = str(result.inserted_id)
        user = User.get(user_id) # Retrieve the created user

        if role == 'faculty':
            send_credentials_email(email, username, password, role)
            # print(f"Credentials email sent to {email} for {role}")

        return user_id

    @staticmethod
    def delete(user_id):
        mongo.db.users.delete_one({'_id': ObjectId(user_id)})

    @staticmethod
    def get_all_faculty():
        faculties = mongo.db.users.find({'role': 'faculty'})
        return [User(
            id=str(faculty['_id']),
            username=faculty['username'],
            email=faculty['email'],
            password=faculty['password'],
            role=faculty['role'],
            name=faculty.get('name'),
            faculty_roll_no=faculty.get('faculty_roll_no')
        ) for faculty in faculties]

    @staticmethod
    def get_all_students():
        students = mongo.db.users.find({'role': 'student'})
        return [User(
            id=str(student['_id']),
            username=student['username'],
            email=student['email'],
            password=student['password'],
            role=student['role']
        ) for student in students]


class Team(object): # Inheriting from object for older Python versions
    @staticmethod
    def create(name,team_lead_id, faculty_id,leader_roll_no):
        return mongo.db.teams.insert_one({'name': name,'team_lead':team_lead_id, 'faculty_id': ObjectId(faculty_id),'team_lead_roll':leader_roll_no}).inserted_id

    @staticmethod
    def get_all(faculty_id):
        teams = list(mongo.db.teams.find({'faculty_id': ObjectId(faculty_id)}))
        for team in teams:
            team['_id'] = str(team['_id'])
        return teams

    @staticmethod
    def get_by_team_lead(team_lead_id):
        teams = list(mongo.db.teams.find({'team_lead': team_lead_id}))
        for team in teams:
            team['_id'] = str(team['_id'])
        return teams

    @staticmethod
    def get(team_id):
        team = mongo.db.teams.find_one({'_id': ObjectId(team_id)})
        if team:
            team['_id'] = str(team['_id'])
        return team

    @staticmethod
    def update_faculty_id(team_id, new_faculty_id):
        print(f"Updating faculty_id for team {team_id} to {new_faculty_id}")
        mongo.db.teams.update_one(
            {"_id": ObjectId(team_id)},
            {"$set": {"faculty_id": new_faculty_id}}
        )

    @staticmethod
    def delete(team_id):
        mongo.db.team_leaders.delete_many({'team_id': ObjectId(team_id)})
        mongo.db.submissions.delete_many({'team_id': ObjectId(team_id)})
        mongo.db.teams.delete_one({'_id': ObjectId(team_id)})

    @staticmethod
    def get_teams_by_student(team_lead_id):
        print(f"Getting teams for team lead ID: {team_lead_id}")
        teams = list(mongo.db.teams.find({'team_lead': ObjectId(team_lead_id)}))
        return teams

class TeamLeader(UserMixin):
    def __init__(self, id, username, email, password, role, roll_no): # Ensure id is first
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.role = role
        self.roll_no = roll_no

    def get_id(self):
        return str(self.id)

    @staticmethod
    def get_tl(identifier):
        try:
            if isinstance(identifier, str):
                if ObjectId.is_valid(identifier):
                    user_data = mongo.db.team_leaders.find_one({'_id': ObjectId(identifier)})
                else:
                    user_data = mongo.db.team_leaders.find_one({'username': identifier})
            else:
                user_data = mongo.db.team_leaders.find_one({'username': identifier})

            if user_data:
                return TeamLeader(
                    id=str(user_data['_id']), # Ensure ID is converted to string
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    role=user_data['role'],
                    roll_no=user_data.get('roll_no')
                )
        except Exception as e:
            print(f"Error in TeamLeader.get_tl: {e}")
        return None


    @staticmethod
    def get_by_email(email):
        user_data = mongo.db.team_leaders.find_one({'email': email})
        if not user_data:
            return None
        return TeamLeader(
            id=str(user_data['_id']),
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            role=user_data['role'],
            roll_no=user_data.get('roll_no')
        )  
    
    @staticmethod
    def create(roll_no, name, branch, section, email, username, password=None):
        if not password:
            password = generate_temporary_password()
            hashed_password = generate_password_hash(password)
        else:
            hashed_password = generate_password_hash(password)

        team_leader = mongo.db.team_leaders.insert_one({
            'roll_no': roll_no,
            'name': name,
            'branch': branch,
            'section': section,
            'email': email,
            'role': 'team_leader',
            'username': username,
            'password': hashed_password
        })
        team_leader_id = str(team_leader.inserted_id)
        team_leader_obj = TeamLeader.get_tl(team_leader_id) # Retrieve the created team leader

        send_credentials_email(email, username, password, 'team_leader')

        return team_leader_id

    @staticmethod
    def update(project_id, title=None, description=None, team_members=None,
               category=None, guide_name=None, github_link=None, drive_link=None,
               zip_file_id=None, screenshot_ids=None):
        update_data = {}
        if title is not None:
            update_data['title'] = title
        if description is not None:
            update_data['description'] = description
        if team_members is not None:
            update_data['team_members'] = team_members
        if category is not None:
            update_data['category'] = category
        if guide_name is not None:
            update_data['guide_name'] = guide_name
        if github_link is not None:
            update_data['github_link'] = github_link
        if drive_link is not None:
            update_data['drive_link'] = drive_link
        if zip_file_id is not None:
            update_data['zip_file_id'] = zip_file_id
        if screenshot_ids is not None:
            update_data['screenshot_ids'] = screenshot_ids

        if update_data:
            mongo.db.projects.update_one({'_id': ObjectId(project_id)}, {'$set': update_data})
            return True
        return False

    @staticmethod
    def get(team_leader_id):
        team_lead = mongo.db.team_leaders.find_one({'_id': ObjectId(team_leader_id)})
        if team_lead:
            team_lead['_id'] = str(team_lead['_id'])
        return team_lead

    @staticmethod
    def get_by_roll_no(roll_no):
        team_data = mongo.db.team_leaders.find_one({'roll_no': roll_no})
        if team_data:
            return TeamLeader(
                id=str(team_data.get('_id')),
                username=team_data.get('username'),
                email=team_data.get('email'),
                password=team_data.get('password'),
                role=team_data.get('role'),
                roll_no=team_data.get('roll_no')
            )
        return None

    @staticmethod
    def get_all_by_team(team_id):
        leaders = list(mongo.db.team_leaders.find({'team_id': ObjectId(team_id)}))
        for leader in leaders:
            leader['_id'] = str(leader['_id'])
        return leaders

    @staticmethod
    def delete(submission_id):
        mongo.db.team_leaders.delete_one({'_id': ObjectId(submission_id)})
# class Submission:
#     @staticmethod
#     def get_all(team_id):
#         submissions = list(mongo.db.submissions.find({'team_id': ObjectId(team_id)}))
#         for submission in submissions:
#             submission['_id'] = str(submission['_id'])
#         return submissions

#     @staticmethod
#     def get(submission_id):
#         submission = mongo.db.submissions.find_one({'_id': ObjectId(submission_id)})
#         if submission:
#             submission['_id'] = str(submission['_id'])
#         return submission

#     @staticmethod
#     def give_marks(submission_id, marks):
#         mongo.db.submissions.update_one({'_id': ObjectId(submission_id)}, {'$set': {'marks': marks}})
class Deadline:
    @staticmethod
    def create(title, date, faculty_id):
        result = mongo.db.deadlines.insert_one({
            'title': title,
            'date': date,
            'faculty_id': ObjectId(faculty_id)
        })
        return str(result.inserted_id)

    @staticmethod
    def get_all(faculty_id):
        deadlines = list(mongo.db.deadlines.find({'faculty_id': ObjectId(faculty_id)}))
        for deadline in deadlines:
            deadline['_id'] = str(deadline['_id'])
        return deadlines
    
    @staticmethod
    def delete_by_faculty_id(faculty_id):
        mongo.db.deadlines.delete_many({"faculty_id": ObjectId(faculty_id)})


from database import mongo  # Your MongoDB connection
from bson.objectid import ObjectId

import os
from bson.objectid import ObjectId
from database import mongo  # Assuming this is where your mongo client is

class TemplateFile:
    @staticmethod
    def create(filename, filepath, faculty_id):
        try:
            result = mongo.db["template_files"].insert_one({'filename': filename,'filepath': filepath,'faculty_id': ObjectId(faculty_id)
            })
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error creating template file record: {e}")
            return None  # Or raise an exception

    @staticmethod
    def get_all(faculty_id):
        try:
            files = list(mongo.db["template_files"].find({'faculty_id': ObjectId(faculty_id)}))
            for file in files:
                file['_id'] = str(file['_id'])
            return files
        except Exception as e:
            print(f"Error getting all template files: {e}")
            return []  # Or raise an exception

    @staticmethod
    def delete(file_id):
        # print(f"Deleting file with ID: {file_id}")
        try:
            file_data = mongo.db["template_files"].find_one({'_id': ObjectId(file_id)})
            # print(f"File data: {file_data}")
            if file_data:
                filepath = file_data['filepath']
                print(f"Deleting file at: {filepath}")
                if os.path.exists(filepath):
                    os.remove(filepath)
                mongo.db["db.template_files"].delete_one({'_id': ObjectId(file_id)})
                return True
            else:
                print(f"Template file record not found for id: {file_id}")
                return False
        except FileNotFoundError:
            print(f"File not found: {filepath}")
            return False
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
        
    @staticmethod
    def delete_by_faculty_id(faculty_id):
        mongo.db.template_files.delete_many({"faculty_id": ObjectId(faculty_id)})

    
    @staticmethod
    def get(file_id):
        print(file_id)
        file_data = mongo.db["template_files"].find_one({'_id': ObjectId(file_id)})
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
        else:
            flash('File record not found.', 'error')
        
        
class Announcement:
    @staticmethod
    def create(title, content, faculty_id):
        result = mongo.db.announcements.insert_one({
            'title': title,
            'content': content,
            'faculty_id': ObjectId(faculty_id)
        })
        return str(result.inserted_id)

    @staticmethod
    def get_all(faculty_id):
        announcements = list(mongo.db.announcements.find({'faculty_id': ObjectId(faculty_id)}))
        for announcement in announcements:
            announcement['_id'] = str(announcement['_id'])
        return announcements
    @staticmethod
    def delete_by_faculty_id(faculty_id):
        mongo.db.announcements.delete_many({"faculty_id": ObjectId(faculty_id)})




class Project:

    def __init__(self, title, description, team_lead_roll_no, team_lead_name, team_members, category, guide_name, github_link, drive_link, zip_file_id, screenshot_ids):
        self.title = title
        self.description = description
        self.team_lead_roll_no = team_lead_roll_no
        self.team_lead_name = team_lead_name
        self.team_members = team_members
        self.category = category
        self.guide_name = guide_name
        self.github_link = github_link
        self.drive_link = drive_link
        self.zip_file_id = zip_file_id
        self.screenshot_ids = screenshot_ids
        self.id = None
    def get_id(self):
        return str(self.id)
    @staticmethod
    def create(title, description, team_lead_roll_no, team_lead_name, team_members, category, guide_name, github_link, drive_link, zip_file_id, screenshot_ids):
        project = mongo.db.projects.insert_one({
            'title': title,
            'description': str(description),
            'team_lead_roll_no': team_lead_roll_no,
            'team_lead_name': team_lead_name,
            'team_members': team_members,  # Store list of members
            'category': category,
            'guide_name': guide_name,
            'github_link': github_link,
            'drive_link': drive_link,
            'zip_file_id': zip_file_id,
            'screenshot_ids': screenshot_ids
        })
        return str(project.inserted_id)





    @staticmethod
    def get_by_team_lead_roll_no(team_lead_roll_no):
        project = mongo.db.projects.find_one({'team_lead_roll_no': team_lead_roll_no})
        # if project:
        #     project['_id'] = str(project['_id'])
        return project



    @staticmethod
    def update(project_id, title=None, description=None, team_members=None,
               category=None, guide_name=None, github_link=None, drive_link=None,
               zip_file_id=None, screenshot_ids=None):  # Added zip_file_id and screenshot_ids to update
        update_data = {}
        if title:
            update_data['title'] = title
        if description:
            update_data['description'] = description
        if team_members:
            update_data['team_members'] = team_members
        if category:
            update_data['category'] = category
        if guide_name:
            update_data['guide_name'] = guide_name
        if github_link:
            update_data['github_link'] = github_link
        if drive_link:
            update_data['drive_link'] = drive_link
        if zip_file_id:
            update_data['zip_file_id'] = zip_file_id
        if screenshot_ids:
            update_data['screenshot_ids'] = screenshot_ids


        if update_data:
            mongo.db.projects.update_one({'_id': ObjectId(project_id)}, {'$set': update_data})
            return True
        return False


    @staticmethod
    def get_by_id(project_id):
        project = mongo.db.projects.find_one({'_id': ObjectId(project_id)})
        if project:
            project['_id'] = str(project['_id'])
        return project

    @staticmethod
    def get_all():
        projects = list(mongo.db.projects.find())
        for project in projects:
            project['_id'] = str(project['_id'])
        return projects


    @staticmethod
    def delete(project_id):
        mongo.db.projects.delete_one({'_id': ObjectId(project_id)})
        return True
    @staticmethod
    def delete_media(project_id, filepath):
        """
        Deletes a specific media file associated with a project
        and removes its reference from the database.
        """
        try:
            project_oid = ObjectId(project_id)
        except Exception:
            return False, "Invalid project ID"

        project_data = mongo.db.projects.find_one({'_id': project_oid})
        if not project_data:
            return False, "Project not found"

        if filepath in project_data.get('screenshot_ids', []):
            update_result = mongo.db.projects.update_one(
                {'_id': project_oid},
                {'$pull': {'screenshot_ids': filepath}}
            )
            if update_result.modified_count > 0:
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    return True, "Media deleted successfully"
                except OSError as e:
                    print(f"Error deleting file {filepath}: {e}")
                    return True, "Media reference removed, but file deletion failed"
            else:
                return False, "Filepath not found in project's media list"
        else:
            return False, "Filepath not associated with this project"

    @staticmethod
    def delete_zip_file(project_id):
        """
        Deletes the ZIP file associated with a project and removes its reference.
        """
        try:
            project_oid = ObjectId(project_id)
        except Exception:
            return False, "Invalid project ID"

        project_data = mongo.db.projects.find_one({'_id': project_oid})
        if not project_data:
            return False, "Project not found"

        zip_file_path = project_data.get('zip_file_id')
        if zip_file_path:
            update_result = mongo.db.projects.update_one(
                {'_id': project_oid},
                {'$set': {'zip_file_id': None}}
            )
            if update_result.modified_count > 0:
                try:
                    if os.path.exists(zip_file_path):
                        os.remove(zip_file_path)
                    return True, "ZIP file deleted successfully"
                except OSError as e:
                    print(f"Error deleting ZIP file {zip_file_path}: {e}")
                    return True, "ZIP file reference removed, but file deletion failed"
            else:
                return False, "No ZIP file ID found for this project"
        else:
            return True, "No ZIP file associated with this project"
     
        
class Submission:
    def __init__(self, team_id,  marks=None, student_feedback=None, id=None): # Added student_feedback
        self.team_id = team_id
        self.marks = marks
        self.student_feedback = student_feedback # Added student_feedback
        self.id = id

    @staticmethod
    def get_all():
        submissions = mongo.db.submissions.find()
        for submission in submissions:
            submission['_id'] = str(submission['_id'])
            submission['team_id'] = str(submission['team_id'])
        return submissions

    @staticmethod
    def get_by_team_id(team_id):
        submissions = mongo.db.submissions.find_one({'team_id': ObjectId(team_id)})
        # for submission in submissions:
        #     submission['_id'] = str(submission['_id'])
        return submissions

    @staticmethod
    def get(submission_id):
        submission = mongo.db.submissions.find_one({'_id': ObjectId(submission_id)})
        if submission:
            submission['_id'] = str(submission['_id'])
        return submission

    @staticmethod
    def create(team_id):
        from datetime import datetime
        submission = mongo.db.submissions.insert_one({
            'team_id': ObjectId(team_id),
            'marks': None,
            'student_feedback': {},
            'overall_feedback': None,
        })
        return str(submission.inserted_id)

    @staticmethod
    def give_marks(submission_id, marks, student_feedback=None,overall_feedback=None): # Changed feedback to student_feedback
        update_data = {'marks': marks}
        if student_feedback is not None:
            update_data['student_feedback'] = student_feedback
        if overall_feedback is not None:
            update_data['overall_feedback'] = overall_feedback
        mongo.db.submissions.update_one({'_id': ObjectId(submission_id)}, {'$set': update_data})

    @staticmethod
    def delete(submission_id):
        mongo.db.submissions.delete_one({'_id': ObjectId(submission_id)})


