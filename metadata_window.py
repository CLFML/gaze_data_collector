import sys
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,  
                            QLineEdit, QComboBox, QPushButton, QFormLayout, QMessageBox, 
                            QSpinBox, QGroupBox, QTextEdit, QApplication)
import cv2
import mediapipe as mp
from setup_window import SetupWindow

class MainWindow(QMainWindow):
    """Main window for collecting metadata and starting the experiment."""
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.metadata = {}
        self.notes = []  # List to store timestamped notes
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the main UI components."""
        self.setWindowTitle("Gaze Estimation Data Collection")
        self.setMinimumSize(800, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Experimenter information group
        experimenter_group = QGroupBox("Experimenter Information")
        experimenter_layout = QFormLayout()
        self.experimenter_id = QLineEdit()
        experimenter_layout.addRow("Experimenter ID:", self.experimenter_id)
        experimenter_group.setLayout(experimenter_layout)
        layout.addWidget(experimenter_group)
        
        # Subject information group
        subject_group = QGroupBox("Subject Information")
        subject_layout = QFormLayout()
        
        self.subject_id = QLineEdit()
        subject_layout.addRow("Subject ID:", self.subject_id)
        
        self.subject_age = QSpinBox()
        self.subject_age.setRange(18, 100)
        subject_layout.addRow("Age:", self.subject_age)
        
        self.subject_gender = QComboBox()
        self.subject_gender.addItems(["Male", "Female", "Other", "Prefer not to say"])
        subject_layout.addRow("Gender:", self.subject_gender)
        
        self.vision_correction = QComboBox()
        self.vision_correction.addItems(["None", "Glasses", "Contact lenses"])
        subject_layout.addRow("Vision Correction:", self.vision_correction)
        
        self.dominant_eye = QComboBox()
        self.dominant_eye.addItems(["Left", "Right", "Unknown"])
        subject_layout.addRow("Dominant Eye:", self.dominant_eye)
        
        subject_group.setLayout(subject_layout)
        layout.addWidget(subject_group)
        
        # Notes section
        notes_group = QGroupBox("Experiment Notes")
        notes_layout = QVBoxLayout()
        
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Enter experiment notes here...")
        notes_layout.addWidget(self.notes_input)
        
        add_note_btn = QPushButton("Add Note")
        add_note_btn.clicked.connect(self.add_note)
        notes_layout.addWidget(add_note_btn)
        
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        # Add buttons
        button_layout = QHBoxLayout()
        self.collect_metadata_btn = QPushButton("Collect System Metadata")
        self.collect_metadata_btn.clicked.connect(self.collect_metadata)
        button_layout.addWidget(self.collect_metadata_btn)
        
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.proceed_to_setup)
        button_layout.addWidget(self.next_btn)
        
        layout.addLayout(button_layout)
    
    def add_note(self):
        """Add a timestamped note to the notes list."""
        note_text = self.notes_input.toPlainText().strip()
        if note_text:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.notes.append({
                "timestamp": timestamp,
                "note": note_text
            })
            self.notes_input.clear()
            QMessageBox.information(self, "Success", "Note added successfully!")
    
    def collect_metadata(self):
        """Collect and store all metadata."""
        try:
            # Collect user input
            subject_data = {
                "id": self.subject_id.text(),
                "age": self.subject_age.value(),
                "gender": self.subject_gender.currentText(),
                "vision_correction": self.vision_correction.currentText(),
                "dominant_eye": self.dominant_eye.currentText()
            }
            
            # Validate input
            if not self.validate_metadata(subject_data):
                return
            
            # Combine all metadata
            self.metadata = {
                "subject": subject_data,
                "session": {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "start_time": datetime.now().strftime("%H:%M:%S"),
                    "experimenter": self.experimenter_id.text()
                },
                "software": {
                    "app_version": self.data_manager.app_version,
                    "mediapipe_version": mp.__version__,
                    "opencv_version": cv2.__version__
                },
                "notes": self.notes
            }
            
            QMessageBox.information(self, "Success", "Metadata collected successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to collect metadata: {str(e)}")
            
    def validate_metadata(self, subject_data):
        """Validate the collected metadata."""
        if not subject_data["id"]:
            QMessageBox.warning(self, "Validation Error", "Subject ID is required!")
            return False
        if not self.experimenter_id.text():
            QMessageBox.warning(self, "Validation Error", "Experimenter ID is required!")
            return False
        return True
    
    def proceed_to_setup(self):
        """Save metadata and proceed to experiment setup."""
        if not hasattr(self, 'metadata') or not self.metadata:
            QMessageBox.warning(self, "Warning", "Please collect metadata first!")
            return
            
        try:
            # Create subject directory and save metadata
            subject_dir = self.data_manager.create_subject_directory(self.metadata["subject"]["id"])
            self.data_manager.save_metadata(subject_dir, self.metadata)
            
            # Launch setup window
            self.setup_window = SetupWindow(self.data_manager, subject_dir)
            self.setup_window.show()
            self.hide()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to proceed: {str(e)}")


def main():
    """Main function for testing the metadata window independently."""
    app = QApplication(sys.argv)
    
    # Create test data manager
    from data_manager import DataManager
    dm = DataManager()
    
    # Create and show the metadata window
    window = MainWindow(dm)
    window.show()
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())