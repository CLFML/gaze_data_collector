import sys
import platform
import wmi
import screeninfo
import cv2
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,  
                            QLineEdit, QComboBox, QPushButton, QFormLayout, QMessageBox, 
                            QSpinBox, QGroupBox, QTextEdit, QApplication)
from setup_window import SetupWindow

class SystemInfoCollector:
    """Utility class to collect system information automatically."""
    
    @staticmethod
    def get_laptop_info():
        """Collect laptop specifications."""
        try:
            w = wmi.WMI()
            system_info = w.Win32_ComputerSystem()[0]
            os_info = w.Win32_OperatingSystem()[0]
            cpu_info = w.Win32_Processor()[0]
            
            return {
                "manufacturer": system_info.Manufacturer,
                "model": system_info.Model,
                "os": f"{os_info.Caption} {os_info.OSArchitecture}",
                "processor": cpu_info.Name,
                "ram_gb": round(float(system_info.TotalPhysicalMemory) / (1024**3), 2),
                "hostname": platform.node()
            }
        except Exception as e:
            print(f"Error collecting laptop info: {str(e)}")
            return {}

    @staticmethod
    def get_camera_info():
        """Collect webcam specifications."""
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return {}
                
            camera_info = {
                "resolution": f"{int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}",
                "fps": int(cap.get(cv2.CAP_PROP_FPS)),
                "backend": cap.getBackendName()
            }
            
            # Try to get camera name using WMI
            try:
                w = wmi.WMI()
                for camera in w.Win32_PnPEntity():
                    if "camera" in str(camera.Caption).lower():
                        camera_info["model"] = camera.Caption
                        break
            except:
                pass
                
            cap.release()
            return camera_info
        except Exception as e:
            print(f"Error collecting camera info: {str(e)}")
            return {}

    @staticmethod
    def get_screen_info():
        """Collect screen specifications."""
        try:
            monitors = screeninfo.get_monitors()
            if not monitors:
                return {}
                
            primary_monitor = next((m for m in monitors if m.is_primary), monitors[0])
            return {
                "resolution": f"{primary_monitor.width}x{primary_monitor.height}",
                "size_mm": f"{primary_monitor.width_mm}x{primary_monitor.height_mm}",
                "refresh_rate": getattr(primary_monitor, 'refresh_rate', 'Unknown'),
                "scale_factor": getattr(primary_monitor, 'scale_factor', 1.0)
            }
        except Exception as e:
            print(f"Error collecting screen info: {str(e)}")
            return {}

class MainWindow(QMainWindow):
    """Main window for collecting metadata and starting the experiment."""
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.metadata = {}
        self.notes = []
        self.system_info = {}
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the main UI components."""
        self.setWindowTitle("Gaze Estimation Data Collection")
        self.setMinimumSize(800, 800)
        
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

        # System Information Preview
        system_group = QGroupBox("System Information (Auto-detected)")
        system_layout = QVBoxLayout()
        self.system_info_text = QTextEdit()
        self.system_info_text.setReadOnly(True)
        system_layout.addWidget(self.system_info_text)
        collect_metadata_btn = QPushButton("Collect System Metadata")
        collect_metadata_btn.clicked.connect(self.collect_metadata)
        system_layout.addWidget(collect_metadata_btn)
        system_group.setLayout(system_layout)
        layout.addWidget(system_group)
        
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
            
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.proceed_to_setup)
        self.next_btn.setEnabled(False)  # Disable until metadata is collected
        button_layout.addWidget(self.next_btn)
        
        layout.addLayout(button_layout)
        
        # Automatically collect system metadata on startup
        QApplication.processEvents()
        
    def collect_metadata(self):
        """Collect and store all metadata including system information."""
        try:
            # Collect system information
            self.system_info = {
                "laptop": SystemInfoCollector.get_laptop_info(),
                "camera": SystemInfoCollector.get_camera_info(),
                "screen": SystemInfoCollector.get_screen_info()
            }
            
            # Update system info preview
            self.update_system_info_preview()
            
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
                "equipment": {
                    "laptop": self.system_info["laptop"],
                    "camera": self.system_info["camera"],
                    "screen": self.system_info["screen"]
                },
                "software": {
                    "app_version": self.data_manager.app_version,
                    "opencv_version": cv2.__version__,
                    "python_version": platform.python_version(),
                    "os_platform": platform.platform()
                },
                "notes": self.notes
            }
            
            self.next_btn.setEnabled(True)
            QMessageBox.information(self, "Success", "Metadata collected successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to collect metadata: {str(e)}")
            
    def update_system_info_preview(self):
        """Update the system information preview text."""
        preview_text = "Detected System Information:\n\n"
        
        if self.system_info.get("laptop"):
            laptop = self.system_info["laptop"]
            preview_text += "Laptop:\n"
            preview_text += f"- Model: {laptop.get('manufacturer', 'Unknown')} {laptop.get('model', 'Unknown')}\n"
            preview_text += f"- OS: {laptop.get('os', 'Unknown')}\n"
            preview_text += f"- CPU: {laptop.get('processor', 'Unknown')}\n"
            preview_text += f"- RAM: {laptop.get('ram_gb', 'Unknown')} GB\n\n"
        
        if self.system_info.get("camera"):
            camera = self.system_info["camera"]
            preview_text += "Camera:\n"
            preview_text += f"- Model: {camera.get('model', 'Unknown')}\n"
            preview_text += f"- Resolution: {camera.get('resolution', 'Unknown')}\n"
            preview_text += f"- FPS: {camera.get('fps', 'Unknown')}\n\n"
        
        if self.system_info.get("screen"):
            screen = self.system_info["screen"]
            preview_text += "Screen:\n"
            preview_text += f"- Resolution: {screen.get('resolution', 'Unknown')}\n"
            preview_text += f"- Physical Size: {screen.get('size_mm', 'Unknown')} mm\n"
            preview_text += f"- Refresh Rate: {screen.get('refresh_rate', 'Unknown')} Hz\n"
        
        self.system_info_text.setText(preview_text)
    
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
    
    from data_manager import DataManager
    dm = DataManager()
    
    window = MainWindow(dm)
    window.show()
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())