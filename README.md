# Laptop-1: Admin Dashboard System

## Overview
This is the administrative dashboard for the Advanced Multiple Facial Recognition Attendance Management System. It provides interfaces for student registration, attendance reporting, and system management.

## Features
- Secure admin login
- Student registration with facial data capture
- Attendance reports by stream (MCA, MBA, BVoc.IT)
- Real-time attendance analytics
- System status monitoring
- Firebase integration for data synchronization

## Installation

1. Install Python 3.8 or higher
2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Configure Firebase:
   - Replace the Firebase configuration in app.py with your project details
   - Set up Firebase Realtime Database
   - Configure Firebase Authentication

4. Run the application:
```bash
python app.py
```

## Usage

1. Access the application at http://localhost:5000
2. Login with admin credentials (default: admin/admin123)
3. Use the dashboard to manage students and view reports

## Security Notes
- Change the default admin credentials in production
- Update the Flask secret key
- Configure proper Firebase security rules
- Use HTTPS in production environment

## File Structure
- `app.py` - Main Flask application
- `templates/` - HTML templates
- `static/` - CSS, JavaScript, and uploaded files
- `requirements.txt` - Python dependencies
