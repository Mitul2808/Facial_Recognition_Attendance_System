# Configuration file for Laptop-2 Camera System

# Firebase Configuration
firebase_config = {
    "apiKey": "AIzaSyDFXmc1RF6pddkGK7-16P5xijRskArcE_s",
    "authDomain": "facial-attendance-system-5be26.firebaseapp.com",
    "databaseURL": "https://facial-attendance-system-5be26-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "facial-attendance-system-5be26",
    "storageBucket": "facial-attendance-system-5be26.appspot.com",
    "messagingSenderId": "1001208569305",
    "appId": "1:1001208569305:web:65ce94e8959a3576bbcdc8"
}

# Camera Settings
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_INDEX = 0  # Change if using external camera

# Motion Detection Settings
MOTION_THRESHOLD = 5000
NO_MOTION_TIMEOUT = 30  # seconds

# Recognition Settings  
RECOGNITION_CONFIDENCE_THRESHOLD = 0.6  # 60%
PROCESSING_SCALE = 0.25  # Scale down for faster processing

# Lecture Schedule
LECTURE_SCHEDULE = {
    1: {"start": "08:30", "end": "08:45"},
    2: {"start": "09:25", "end": "09:40"},
    3: {"start": "10:20", "end": "10:35"},
    4: {"start": "11:40", "end": "11:55"},
    5: {"start": "12:25", "end": "12:40"}
}

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
