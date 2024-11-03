import sys
import os
from PyQt5.QtWidgets import QApplication
from data_manager import DataManager
from setup_window import SetupWindow
from experiment_window import ExperimentWindow

class GazeEstimationApp:
    """Main application class for the gaze estimation experiment."""
    
    def __init__(self):
        """Initialize the application."""
        # Create QApplication first
        self.app = QApplication(sys.argv)
        
        # Set application properties
        self.app.setStyle('Fusion')
        self.app.setApplicationName('Gaze Estimation Experiment')
        self.app.setApplicationVersion('1.0.3')
        
        # Create data manager with application instance
        self.data_manager = DataManager(app_version='1.0.3')
        
    def start(self):
        """Start the application with the metadata collection window."""
        from metadata_window import MainWindow
        self.main_window = MainWindow(self.data_manager)
        self.main_window.show()
        return self.app.exec_()
    
    @staticmethod
    def check_dependencies():
        """Check if all required dependencies are installed."""
        try:
            import cv2
            import mediapipe
            import numpy as np
            print("All dependencies are installed.")
            return True
        except ImportError as e:
            print(f"Missing dependency: {str(e)}")
            return False

def main():
    """Main entry point of the application."""
    # Create application instance
    app = GazeEstimationApp()
    
    # Check dependencies
    if not app.check_dependencies():
        print("Please install all required dependencies:")
        print("pip install opencv-python mediapipe numpy PyQt5")
        sys.exit(1)
    
    try:
        # Start the application
        sys.exit(app.start())
    except Exception as e:
        print(f"Application error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

# import sys
# import json
# import os
# from datetime import datetime
# import platform
# import screeninfo
# import mediapipe as mp
# from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
#                             QHBoxLayout, QLabel, QLineEdit, QComboBox, 
#                             QPushButton, QFormLayout, QMessageBox, QSpinBox,
#                             QTextEdit, QGroupBox)
# from PyQt5.QtCore import Qt
# import cv2
# from setupWindow import SetupWindow

# # App version constant
# APP_VERSION = "1.0.3"

# class MetadataCollector:
#     """Handles collection and validation of system and experiment metadata."""
    
#     def get_system_info(self):
#         """Collect system information automatically."""
#         try:
#             # Get screen information
#             screens = screeninfo.get_monitors()
#             primary_screen = next(s for s in screens if s.is_primary)
#             screen_info = {
#                 "size": f"{primary_screen.width_mm/25.4:.1f} inches",
#                 "resolution": f"{primary_screen.width}x{primary_screen.height}"
#             }
            
#             # Get webcam information
#             cap = cv2.VideoCapture(0)
#             webcam_info = {
#                 "resolution": f"{int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}",
#                 "frame_rate": int(cap.get(cv2.CAP_PROP_FPS))
#             }
#             cap.release()
            
#             # Get system information
#             system_info = {
#                 "os": platform.system(),
#                 "os_version": platform.version(),
#                 "machine": platform.machine(),
#                 "processor": platform.processor()
#             }
            
#             return {
#                 "screen": screen_info,
#                 "webcam": webcam_info,
#                 "system": system_info
#             }
#         except Exception as e:
#             raise RuntimeError(f"Failed to collect system information: {str(e)}")

#     def get_software_versions(self):
#         """Collect software version information."""
#         return {
#             "app_version": APP_VERSION,
#             "mediapipe_version": mp.__version__,
#             "opencv_version": cv2.__version__
#         }

# class MainWindow(QMainWindow):
#     """Main application window handling the UI and workflow."""
    
#     def __init__(self):
#         super().__init__()
#         self.metadata = {}
#         self.notes = []  # List to store timestamped notes
#         self.setup_ui()
        

#     def setup_ui(self):
#         """Initialize the main UI components."""
#         self.setWindowTitle("Gaze Estimation Data Collection")
#         self.setMinimumSize(800, 800)
        
#         # Create central widget and layout
#         central_widget = QWidget()
#         self.setCentralWidget(central_widget)
#         layout = QVBoxLayout(central_widget)
        
#         # Experimenter information group
#         experimenter_group = QGroupBox("Experimenter Information")
#         experimenter_layout = QFormLayout()
#         self.experimenter_id = QLineEdit()
#         experimenter_layout.addRow("Experimenter ID:", self.experimenter_id)
#         experimenter_group.setLayout(experimenter_layout)
#         layout.addWidget(experimenter_group)
        
#         # Subject information group
#         subject_group = QGroupBox("Subject Information")
#         subject_layout = QFormLayout()
        
#         self.subject_id = QLineEdit()
#         subject_layout.addRow("Subject ID:", self.subject_id)
        
#         self.subject_age = QSpinBox()
#         self.subject_age.setRange(18, 100)
#         subject_layout.addRow("Age:", self.subject_age)
        
#         self.subject_gender = QComboBox()
#         self.subject_gender.addItems(["Male", "Female", "Other", "Prefer not to say"])
#         subject_layout.addRow("Gender:", self.subject_gender)
        
#         self.vision_correction = QComboBox()
#         self.vision_correction.addItems(["None", "Glasses", "Contact lenses"])
#         subject_layout.addRow("Vision Correction:", self.vision_correction)
        
#         self.dominant_eye = QComboBox()
#         self.dominant_eye.addItems(["Left", "Right", "Unknown"])
#         subject_layout.addRow("Dominant Eye:", self.dominant_eye)
        
#         subject_group.setLayout(subject_layout)
#         layout.addWidget(subject_group)
        
#         # Notes section
#         notes_group = QGroupBox("Experiment Notes")
#         notes_layout = QVBoxLayout()
        
#         self.notes_input = QTextEdit()
#         self.notes_input.setPlaceholderText("Enter experiment notes here...")
#         notes_layout.addWidget(self.notes_input)
        
#         add_note_btn = QPushButton("Add Note")
#         add_note_btn.clicked.connect(self.add_note)
#         notes_layout.addWidget(add_note_btn)
        
#         notes_group.setLayout(notes_layout)
#         layout.addWidget(notes_group)
        
#         # Add buttons
#         button_layout = QHBoxLayout()
#         self.collect_metadata_btn = QPushButton("Collect System Metadata")
#         self.collect_metadata_btn.clicked.connect(self.collect_metadata)
#         button_layout.addWidget(self.collect_metadata_btn)
        
#         self.next_btn = QPushButton("Next")
#         self.next_btn.clicked.connect(self.proceed_to_setup)
#         button_layout.addWidget(self.next_btn)
        
#         layout.addLayout(button_layout)
            
#     def add_note(self):
#         """Add a timestamped note to the notes list."""
#         note_text = self.notes_input.toPlainText().strip()
#         if note_text:
#             timestamp = datetime.now().strftime("%H:%M:%S")
#             self.notes.append({
#                 "timestamp": timestamp,
#                 "note": note_text
#             })
#             self.notes_input.clear()
#             QMessageBox.information(self, "Success", "Note added successfully!")
    
#     def collect_metadata(self):
#         """Collect and store all metadata."""
#         try:
#             # Collect user input
#             subject_data = {
#                 "id": self.subject_id.text(),
#                 "age": self.subject_age.value(),
#                 "gender": self.subject_gender.currentText(),
#                 "vision_correction": self.vision_correction.currentText(),
#                 "dominant_eye": self.dominant_eye.currentText()
#             }
            
#             # Validate input
#             if not self.validate_metadata(subject_data):
#                 return
            
#             # Collect system metadata
#             collector = MetadataCollector()
#             system_info = collector.get_system_info()
#             software_versions = collector.get_software_versions()
            
#             # Combine all metadata
#             self.metadata = {
#                 "subject": subject_data,
#                 "session": {
#                     "date": datetime.now().strftime("%Y-%m-%d"),
#                     "start_time": datetime.now().strftime("%H:%M:%S"),
#                     "experimenter": self.experimenter_id.text()
#                 },
#                 "equipment": {
#                     "webcam": system_info["webcam"],
#                     "screen": system_info["screen"],
#                     "system": system_info["system"]
#                 },
#                 "software": software_versions,
#                 "notes": self.notes
#             }
            
#             QMessageBox.information(self, "Success", "System metadata collected successfully!")
            
#         except Exception as e:
#             QMessageBox.critical(self, "Error", f"Failed to collect metadata: {str(e)}")
    
#     def validate_metadata(self, subject_data):
#         """Validate the collected metadata."""
#         if not subject_data["id"]:
#             QMessageBox.warning(self, "Validation Error", "Subject ID is required!")
#             return False
#         if not self.experimenter_id.text():
#             QMessageBox.warning(self, "Validation Error", "Experimenter ID is required!")
#             return False
#         return True
    
#     def proceed_to_setup(self):
#         """Save metadata and proceed to experiment setup."""
#         if not hasattr(self, 'metadata') or not self.metadata:
#             QMessageBox.warning(self, "Warning", "Please collect metadata first!")
#             return
            
#         try:
#             # Create directory structure
#             base_dir = datetime.now().strftime("%Y%m%d") + "_GazeEstimationExperiment"
#             subject_dir = os.path.join(base_dir, f"S{self.subject_id.text().zfill(3)}")
#             os.makedirs(subject_dir, exist_ok=True)
#             os.makedirs(os.path.join(subject_dir, "AngleSetups"), exist_ok=True)
            
#             # Save metadata
#             metadata_path = os.path.join(subject_dir, "Metadata.json")
#             with open(metadata_path, 'w') as f:
#                 json.dump(self.metadata, f, indent=2)
            
#             QMessageBox.information(self, "Success", 
#                                   "Metadata saved successfully!\nProceeding to experiment setup...")
            
#             # Launch setup window
#             self.setup_window = SetupWindow(metadata_path)
#             self.setup_window.show()
#             self.hide()
            
#         except Exception as e:
#             QMessageBox.critical(self, "Error", f"Failed to proceed: {str(e)}")            
                
#         #     # TODO: Launch experiment setup window
#         #     # self.setup_window = SetupWindow(self.metadata)
#         #     # self.setup_window.show()
#         #     # self.hide()
            
#         # except Exception as e:
#         #     QMessageBox.critical(self, "Error", f"Failed to save metadata: {str(e)}")

# def main():
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec_())

# if __name__ == "__main__":
#     main()