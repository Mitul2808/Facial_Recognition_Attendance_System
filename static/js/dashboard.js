// Dashboard JavaScript
let currentView = 'dashboard';
let students = {};
let attendanceData = {};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    loadStudents();
    loadAttendance();
    updateSystemStatus();

    // Set up photo capture functionality
    setupPhotoCapture();

    // Set up form submission
    document.getElementById('studentForm').addEventListener('submit', handleStudentRegistration);

    // Update system status every 30 seconds
    setInterval(updateSystemStatus, 30000);
});

// View Management
function showView(viewName) {
    // Hide all views
    document.querySelectorAll('.view').forEach(view => {
        view.style.display = 'none';
    });

    // Show requested view
    if (viewName === 'dashboard') {
        document.getElementById('dashboardView').style.display = 'grid';
    } else {
        document.getElementById(viewName + 'View').style.display = 'block';

        // Initialize view-specific functionality
        if (viewName === 'attendanceAnalytics') {
            initializeAttendanceChart();
        }
    }

    currentView = viewName;
}

// Student Registration Functions
function setupPhotoCapture() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const capturedImage = document.getElementById('capturedImage');
    const startCameraBtn = document.getElementById('startCamera');
    const capturePhotoBtn = document.getElementById('capturePhoto');
    const retakePhotoBtn = document.getElementById('retakePhoto');

    let stream = null;

    startCameraBtn.addEventListener('click', async function() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ 
                video: { width: 640, height: 480 } 
            });
            video.srcObject = stream;
            video.style.display = 'block';
            startCameraBtn.style.display = 'none';
            capturePhotoBtn.style.display = 'inline-block';
        } catch (err) {
            alert('Error accessing camera: ' + err.message);
        }
    });

    capturePhotoBtn.addEventListener('click', function() {
        const context = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0);

        // Convert to base64
        const imageData = canvas.toDataURL('image/jpeg', 0.8);
        capturedImage.src = imageData;
        capturedImage.style.display = 'block';

        // Stop camera
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
        video.style.display = 'none';
        capturePhotoBtn.style.display = 'none';
        retakePhotoBtn.style.display = 'inline-block';
    });

    retakePhotoBtn.addEventListener('click', function() {
        capturedImage.style.display = 'none';
        retakePhotoBtn.style.display = 'none';
        startCameraBtn.style.display = 'inline-block';
    });
}

async function handleStudentRegistration(e) {
    e.preventDefault();

    const formData = {
        id: document.getElementById('studentId').value,
        name: document.getElementById('studentName').value,
        email: document.getElementById('studentEmail').value,
        phone: document.getElementById('studentPhone').value,
        stream: document.getElementById('stream').value,
        enrollmentDate: document.getElementById('enrollmentDate').value
    };

    // Get captured photo
    const capturedImage = document.getElementById('capturedImage');
    if (capturedImage.src && capturedImage.style.display !== 'none') {
        formData.photo_data = capturedImage.src;
    } else {
        alert('Please capture a photo before registering');
        return;
    }

    try {
        const response = await fetch('/api/students', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        if (result.success) {
            alert('Student registered successfully!');

            const studentForm = document.getElementById('studentForm');
            if (studentForm) studentForm.reset();

            const capturedImage = document.getElementById('capturedImage');
            if (capturedImage) capturedImage.style.display = 'none';

            // **Check your actual HTML for the correct ID - likely 'retakePhoto' instead of 'retakePhotoBtn'**
            const retakePhotoBtn = document.getElementById('retakePhoto') || document.getElementById('retakePhotoBtn');
            if (retakePhotoBtn) retakePhotoBtn.style.display = 'none';

            const startCamera = document.getElementById('startCamera');
            if (startCamera) startCamera.style.display = 'inline-block';

            loadStudents(); // Refresh students list
        } else {
            alert('Registration failed: ' + result.message);
        }
    } catch (error) {
        alert('Registration error: ' + error.message);
    }
}

// Data Loading Functions
async function loadStudents() {
    try {
        const response = await fetch('/api/students');
        students = await response.json();
    } catch (error) {
        console.error('Error loading students:', error);
    }
}

async function loadAttendance() {
    try {
        const response = await fetch('/api/attendance');
        attendanceData = await response.json();
    } catch (error) {
        console.error('Error loading attendance:', error);
    }
}

// Reports Functions
async function generateReport() {
    const stream = document.getElementById('reportStream').value;
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;

    try {
        const params = new URLSearchParams();
        if (stream) params.append('stream', stream);
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);

        const response = await fetch('/api/attendance/report?' + params);
        const reportData = await response.json();

        displayReport(reportData);
    } catch (error) {
        console.error('Error generating report:', error);
    }
}

function displayReport(data) {
    const resultsDiv = document.getElementById('reportResults');

    if (data.length === 0) {
        resultsDiv.innerHTML = '<p>No attendance data found for the selected criteria.</p>';
        return;
    }

    let html = `
        <table class="report-table">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Student ID</th>
                    <th>Student Name</th>
                    <th>Stream</th>
                    <th>Lecture 1</th>
                    <th>Lecture 2</th>
                    <th>Lecture 3</th>
                    <th>Lecture 4</th>
                    <th>Lecture 5</th>
                </tr>
            </thead>
            <tbody>
    `;

    data.forEach(record => {
        html += `
            <tr>
                <td>${record.date}</td>
                <td>${record.student_id}</td>
                <td>${record.student_name}</td>
                <td>${record.stream}</td>
                <td>${record.lectures.lecture1 || 'Absent'}</td>
                <td>${record.lectures.lecture2 || 'Absent'}</td>
                <td>${record.lectures.lecture3 || 'Absent'}</td>
                <td>${record.lectures.lecture4 || 'Absent'}</td>
                <td>${record.lectures.lecture5 || 'Absent'}</td>
            </tr>
        `;
    });

    html += '</tbody></table>';
    resultsDiv.innerHTML = html;
}

// Analytics Functions
function initializeAttendanceChart() {
    const ctx = document.getElementById('attendanceChart').getContext('2d');

    // Sample data for demonstration
    const chartData = {
        labels: ['MCA', 'MBA', 'BVoc.IT'],
        datasets: [{
            label: 'Average Attendance %',
            data: [85, 92, 78],
            backgroundColor: [
                'rgba(59, 130, 246, 0.8)',
                'rgba(16, 185, 129, 0.8)',
                'rgba(245, 158, 11, 0.8)'
            ],
            borderColor: [
                'rgba(59, 130, 246, 1)',
                'rgba(16, 185, 129, 1)',
                'rgba(245, 158, 11, 1)'
            ],
            borderWidth: 2
        }]
    };

    new Chart(ctx, {
        type: 'bar',
        data: chartData,
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Attendance by Stream'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
}

// Add FullCalendar CSS/JS in HTML separately as advised

// Load festivals and initialize calendar view
async function loadCalendarFestivals() {
    try {
        const response = await fetch('/api/festivals');
        const festivals = await response.json();

        // Transform for FullCalendar events
        const events = [];
        for (const date in festivals) {
            if (festivals.hasOwnProperty(date)) {
                events.push({
                    title: festivals[date].name,
                    start: date,
                    allDay: true
                });
            }
        }

        const calendarEl = document.getElementById('calendar');
        calendarEl.innerHTML = ''; // Clear old calendar

        const calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            events: events
        });
        calendar.render();
    } catch (error) {
        console.error('Calendar load error:', error);
        document.getElementById('calendar').innerHTML = '<p>Error loading calendar data</p>';
    }
}

// Extend showView function to support calendar and systemStatus
function showView(viewName) {
    document.querySelectorAll('.view').forEach(view => {
        view.style.display = 'none';
    });

    if (viewName === 'dashboard') {
        document.getElementById('dashboardView').style.display = 'grid';
    } else {
        const viewElement = document.getElementById(viewName + 'View');
        if (viewElement) {
            viewElement.style.display = 'block';
        }

        if (viewName === 'attendanceAnalytics') {
            initializeAttendanceChart();
        }
        if (viewName === 'calendar') {
            loadCalendarFestivals();
        }
        if (viewName === 'systemStatus') {
            updateSystemStatus();
        }
    }

    currentView = viewName;
}

// Update system status UI with detailed info
async function updateSystemStatus() {
    try {
        const response = await fetch('/api/system-status');
        const status = await response.json();

        document.getElementById('firebaseStatus').textContent = status.firebase;
        document.getElementById('laptop1Status').textContent = status.laptop1;
        document.getElementById('laptop2Status').textContent = status.laptop2;
        document.getElementById('lastSync').textContent = status.last_sync ? new Date(status.last_sync).toLocaleString() : 'N/A';

        const indicator = document.getElementById('systemStatusIndicator');
        if (status.firebase === 'Connected' && status.laptop1 === 'Connected') {
            indicator.style.background = '#10b981'; // Green
        } else {
            indicator.style.background = '#ef4444'; // Red
        }
    } catch (error) {
        console.error('System status update error:', error);
        const indicator = document.getElementById('systemStatusIndicator');
        indicator.style.background = '#ef4444';
        document.getElementById('firebaseStatus').textContent = 'Error';
        document.getElementById('laptop1Status').textContent = 'Error';
        document.getElementById('laptop2Status').textContent = 'Error';
        document.getElementById('lastSync').textContent = 'N/A';
    }
}

// Utility Functions
function logout() {
    if (confirm('Are you sure you want to logout?')) {
        window.location.href = '/logout';
    }
}

// Export functions for global access
window.showView = showView;
window.generateReport = generateReport;
window.logout = logout;