import sys
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QComboBox, QFormLayout, QMessageBox,
                            QGroupBox, QApplication)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage
import cv2
from experiment_window import ExperimentWindow
import mediapipe as mp
import numpy as np

class SetupWindow(QWidget):
    """Window for experiment setup including camera angles and distances."""

    def __init__(self, data_manager, subject_dir, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.subject_dir = subject_dir
        self.camera = None
        self.anonymized = True
        
        # Initialize MediaPipe components
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Define experimental parameters first
        self.yaw_angles = [0, 15, -15, 30, -30]
        self.pitch_angles = [0, 15, -15, 30, -30]
        self.distances = [30, 60, 90]  # cm

        # Add trial tracking
        self.completed_setups = set()  # Track which angle/distance combinations have been done
        self.total_combinations = len(self.yaw_angles) * len(self.pitch_angles) * len(self.distances)
        
        # Now setup UI and camera
        self.setup_ui()
        self.setup_camera()
        self.update_window_title()
        self.update_progress()

    
    def update_window_title(self):
        """Update window title with current trial number."""
        trial_count = self.data_manager.get_trial_count(self.subject_dir)
        self.setWindowTitle(f"Experiment Setup - Trial {trial_count + 1}")
    
    def setup_ui(self):
        """Initialize the UI components."""
        self.setMinimumSize(1200, 800)
        
        layout = QHBoxLayout(self)
        
        # Left panel for camera preview
        preview_group = QGroupBox("Camera Preview")
        preview_layout = QVBoxLayout()
        self.preview_label = QLabel()
        self.preview_label.setMinimumSize(640, 480)
        preview_layout.addWidget(self.preview_label)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Right panel for controls
        controls_layout = QVBoxLayout()
        
        # Setup parameters group
        setup_group = QGroupBox("Setup Parameters")
        setup_form = QFormLayout()
        
        # Yaw angle selection
        self.yaw_combo = QComboBox()
        self.yaw_combo.addItems([f"{angle}°" for angle in self.yaw_angles])
        setup_form.addRow("Camera Yaw:", self.yaw_combo)
        
        # Pitch angle selection
        self.pitch_combo = QComboBox()
        self.pitch_combo.addItems([f"{angle}°" for angle in self.pitch_angles])
        setup_form.addRow("Camera Pitch:", self.pitch_combo)
        
        # Distance selection
        self.distance_combo = QComboBox()
        self.distance_combo.addItems([f"{dist} cm" for dist in self.distances])
        setup_form.addRow("Subject Distance:", self.distance_combo)
        
        setup_group.setLayout(setup_form)
        controls_layout.addWidget(setup_group)
        
        # Setup instructions group
        instructions_group = QGroupBox("Setup Instructions")
        instructions_layout = QVBoxLayout()
        
        instructions_text = """
        1. Position the subject at the marked distance
        2. Use the digital inclinometer to set camera pitch
        3. Use the printed pattern to set camera yaw
        4. Verify subject is centered in camera view
        5. Ensure good lighting conditions
        """
        instructions_label = QLabel(instructions_text)
        instructions_layout.addWidget(instructions_label)
        
        instructions_group.setLayout(instructions_layout)
        controls_layout.addWidget(instructions_group)
        
        # Trial information group
        trial_group = QGroupBox("Trial Information")
        trial_layout = QVBoxLayout()
        self.trial_label = QLabel(f"Preparing trial...")
        trial_layout.addWidget(self.trial_label)
        trial_group.setLayout(trial_layout)
        controls_layout.addWidget(trial_group)
        
        # Validation group
        validation_group = QGroupBox("Setup Validation")
        validation_layout = QVBoxLayout()
        
        self.validation_label = QLabel("Status: Not validated")
        validation_layout.addWidget(self.validation_label)
        
        validation_group.setLayout(validation_layout)
        controls_layout.addWidget(validation_group)

        # Add progress information
        progress_group = QGroupBox("Session Progress")
        progress_layout = QVBoxLayout()
        self.progress_label = QLabel("Completed: 0/{} combinations".format(self.total_combinations))
        progress_layout.addWidget(self.progress_label)
        
        # Add remaining combinations display
        self.remaining_label = QLabel("Remaining combinations:")
        progress_layout.addWidget(self.remaining_label)
        progress_group.setLayout(progress_layout)
        controls_layout.addWidget(progress_group)        
        
        # Control buttons
        button_layout = QHBoxLayout()

        self.validate_btn = QPushButton("Validate Setup")
        self.validate_btn.clicked.connect(self.validate_setup)
        button_layout.addWidget(self.validate_btn)
        
        self.start_btn = QPushButton("Start Trial")
        self.start_btn.clicked.connect(self.start_trial)
        self.start_btn.setEnabled(False)
        button_layout.addWidget(self.start_btn)
        
        controls_layout.addLayout(button_layout)

        # Add session control buttons
        session_button_layout = QHBoxLayout()
        
        self.new_subject_btn = QPushButton("New Subject")
        self.new_subject_btn.clicked.connect(self.start_new_subject)
        session_button_layout.addWidget(self.new_subject_btn)
        
        self.end_session_btn = QPushButton("End Session")
        self.end_session_btn.clicked.connect(self.end_session)
        session_button_layout.addWidget(self.end_session_btn)        

        controls_layout.addLayout(session_button_layout)
        
        layout.addLayout(controls_layout)

    def update_progress(self):
        """Update the progress display."""
        completed = len(self.completed_setups)
        self.progress_label.setText(f"Completed: {completed}/{self.total_combinations} combinations")
        
        # Show remaining combinations
        remaining_text = "Remaining combinations:\n"
        for yaw in self.yaw_angles:
            for pitch in self.pitch_angles:
                for dist in self.distances:
                    combo = (yaw, pitch, dist)
                    if combo not in self.completed_setups:
                        remaining_text += f"Yaw: {yaw}°, Pitch: {pitch}°, Distance: {dist}cm\n"
        
        self.remaining_label.setText(remaining_text)

    def get_current_combination(self):
        """Get the current angle/distance combination."""
        return (
            self.yaw_angles[self.yaw_combo.currentIndex()],
            self.pitch_angles[self.pitch_combo.currentIndex()],
            self.distances[self.distance_combo.currentIndex()]
        )
    
    def combination_exists(self):
        """Check if the current combination has already been completed."""
        return self.get_current_combination() in self.completed_setups
    
    def setup_camera(self):
        """Initialize the camera preview."""
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            QMessageBox.critical(self, "Error", "Failed to open camera!")
            return
        
        # Start timer for camera preview updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_preview)
        self.timer.start(30)  # Update every 30ms (approx. 33 fps)
    
    def update_preview(self):
        """Update the camera preview with facial landmarks."""
        if self.camera is None:
            return
            
        ret, frame = self.camera.read()
        if ret:
            # Flip the frame horizontally for a mirror effect
            frame = cv2.flip(frame, 1)
            
            # Convert the BGR image to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process the frame and detect landmarks
            results = self.face_mesh.process(rgb_frame)
            
            # Draw the landmarks on the frame
            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]
                
                # Create a copy of the frame for drawing
                annotated_frame = np.zeros_like(frame) if self.anonymized else frame.copy()
                
                # Draw face mesh
                self.mp_drawing.draw_landmarks(
                    image=annotated_frame,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_tesselation_style()
                )
                
                # Draw the contours
                self.mp_drawing.draw_landmarks(
                    image=annotated_frame,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_contours_style()
                )
                
                # Draw iris landmarks
                self.mp_drawing.draw_landmarks(
                    image=annotated_frame,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_IRISES,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_iris_connections_style()
                )
                
                # Draw specific points for eye landmarks
                for idx in [33, 133, 362, 263]:  # Corner points of the eyes
                    pos = face_landmarks.landmark[idx]
                    x = int(pos.x * frame.shape[1])
                    y = int(pos.y * frame.shape[0])
                    cv2.circle(annotated_frame, (x, y), 3, (0, 255, 0), -1)
                
                # Draw iris centers
                iris_landmarks = [
                    (468, 473),  # Left eye
                    (473, 477)   # Right eye
                ]
                for start, end in iris_landmarks:
                    for idx in range(start, end + 1):
                        if idx < len(face_landmarks.landmark):
                            pos = face_landmarks.landmark[idx]
                            x = int(pos.x * frame.shape[1])
                            y = int(pos.y * frame.shape[0])
                            cv2.circle(annotated_frame, (x, y), 3, (255, 0, 0), -1)
                
                # Add text to show that landmarks are detected
                cv2.putText(annotated_frame, "Face Detected", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                # If no face is detected, show the original frame with a warning
                annotated_frame = frame
                cv2.putText(annotated_frame, "No Face Detected", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            # Convert the frame to QPixmap and display it
            h, w, ch = annotated_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB).data,
                            w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            scaled_pixmap = pixmap.scaled(self.preview_label.size(), 
                                        Qt.KeepAspectRatio)
            self.preview_label.setPixmap(scaled_pixmap)

    def validate_setup(self):
        """Validate the experimental setup."""
        try:
            # Check if combination already exists
            if self.combination_exists():
                raise Exception("This combination has already been completed. Please select a different combination.")
                        
            # Check camera feed
            if self.camera is None or not self.camera.isOpened():
                raise Exception("Camera is not properly initialized")
            
            # Check if face is detected
            ret, frame = self.camera.read()
            if not ret:
                raise Exception("Cannot read from camera")
            
            # Process the frame with MediaPipe
            # rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # results = self.face_mesh.process(rgb_frame)
            
            # if not results.multi_face_landmarks:
            #     raise Exception("No face detected - please center your face in the camera")
            
            # # Check if iris landmarks are detected
            # face_landmarks = results.multi_face_landmarks[0]
            # if len(face_landmarks.landmark) < 478:  # MediaPipe face mesh with iris has 478 landmarks
            #     raise Exception("Iris landmarks not detected - please move closer to the camera")
            
            # Update status and enable start button
            self.validation_label.setText("Status: Setup validated successfully")
            self.validation_label.setStyleSheet("color: green")
            self.start_btn.setEnabled(True)
            
            QMessageBox.information(self, "Success", 
                                  "Setup validated successfully!")
            
        except Exception as e:
            self.validation_label.setText(f"Status: Validation failed - {str(e)}")
            self.validation_label.setStyleSheet("color: red")
            self.start_btn.setEnabled(False)
            QMessageBox.warning(self, "Validation Failed", str(e))    
        
    def start_trial(self):
        """Start a new trial with current setup."""
        if not self.start_btn.isEnabled():
            return
            
        try:
            # Create new trial directory
            trial_dir = self.data_manager.create_trial_directory(self.subject_dir)
            
            # Prepare trial configuration
            trial_config = {
                "trial_id": trial_dir.name,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "setup": {
                    "yaw": self.yaw_angles[self.yaw_combo.currentIndex()],
                    "pitch": self.pitch_angles[self.pitch_combo.currentIndex()],
                    "distance": self.distances[self.distance_combo.currentIndex()]
                },
                "conditions": {
                    "dot_display_time": 2000,
                    "rest_time": 1000,
                    "grid_size": 3,
                    "dot_radius": 15
                }
            }
            
            # Save trial configuration
            self.data_manager.save_trial_config(trial_dir, trial_config)
            
            # Launch experiment window
            self.experiment_window = ExperimentWindow(
                self.data_manager,
                trial_dir,
                trial_config
            )
            self.experiment_window.show()
            self.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", 
                               f"Failed to start trial: {str(e)}")    
        
    def on_experiment_finished(self):
        """Handle completion of an experiment trial."""
        # Add current combination to completed setups
        self.completed_setups.add(self.get_current_combination())
        
        # Update progress
        self.update_progress()
        
        # Reset validation
        self.validation_label.setText("Status: Not validated")
        self.validation_label.setStyleSheet("color: black")
        self.start_btn.setEnabled(False)
        
        # Show options dialog
        self.show_next_options()

    def show_next_options(self):
        """Show dialog with options for next action."""
        if len(self.completed_setups) >= self.total_combinations:
            QMessageBox.information(self, "Session Complete", 
                "All combinations have been completed for this subject!")
            self.start_new_subject()
            return
            
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText("Trial completed successfully!")
        msg.setInformativeText("What would you like to do next?")
        
        continue_btn = msg.addButton("Next Trial", QMessageBox.ActionRole)
        new_subject_btn = msg.addButton("New Subject", QMessageBox.ActionRole)
        end_btn = msg.addButton("End Session", QMessageBox.ActionRole)
        
        msg.exec_()
        
        clicked_button = msg.clickedButton()
        if clicked_button == continue_btn:
            self.show()
        elif clicked_button == new_subject_btn:
            self.start_new_subject()
        else:
            self.end_session()
    
    def start_new_subject(self):
        """Start a session with a new subject."""
        from metadata_window import MainWindow
        self.metadata_window = MainWindow(self.data_manager)
        self.metadata_window.show()
        self.close()
    
    def end_session(self):
        """End the current session."""
        reply = QMessageBox.question(self, 'End Session', 
                                   'Are you sure you want to end the session?',
                                   QMessageBox.Yes | QMessageBox.No, 
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            QApplication.quit()

    def closeEvent(self, event):
        """Clean up resources when window is closed."""
        if self.camera is not None:
            self.camera.release()
        if hasattr(self, 'timer'):
            self.timer.stop()
        if hasattr(self, 'face_mesh'):
            self.face_mesh.close()
        event.accept()

    def start_trial(self):
        """Start a new trial with current setup."""
        if not self.start_btn.isEnabled():
            return
            
        try:
            # Create trial directory
            trial_dir = self.data_manager.create_trial_directory(self.subject_dir)
            
            # Prepare trial configuration
            trial_config = {
                "trial_id": trial_dir.name,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "setup": {
                    "yaw": self.yaw_angles[self.yaw_combo.currentIndex()],
                    "pitch": self.pitch_angles[self.pitch_combo.currentIndex()],
                    "distance": self.distances[self.distance_combo.currentIndex()]
                },
                "conditions": {
                    "dot_display_time": 2000,
                    "rest_time": 1000,
                    "grid_size": 3,
                    "dot_radius": 15
                }
            }
            
            # Save trial configuration
            self.data_manager.save_trial_config(trial_dir, trial_config)
            
            # Launch experiment window
            self.experiment_window = ExperimentWindow(
                self.data_manager,
                trial_dir,
                trial_config
            )
            # Connect the finished signal
            self.experiment_window.finished.connect(self.on_experiment_finished)
            self.experiment_window.show()
            self.hide()  # Hide setup window but don't close it
            
        except Exception as e:
            QMessageBox.critical(self, "Error", 
                               f"Failed to start trial: {str(e)}")        
        
    
def main():
    """Main function for testing the SetupWindow independently."""
    app = QApplication(sys.argv)
    
    # Create test data manager and subject directory
    from data_manager import DataManager
    dm = DataManager()
    subject_dir = dm.create_subject_directory("001")
    
    # Create and show the setup window
    window = SetupWindow(dm, subject_dir)
    window.show()
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
