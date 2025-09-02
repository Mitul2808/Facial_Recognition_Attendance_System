import cv2
import numpy as np
import face_recognition
import os
import json
import time
import threading
from datetime import datetime, timedelta
import pyrebase
from PIL import Image
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AttendanceSystem:
    def __init__(self):
        # Firebase configuration
        self.firebase_config = {
            "apiKey": "AIzaSyDFXmc1RF6pddkGK7-16P5xijRskArcE_s",
            "authDomain": "facial-attendance-system-5be26.firebaseapp.com",
            "databaseURL": "https://facial-attendance-system-5be26-default-rtdb.asia-southeast1.firebasedatabase.app",
            "projectId": "facial-attendance-system-5be26",
            "storageBucket": "facial-attendance-system-5be26.appspot.com",
            "messagingSenderId": "1001208569305",
            "appId": "1:1001208569305:web:65ce94e8959a3576bbcdc8"
        }

        # Initialize Firebase
        try:
            self.firebase = pyrebase.initialize_app(self.firebase_config)
            self.db = self.firebase.database()
            logger.info("Firebase initialized successfully")
        except Exception as e:
            logger.error(f"Firebase initialization failed: {e}")
            self.db = None

        # System parameters
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_ids = []
        self.motion_threshold = 5000
        self.no_motion_timeout = 5  # seconds
        self.last_motion_time = time.time()
        self.camera_active = False
        self.attendance_marked_today = set()

        # Lecture schedule
        self.lecture_schedule = {
            1: {"start": "08:30", "end": "09:25"},
            2: {"start": "09:25", "end": "10:20"},
            3: {"start": "10:20", "end": "11:15"},
            4: {"start": "11:40", "end": "12:35"},
            5: {"start": "12:35", "end": "13:30"},
        }

        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Load known faces
        self.load_known_faces()

        # Start background threads
        self.start_background_threads()

    def load_known_faces(self):
        """Load known faces from Firebase"""
        if not self.db:
            logger.error("Cannot load faces - Firebase not initialized")
            return

        try:
            students = self.db.child("students").get()
            if students.val():
                data = students.val()
                if isinstance(data, dict):
                    for student_id, student_data in data.items():
                        if 'face_encoding' in student_data:
                            encoding = np.array(student_data['face_encoding'])
                            self.known_face_encodings.append(encoding)
                            self.known_face_names.append(student_data.get('name', 'Unknown'))
                            self.known_face_ids.append(student_id)
                elif isinstance(data, list):
                    for idx, student_data in enumerate(data):
                        if student_data and 'face_encoding' in student_data:
                            encoding = np.array(student_data['face_encoding'])
                            self.known_face_encodings.append(encoding)
                            self.known_face_names.append(student_data.get('name', 'Unknown'))
                            self.known_face_ids.append(str(idx))

            logger.info(f"Loaded {len(self.known_face_encodings)} known faces")
        except Exception as e:
            logger.error(f"Error loading known faces: {e}")

    def detect_motion(self, frame1, frame2):
        """Detect motion between two frames"""
        # Convert to grayscale
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        # Calculate absolute difference
        diff = cv2.absdiff(gray1, gray2)

        # Apply threshold
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)

        # Calculate motion amount
        motion_amount = np.sum(thresh)

        return motion_amount > self.motion_threshold

    def get_current_lecture(self):
        """Get current lecture number based on time"""
        current_time = datetime.now().strftime("%H:%M")

        for lecture_num, times in self.lecture_schedule.items():
            if times["start"] <= current_time <= times["end"]:
                return lecture_num

        return None
        # return 1  # For testing purposes, always return lecture 1

    def mark_attendance(self, student_id, student_name, confidence):
        """Mark attendance for a student"""
        current_lecture = self.get_current_lecture()
        if not current_lecture:
            logger.info(f"Not in lecture time - attendance not marked for {student_name}")
            return False

        today = datetime.now().strftime("%Y-%m-%d")
        attendance_key = f"{student_id}_{today}_{current_lecture}"

        # Check if already marked for this lecture today
        if attendance_key in self.attendance_marked_today:
            return False

        try:
            # Update attendance in Firebase
            attendance_data = {
                "student_id": student_id,
                "student_name": student_name,
                "date": today,
                "lecture": current_lecture,
                "time": datetime.now().isoformat(),
                "confidence": float(confidence),
                "status": "Present"
            }

            if self.db:
                self.db.child("attendance").child(today).child(student_id).child(f"lecture{current_lecture}").set("Present")
                self.db.child("attendance_logs").push(attendance_data)

                # Update system status
                self.db.child("system").child("laptop2_status").set({
                    "status": "connected",
                    "last_update": datetime.now().isoformat(),
                    "last_recognition": f"{student_name} (Confidence: {confidence:.2f})"
                })

            self.attendance_marked_today.add(attendance_key)
            logger.info(f"Attendance marked for {student_name} in Lecture {current_lecture}")
            return True

        except Exception as e:
            logger.error(f"Error marking attendance: {e}")
            return False

    def process_frame(self, frame):
        """Process frame for face recognition"""
        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Find faces
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        face_confidences = []

        for face_encoding in face_encodings:
            # Compare with known faces
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)

            name = "Unknown"
            confidence = 0
            student_id = None

            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
                    student_id = self.known_face_ids[best_match_index]
                    confidence = 1 - face_distances[best_match_index]

                    # Mark attendance if confidence is high enough
                    if confidence > 0.1:  # 60% confidence threshold
                        self.mark_attendance(student_id, name, confidence)

            face_names.append(name)
            face_confidences.append(confidence)

        # Scale back up face locations
        face_locations = [(top*4, right*4, bottom*4, left*4) for (top, right, bottom, left) in face_locations]

        return face_locations, face_names, face_confidences

    def draw_results(self, frame, face_locations, face_names, face_confidences):
        """Draw recognition results on frame"""
        for (top, right, bottom, left), name, confidence in zip(face_locations, face_names, face_confidences):
            # Draw rectangle around face
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

            # Draw label
            label = f"{name}"
            if confidence > 0:
                label += f" ({confidence:.2f})"

            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            cv2.putText(frame, label, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

        # Add system info
        current_lecture = self.get_current_lecture()
        info_text = f"Lecture: {current_lecture if current_lecture else 'None'}"
        cv2.putText(frame, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        return frame

    def camera_thread(self):
        """Main camera processing thread"""
        prev_frame = None

        while True:
            ret, frame = self.cap.read()
            if not ret:
                logger.error("Failed to read from camera")
                break

            # Motion detection
            if prev_frame is not None:
                motion_detected = self.detect_motion(prev_frame, frame)

                if motion_detected:
                    self.last_motion_time = time.time()
                    if not self.camera_active:
                        self.camera_active = True
                        logger.info("Camera activated - motion detected")
                else:
                    # Check if no motion for timeout period
                    if time.time() - self.last_motion_time > self.no_motion_timeout:
                        if self.camera_active:
                            self.camera_active = False
                            logger.info("Camera deactivated - no motion")

            prev_frame = frame.copy()

            # Process frame only if camera is active
            if self.camera_active:
                face_locations, face_names, face_confidences = self.process_frame(frame)
                frame = self.draw_results(frame, face_locations, face_names, face_confidences)

                # Add "ACTIVE" indicator
                cv2.putText(frame, "ACTIVE", (frame.shape[1] - 100, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                # Add "STANDBY" indicator
                cv2.putText(frame, "STANDBY", (frame.shape[1] - 100, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

            # Display frame
            cv2.imshow('Attendance System - Laptop 2', frame)

            # Check for exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    def sync_thread(self):
        """Background thread for data synchronization"""
        while True:
            try:
                # Reload known faces periodically
                self.load_known_faces()

                # Update system status
                if self.db:
                    self.db.child("system").child("laptop2_status").set({
                        "status": "connected",
                        "last_update": datetime.now().isoformat(),
                        "camera_active": self.camera_active
                    })

                # Clear daily attendance cache at midnight
                current_date = datetime.now().strftime("%Y-%m-%d")
                if hasattr(self, 'last_date') and self.last_date != current_date:
                    self.attendance_marked_today.clear()
                    logger.info("Daily attendance cache cleared")

                self.last_date = current_date

            except Exception as e:
                logger.error(f"Sync error: {e}")

            time.sleep(60)  # Sync every minute

    def start_background_threads(self):
        """Start background threads"""
        sync_thread = threading.Thread(target=self.sync_thread, daemon=True)
        sync_thread.start()

    def run(self):
        """Main run method"""
        logger.info("Starting Attendance System...")
        logger.info("Press 'q' to quit")

        try:
            self.camera_thread()
        except KeyboardInterrupt:
            logger.info("System interrupted by user")
        finally:
            self.cleanup()

    def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up resources...")
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    system = AttendanceSystem()
    system.run()
