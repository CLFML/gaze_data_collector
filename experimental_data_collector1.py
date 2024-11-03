import sys
import csv
import json
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                           QComboBox, QFileDialog, QMessageBox, QGroupBox, 
                           QFormLayout, QGridLayout)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
import cv2
import mediapipe as mp
import numpy as np

class GazeEstimationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gaze Estimation Data Collection")
        self.setGeometry(100, 100, 1200, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.setup_ui()
        self.setup_camera()
        self.recording = False

    def setup_ui(self):
        # Create a horizontal layout for metadata and camera feed
        main_layout = QHBoxLayout()
        
        # Metadata section
        metadata_widget = QWidget()
        metadata_layout = QVBoxLayout(metadata_widget)
        
        # Subject Information Group
        subject_group = QGroupBox("Subject Information")
        subject_form = QFormLayout()

        # Subject ID
        self.subject_id_input = QLineEdit()
        subject_form.addRow("Subject ID:", self.subject_id_input)

        # Age
        self.age_input = QLineEdit()
        self.age_input.setPlaceholderText("Enter age")
        subject_form.addRow("Age:", self.age_input)

        # Gender
        self.gender_input = QComboBox()
        self.gender_input.addItems(["Select Gender", "Male", "Female", "Other", "Prefer not to say"])
        subject_form.addRow("Gender:", self.gender_input)

        # Vision Correction
        self.vision_input = QComboBox()
        self.vision_input.addItems([
            "Select Vision Correction",
            "None",
            "Glasses",
            "Contact Lenses",
            "Laser Surgery",
            "Other"
        ])
        subject_form.addRow("Vision Correction:", self.vision_input)

        # Dominant Eye
        self.eye_input = QComboBox()
        self.eye_input.addItems([
            "Select Dominant Eye",
            "Left",
            "Right",
            "Unknown"
        ])
        subject_form.addRow("Dominant Eye:", self.eye_input)

        subject_group.setLayout(subject_form)
        metadata_layout.addWidget(subject_group)

        # Session Information Group
        session_group = QGroupBox("Session Information")
        session_form = QFormLayout()

        # Experimenter Name
        self.experimenter_input = QLineEdit()
        session_form.addRow("Experimenter:", self.experimenter_input)

        # Notes Field
        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("Enter any relevant notes about the session")
        session_form.addRow("Notes:", self.notes_input)

        session_group.setLayout(session_form)
        metadata_layout.addWidget(session_group)

        # Status Display
        self.status_label = QLabel("Status: Ready")
        metadata_layout.addWidget(self.status_label)

        # Control buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Recording")
        self.start_button.clicked.connect(self.start_recording)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Recording")
        self.stop_button.clicked.connect(self.stop_recording)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)

        metadata_layout.addLayout(button_layout)
        metadata_layout.addStretch()

        # Add metadata widget to main layout
        main_layout.addWidget(metadata_widget, stretch=1)

        # Camera feed section
        camera_widget = QWidget()
        camera_layout = QVBoxLayout(camera_widget)
        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignCenter)
        camera_layout.addWidget(self.camera_label)

        # Add camera widget to main layout
        main_layout.addWidget(camera_widget, stretch=2)

        # Add main layout to the window
        self.layout.addLayout(main_layout)

    def setup_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update every 30 ms

        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # Flip the frame horizontally for a more natural mirror view
            frame = cv2.flip(frame, 1)
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)

            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    self.draw_landmarks(frame, face_landmarks)
                    if self.recording:
                        self.record_landmarks(face_landmarks)

            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            scaled_pixmap = QPixmap.fromImage(q_image).scaled(
                self.camera_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.camera_label.setPixmap(scaled_pixmap)

    def draw_landmarks(self, frame, landmarks):
        for landmark in landmarks.landmark:
            x = int(landmark.x * frame.shape[1])
            y = int(landmark.y * frame.shape[0])
            cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)

    def record_landmarks(self, landmarks):
        timestamp = datetime.now().timestamp()
        landmark_row = [timestamp]
        for landmark in landmarks.landmark:
            landmark_row.extend([landmark.x, landmark.y, landmark.z])
        self.landmarks_data.append(landmark_row)

    def validate_inputs(self):
        if not self.subject_id_input.text():
            QMessageBox.warning(self, "Validation Error", "Subject ID is required!")
            return False
        if not self.age_input.text().isdigit():
            QMessageBox.warning(self, "Validation Error", "Please enter a valid age!")
            return False
        if self.gender_input.currentText() == "Select Gender":
            QMessageBox.warning(self, "Validation Error", "Please select a gender!")
            return False
        if self.vision_input.currentText() == "Select Vision Correction":
            QMessageBox.warning(self, "Validation Error", "Please select vision correction type!")
            return False
        if self.eye_input.currentText() == "Select Dominant Eye":
            QMessageBox.warning(self, "Validation Error", "Please select dominant eye!")
            return False
        return True

    def start_recording(self):
        if not self.validate_inputs():
            return
            
        self.recording = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.landmarks_data = []
        self.start_time = datetime.now()
        self.status_label.setText("Status: Recording...")
        self.status_label.setStyleSheet("color: red")

    def stop_recording(self):
        self.recording = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Status: Ready")
        self.status_label.setStyleSheet("color: black")
        self.save_data()

    def save_data(self):
        metadata = {
            "subject": {
                "id": self.subject_id_input.text(),
                "age": int(self.age_input.text()),
                "gender": self.gender_input.currentText(),
                "vision_correction": self.vision_input.currentText(),
                "dominant_eye": self.eye_input.currentText()
            },
            "session": {
                "date": self.start_time.strftime("%Y-%m-%d"),
                "start_time": self.start_time.strftime("%H:%M:%S"),
                "end_time": datetime.now().strftime("%H:%M:%S"),
                "experimenter": self.experimenter_input.text(),
                "notes": self.notes_input.text()
            },
            "equipment": {
                "webcam": {
                    "id": 0,  # Default camera
                    "resolution": f"{int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}",
                    "fps": int(self.cap.get(cv2.CAP_PROP_FPS))
                }
            }
        }

        file_name = f"{self.subject_id_input.text()}_{self.start_time.strftime('%Y%m%d_%H%M%S')}"
        options = QFileDialog.Options()
        directory = QFileDialog.getExistingDirectory(self, "Select Directory to Save Data")
        
        if directory:
            # Save metadata
            with open(f"{directory}/{file_name}_metadata.json", "w") as f:
                json.dump(metadata, f, indent=4)

            # Save landmarks
            with open(f"{directory}/{file_name}_landmarks.csv", "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp"] + [f"landmark_{i}_{coord}" 
                    for i in range(468) for coord in ['x','y','z']])
                writer.writerows(self.landmarks_data)

            QMessageBox.information(self, "Data Saved", 
                f"Data has been saved successfully!\nLocation: {directory}")

    def closeEvent(self, event):
        if self.recording:
            reply = QMessageBox.question(self, 'Warning',
                "Recording is still in progress. Do you want to stop and save before closing?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

            if reply == QMessageBox.Yes:
                self.stop_recording()
            
        self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GazeEstimationApp()
    window.show()
    sys.exit(app.exec_())