import os
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import pyrebase
import cv2
import numpy as np
import base64
from werkzeug.utils import secure_filename
import face_recognition
# import { initializeApp } from "firebase/app";
# import { getAnalytics } from "firebase/analytics";

app = Flask(__name__)
app.secret_key = 'your_secret_key_change_this'

# Firebase configuration
firebase_config = {
    "apiKey": "AIzaSyDFXmc1RF6pddkGK7-16P5xijRskArcE_s",
    "authDomain": "facial-attendance-system-5be26.firebaseapp.com",
    "databaseURL": "https://facial-attendance-system-5be26-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "facial-attendance-system-5be26",
    "storageBucket": "facial-attendance-system-5be26.appspot.com",
    "messagingSenderId": "1001208569305",
    "appId": "1:1001208569305:web:65ce94e8959a3576bbcdc8"
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        # Simple admin authentication (in production, use proper authentication)
        if username == 'admin' and password == 'admin123':
            session['user'] = username
            return jsonify({'success': True, 'message': 'Login successful'})
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'})

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/students', methods=['GET', 'POST'])
@login_required
def handle_students():
    if request.method == 'POST':
        try:
            data = request.get_json()
            student_id = data.get('id')

            # Process and store face encoding if image provided
            if 'photo_data' in data:
                photo_data = data['photo_data']
                # Remove data URL prefix
                photo_data = photo_data.split(',')[1]
                photo_bytes = base64.b64decode(photo_data)

                # Save photo
                photo_filename = f"{student_id}.jpg"
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_filename)
                with open(photo_path, 'wb') as f:
                    f.write(photo_bytes)

                # Generate face encoding
                image = face_recognition.load_image_file(photo_path)
                face_encodings = face_recognition.face_encodings(image)

                if face_encodings:
                    encoding_list = face_encodings[0].tolist()
                    data['face_encoding'] = encoding_list
                    data['photo_path'] = photo_filename

            # Save to Firebase
            db.child("students").child(student_id).set(data)
            return jsonify({'success': True, 'message': 'Student registered successfully'})

        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})

    else:
        try:
            students = db.child("students").get().val()
            if not isinstance(students, dict):
                students = {}
            return jsonify(students)
        except:
            return jsonify({})

@app.route('/api/attendance')
@login_required
def get_attendance():
    try:
        attendance = db.child("attendance").get().val()
        return jsonify(attendance or {})
    except:
        return jsonify({})

@app.route('/api/attendance/report')
@login_required
def get_attendance_report():
    try:
        stream = request.args.get('stream')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        attendance = db.child("attendance").get().val() or {}
        students = db.child("students").get().val() or {}

        # Filter attendance based on parameters
        filtered_data = []
        if isinstance(attendance, dict):
            attendance_iter = attendance.items()
        elif isinstance(attendance, list):
            attendance_iter = enumerate(attendance)
        else:
            attendance_iter = []

        for date, records in attendance_iter:
            if start_date and str(date) < str(start_date):
                continue
            if end_date and str(date) > str(end_date):
                continue

            if isinstance(records, dict):
                records_iter = records.items()
            elif isinstance(records, list):
                records_iter = enumerate(records)
            else:
                records_iter = []

            for student_id, lectures in records_iter:
                if isinstance(students, dict):
                    student = students.get(str(student_id), {})
                elif isinstance(students, list):
                    try:
                        student = students[int(student_id)]
                    except (ValueError, IndexError, TypeError):
                        student = {}
                else:
                    student = {}

                if stream and student.get('stream', '') != stream:
                    continue

                filtered_data.append({
                    'date': date,
                    'student_id': student_id,
                    'student_name': student.get('name', 'Unknown'),
                    'stream': student.get('stream', ''),
                    'lectures': lectures
                })

        return jsonify(filtered_data)
    except Exception as e:
        return jsonify([])

@app.route('/api/system-status')
@login_required
def system_status():
    try:
        # Check connection to Firebase
        db.child("system").child("laptop1_status").set({
            "status": "connected",
            "last_update": datetime.now().isoformat()
        })

        # Get Laptop-2 status
        laptop2_status = db.child("system").child("laptop2_status").get().val()

        # Handle laptop2_status type
        if isinstance(laptop2_status, dict):
            laptop2_status_value = laptop2_status.get('status', 'Disconnected')
        elif isinstance(laptop2_status, list) and len(laptop2_status) > 0:
            laptop2_status_value = laptop2_status[0] if isinstance(laptop2_status[0], str) else 'Disconnected'
        else:
            laptop2_status_value = 'Disconnected'

        return jsonify({
            'laptop1': 'Connected',
            'laptop2': laptop2_status_value,
            'firebase': 'Connected',
            'last_sync': datetime.now().isoformat()
        })
    except:
        return jsonify({
            'laptop1': 'Connected',
            'laptop2': 'Unknown',
            'firebase': 'Disconnected',
            'last_sync': None
        })

@app.route('/api/festivals')
@login_required
def get_festivals():
    try:
        festivals = db.child("festivals").get().val()
        if not isinstance(festivals, dict):
            festivals = {}
        return jsonify(festivals)
    except Exception as e:
        return jsonify({})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
