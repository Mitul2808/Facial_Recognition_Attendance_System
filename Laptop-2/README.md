# Laptop-2: Facial Recognition Camera System

## Overview
This is the camera system for the Advanced Multiple Facial Recognition Attendance Management System. It handles automatic face detection, recognition, and attendance marking.

## Features
- Automatic camera activation based on motion detection
- Real-time facial recognition with 90%+ accuracy
- Automatic attendance marking during lecture intervals
- Firebase synchronization with Laptop-1
- Continuous background processing

## Installation

1. Install Python 3.8 or higher
2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Configure Firebase:
   - Replace the Firebase configuration in face_recognition_system.py with your project details
   - Ensure Firebase Realtime Database is set up and accessible

4. Connect camera:
   - Ensure webcam is connected and working
   - Test camera access with other applications if needed

## Usage

1. Run the face recognition system:
```bash
python face_recognition_system.py
```

2. The system will:
   - Automatically detect motion and activate camera
   - Recognize faces of registered students
   - Mark attendance during lecture intervals
   - Sync data with Firebase in real-time

3. Press 'q' to quit the application

## Lecture Schedule
The system automatically marks attendance during these intervals:
- Lecture 1: 8:30 AM - 8:45 AM
- Lecture 2: 9:25 AM - 9:40 AM  
- Lecture 3: 10:20 AM - 10:35 AM
- Lecture 4: 11:40 AM - 11:55 AM
- Lecture 5: 12:25 PM - 12:40 PM

## Configuration
- Motion sensitivity can be adjusted via `motion_threshold`
- Camera timeout can be modified via `no_motion_timeout`
- Recognition confidence threshold is set at 60%

## Troubleshooting
- Ensure camera permissions are granted
- Check Firebase configuration and network connectivity
- Verify that student face encodings are available in the database
- Monitor logs for error messages and system status
