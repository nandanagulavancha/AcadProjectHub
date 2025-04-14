ProjectEduHubDescriptionProjectEduHub is a web application designed to facilitate project management and collaboration within an educational institution. It provides tools for faculty to manage student teams, assignments, and deadlines, while also enabling students to collaborate effectively on their projects.  This project was created by Nandanagulavancha.You can find the project repository here: https://github.com/nandanagulavancha/ProjectEduHubFeaturesFaculty Features:Manage faculty accountsCreate and delete faculty membersView a dashboard of teams and deadlinesCreate student teams and team leadersDelete teams and reassign studentsView team project detailsAssign marks and provide feedback to teamsSet deadlines for project submissionsPost announcements to studentsUpload and download template filesDownload submitted project zip filesStudent Features:View their team and team membersView project detailsView deadlines and announcementsDownload template filesTechnologies UsedPythonFlask frameworkMongoDB databaseHTMLCSSJavaScriptBootstrapInstallationClone the repository:git clone https://github.com/nandanagulavancha/ProjectEduHub.git
Navigate to the project directory:cd ProjectEduHub
Set up a virtual environment (recommended):python3 -m venv venv
source venv/bin/activate  # On Linux/macOS
venv\\Scripts\\activate  # On Windows
Install the dependencies:pip install -r requirements.txt
Configure the database:Ensure you have MongoDB installed and running.Update the MongoDB connection URI in database.py if necessary.  This will involve setting up your MongoDB instance and providing the correct connection details.Run the application:python backend/app.py
UsageFaculty:Log in with your faculty credentials.Use the dashboard to manage teams, deadlines, and announcements.Create teams and assign projects.Upload template files for students.Download project submissions.Students:Log in with your student credentials.View your team and project details.Submit your projects before the deadline.Download template files.Directory Structure├── app.py          # Main application file
├── database.py     # MongoDB connection
├── models.py       # Data models
├── routes
│   ├── admin.py    # Admin routes
│   ├── faculty.py  # Faculty routes
│   ├── student.py  # Student routes
├── templates       # HTML templates
├── uploads         # Directory for uploaded files
├── venv            # Virtual environment (optional)
├── requirements.txt # Project dependencies
└── README.md       # Project documentation
ContributingFork the repository.Create a new branch for your feature or bug fix.Commit your changes.Push to the branch.Submit a pull request.License[Specify the license for your project]AuthorNandanagulavancha
