# ProjectEduHub

ProjectEduHub is a web-based platform for managing educational projects, facilitating collaboration between students, faculty, and administrators.

## Features

- User Authentication (Students, Faculty, Admin)
- Project Submission and Management
- Team Creation and Management
- File Upload System
- Dashboard for Different User Roles
- Email Notifications

## Prerequisites

- Python 3.8 or higher
- MongoDB 4.4 or higher
- Git

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ProjectEduHub.git
cd ProjectEduHub
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
- Copy the `.env.example` file to `.env`
- Update the values in `.env` with your configuration:
  - Set your MongoDB URI
  - Configure email settings
  - Update admin credentials
  - Set a secure SECRET_KEY

5. Initialize the database:
- Make sure MongoDB is running on your system
- The application will create necessary collections on first run

## Running the Application

1. Start the Flask application:
```bash
flask run
```

2. Access the application:
- Open your web browser and navigate to `http://localhost:5000`
- Default admin credentials:
  - Username: admin
  - Password: (as specified in your .env file)

## Project Structure

```
ProjectEduHub/
├── backend/
│   ├── app.py           # Main application file
│   ├── database.py      # Database configuration
│   ├── models.py        # Data models
│   └── routes/          # Route handlers
├── templates/           # HTML templates
├── student_uploads/     # File upload directory
├── requirements.txt     # Python dependencies
├── .env                # Environment variables
└── README.md           # This file
```

## Security Notes

1. Never commit your `.env` file to version control
2. Change all default passwords in production
3. Use strong, unique passwords for admin accounts
4. Keep MongoDB and Python packages updated
5. Regularly backup your database

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
