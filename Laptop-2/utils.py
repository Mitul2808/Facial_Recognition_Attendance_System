import cv2
import numpy as np
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class CameraManager:
    """Utility class for camera management"""

    def __init__(self, camera_index=0, width=640, height=480):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.cap = None
        self.initialize_camera()

    def initialize_camera(self):
        """Initialize camera with error handling"""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

            # Test camera
            ret, frame = self.cap.read()
            if not ret:
                raise Exception("Camera not accessible")

            logger.info(f"Camera initialized successfully: {self.width}x{self.height}")
            return True

        except Exception as e:
            logger.error(f"Camera initialization failed: {e}")
            return False

    def read_frame(self):
        """Read frame with error handling"""
        if self.cap is None:
            return False, None

        ret, frame = self.cap.read()
        return ret, frame

    def release(self):
        """Release camera resources"""
        if self.cap:
            self.cap.release()

class MotionDetector:
    """Utility class for motion detection"""

    def __init__(self, threshold=5000):
        self.threshold = threshold
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(
            detectShadows=True
        )

    def detect_motion(self, frame):
        """Detect motion in frame"""
        # Apply background subtraction
        fg_mask = self.background_subtractor.apply(frame)

        # Calculate motion amount
        motion_amount = np.sum(fg_mask) / 255

        return motion_amount > self.threshold, motion_amount

class FaceProcessor:
    """Utility class for face processing operations"""

    @staticmethod
    def preprocess_image(image_path, target_size=(150, 150)):
        """Preprocess image for better recognition"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return None

            # Convert to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Resize
            resized = cv2.resize(rgb_image, target_size)

            # Histogram equalization for better contrast
            lab = cv2.cvtColor(resized, cv2.COLOR_RGB2LAB)
            lab[:,:,0] = cv2.equalizeHist(lab[:,:,0])
            enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

            return enhanced

        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return None

    @staticmethod
    def validate_face_image(image):
        """Validate if image contains a clear face"""
        try:
            import face_recognition

            # Try to find faces
            face_locations = face_recognition.face_locations(image)

            # Check if exactly one face is found
            if len(face_locations) == 1:
                return True, "Face detected successfully"
            elif len(face_locations) == 0:
                return False, "No face detected in image"
            else:
                return False, f"Multiple faces detected ({len(face_locations)})"

        except Exception as e:
            return False, f"Face validation error: {e}"

class DatabaseManager:
    """Utility class for database operations"""

    def __init__(self, db_instance):
        self.db = db_instance

    def safe_write(self, path, data):
        """Safely write data to database with error handling"""
        try:
            if self.db:
                self.db.child(path).set(data)
                return True
        except Exception as e:
            logger.error(f"Database write error at {path}: {e}")
        return False

    def safe_read(self, path):
        """Safely read data from database with error handling"""
        try:
            if self.db:
                result = self.db.child(path).get()
                return result.val() if result else None
        except Exception as e:
            logger.error(f"Database read error at {path}: {e}")
        return None

    def safe_push(self, path, data):
        """Safely push data to database with error handling"""
        try:
            if self.db:
                result = self.db.child(path).push(data)
                return result.key if result else None
        except Exception as e:
            logger.error(f"Database push error at {path}: {e}")
        return None

def setup_logging(log_level="INFO"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("attendance_system.log"),
            logging.StreamHandler()
        ]
    )
