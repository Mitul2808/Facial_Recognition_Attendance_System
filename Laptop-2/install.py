#!/usr/bin/env python3
"""
Installation script for Laptop-2 Camera System
This script helps set up the camera system with proper dependencies and configuration.
"""

import subprocess
import sys
import os
import platform

def install_package(package):
    """Install a Python package using pip"""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def check_opencv_installation():
    """Check if OpenCV is properly installed"""
    try:
        import cv2
        print(f"✓ OpenCV version: {cv2.getVersionString()}")
        return True
    except ImportError:
        print("✗ OpenCV not found")
        return False

def check_camera_access():
    """Test camera access"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()

        if ret:
            print("✓ Camera access: OK")
            return True
        else:
            print("✗ Camera access: Failed")
            return False
    except Exception as e:
        print(f"✗ Camera test error: {e}")
        return False

def install_system_dependencies():
    """Install system-level dependencies"""
    system = platform.system().lower()

    if system == "linux":
        print("Installing Linux dependencies...")
        try:
            # Common dependencies for OpenCV
            subprocess.run(["sudo", "apt-get", "update"], check=False)
            subprocess.run([
                "sudo", "apt-get", "install", "-y",
                "python3-opencv", "libopencv-dev", "python3-dev",
                "libgtk-3-dev", "libboost-all-dev"
            ], check=False)
        except subprocess.CalledProcessError:
            print("Note: Some system dependencies may need manual installation")

    elif system == "darwin":  # macOS
        print("Installing macOS dependencies...")
        try:
            subprocess.run(["brew", "install", "opencv"], check=False)
        except subprocess.CalledProcessError:
            print("Note: Install Homebrew and try again, or install OpenCV manually")

    elif system == "windows":
        print("Windows detected. Install Visual C++ redistributables if needed.")

def main():
    print("=== Laptop-2 Camera System Installation ===")
    print()

    # Install system dependencies
    install_system_dependencies()

    # Install Python packages
    print("Installing Python packages...")

    packages = [
        "opencv-python==4.8.1.78",
        "face-recognition==1.3.0", 
        "numpy==1.24.3",
        "pyrebase4==4.7.1",
        "Pillow==10.0.0",
        "python-dateutil==2.8.2",
        "requests==2.31.0"
    ]

    for package in packages:
        try:
            print(f"Installing {package}...")
            install_package(package)
            print(f"✓ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {package}: {e}")

    print()
    print("=== System Check ===")

    # Check installations
    opencv_ok = check_opencv_installation()
    camera_ok = check_camera_access()

    # Check face_recognition
    try:
        import face_recognition
        print("✓ face_recognition library: OK")
        face_rec_ok = True
    except ImportError:
        print("✗ face_recognition library: Not found")
        face_rec_ok = False

    # Check Firebase
    try:
        import pyrebase
        print("✓ pyrebase library: OK")
        firebase_ok = True
    except ImportError:
        print("✗ pyrebase library: Not found")
        firebase_ok = False

    print()
    print("=== Installation Summary ===")

    if opencv_ok and camera_ok and face_rec_ok and firebase_ok:
        print("✓ All components installed successfully!")
        print("You can now run the attendance system with: python face_recognition_system.py")
    else:
        print("✗ Some components failed to install. Please check the errors above.")
        print("Manual installation may be required for some dependencies.")

    print()
    print("Next steps:")
    print("1. Configure Firebase settings in face_recognition_system.py")
    print("2. Ensure Laptop-1 is running and accessible")
    print("3. Test the camera system")

if __name__ == "__main__":
    main()
