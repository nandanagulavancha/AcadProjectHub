# ProjectEduHub

**Description**

ProjectEduHub is a web application designed to facilitate project management and collaboration within an educational institution. It provides tools for faculty to manage student teams, assignments, and deadlines, while also enabling students to collaborate effectively on their projects.

You can find the project repository here: [https://github.com/nandanagulavancha/ProjectEduHub](https://github.com/nandanagulavancha/ProjectEduHub)

## Features

**Faculty Features:**

* Manage faculty accounts
* Create and delete faculty members
* View a dashboard of teams and deadlines
* Create student teams and team leaders
* Delete teams and reassign students
* View team project details
* Assign marks and provide feedback to teams
* Set deadlines for project submissions
* Post announcements to students
* Upload and download template files
* Download submitted project zip files

**Student Features:**

* View their team and team members
* View project details
* View deadlines and announcements
* Download template files

**Admin Features:**

* The application automatically creates a default admin user on first run (username: "admin", email: "admin1@example.com", password: "admin"). **Note:** The password is "admin" and is hashed in the database. You should change this password immediately after the initial login.

## Technologies Used

* Python
* Flask framework
* MongoDB database
* HTML
* CSS
* JavaScript
* Bootstrap

## Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/nandanagulavancha/ProjectEduHub.git](https://github.com/nandanagulavancha/ProjectEduHub.git)
    ```

2.  **Navigate to the project directory:**
    ```bash
    cd ProjectEduHub
    ```

3.  **Set up a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate  # On Windows
    ```

4.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Configure the database:**
    * Ensure you have MongoDB installed and running.
    * The application is configured to use MongoDB at `mongodb://localhost:27017/ProjectEduHub` by default. If your MongoDB instance is running elsewhere, you will need to modify the `MONGO_URI` configuration in the `app.py` file.

6.  **Run the application:**
    ```bash
    python backend/app.py
    ```
    The application will automatically create a default admin user on the first run. The username is "admin", the email is "admin1@example.com", and the password is "admin". You should change this password immediately after logging in.

## Usage

**Admin:**

1.  Log in with the default admin credentials (username: "admin", password: "admin").
2.  Change the default admin password immediately.
3.  Use the admin interface to manage faculty and other administrative tasks.

**Faculty:**

1.  Log in with your faculty credentials.
2.  Use the dashboard to manage teams, deadlines, and announcements.
3.  Create teams and assign projects.
4.  Upload template files for students.
5.  Download project submissions.

**Students:**

1.  Log in with your student credentials.
2.  View your team and project details.
3.  Submit your projects before the deadline.
4.  Download template files.

**Note:** This application requires MongoDB to be installed and running on your system. Please ensure MongoDB is set up before running the application.
