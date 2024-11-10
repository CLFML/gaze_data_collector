import sys
from datetime import datetime
import random
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                            QPushButton, QMessageBox, QApplication)
from PyQt5.QtCore import Qt, QTimer, QPoint, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen
import cv2
import mediapipe as mp

class ExperimentWindow(QWidget):
    """Window for providing stimuli and running the gaze experiment and collecting data."""
    finished = pyqtSignal()
    
    def __init__(self, data_manager, trial_dir, trial_config, parent=None):
        """
        Initialize the experiment window.
        
        Args:
            data_manager: DataManager instance for saving data
            trial_dir: Path object pointing to the trial directory
            trial_config: Dictionary containing trial configuration
            parent: Parent widget
        """
        super().__init__(parent)
        self.data_manager = data_manager
        self.trial_dir = trial_dir
        self.trial_config = trial_config
        
        # Initialize experimental state
        self.camera = None
        self.mp_face_mesh = None
        self.current_dot_position = None
        self.landmarks_data = []
        self.is_center_point = False

        # Get parameters from trial config
        conditions = trial_config['conditions']
        self.dot_radius = conditions['dot_radius']
        self.dot_display_time = conditions['dot_display_time']
        self.rest_time = conditions['rest_time']
        self.grid_size = conditions['grid_size']
        
        # Generate grid points
        self.grid_points = self.generate_grid_points()
        self.remaining_points = self.grid_points.copy()

        # Find center point coordinates
        self.center_point = self.calculate_center_point()        
        
        # Setup UI and start experiment
        self.setup_ui()
        self.setup_mediapipe()
        self.setup_camera()

    def calculate_center_point(self):
        """Calculate the coordinates of the center point based on grid size."""
        margin_h = 0.1
        margin_v = 0.1
        available_width = 1 - (2 * margin_h)
        available_height = 1 - (2 * margin_v)
        
        # Calculate center coordinates
        center_x = margin_h + (available_width / 2)
        center_y = margin_v + (available_height / 2)
        
        return (center_x, center_y)        
        
    def setup_ui(self):
        """Initialize the UI components."""
        # Make window fullscreen
        self.showFullScreen()
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Add exit button (small, in corner)
        exit_btn = QPushButton("Exit (Esc)", self)
        exit_btn.clicked.connect(self.close)
        exit_btn.setFixedSize(100, 30)
        exit_btn.move(10, 10)
        
        # Status label
        self.status_label = QLabel("Preparing experiment...", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: gray; font-size: 24px;")
        layout.addWidget(self.status_label)
        
    def setup_mediapipe(self):
        """Initialize MediaPipe face mesh."""
        self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
    def setup_camera(self):
        """Initialize the camera and start capture."""
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            QMessageBox.critical(self, "Error", "Failed to open camera!")
            self.close()
            return
        
        # Start timers for camera capture and experiment
        self.capture_timer = QTimer()
        self.capture_timer.timeout.connect(self.process_frame)
        self.capture_timer.start(33)  # ~30 fps
        
        # Start experiment
        QTimer.singleShot(1000, self.start_experiment)
        
    def generate_grid_points(self):
        """Generate grid points for dot display with margins."""
        points = []
        
        # Define margins as percentage of screen dimensions
        margin_h = 0.1  # margin from left and right edges
        margin_v = 0.1  # margin from top and bottom edges
        
        # Calculate available space
        available_width = 1 - (2 * margin_h)
        available_height = 1 - (2 * margin_v)
        
        # Calculate step sizes
        step_x = available_width / (self.grid_size - 1)
        step_y = available_height / (self.grid_size - 1)
        
        # Generate points
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x = margin_h + (i * step_x)
                y = margin_v + (j * step_y)
                points.append((x, y))
                
        return points
        
    def start_experiment(self):
        """Start the experiment sequence."""
        msg = QMessageBox.information(self, "Experiment Instructions",
                                      """During this experiment:
• You will see dots on the screen
• Look at each dot until it disappears
• Smile when you see a green dot
• A rest period will occur between dots
• The experiment takes about 1 minute
Click OK when you're ready to begin.""")

        self.status_label.setText("Experiment starting...")
        self.show_next_dot()

    def show_next_dot(self):
        """Display the next dot in the sequence."""
        if not self.remaining_points:
            self.finish_experiment()
            return
            
        # Select random point from remaining points
        point_idx = random.randint(0, len(self.remaining_points) - 1)
        self.current_dot_position = self.remaining_points.pop(point_idx)
        
        # Check if this is the center point
        self.is_center_point = (self.current_dot_position == self.center_point)
        
        # Update status with smile request if center point
        points_left = len(self.remaining_points)
        total_points = len(self.grid_points)
        status_text = "\n😊 smile! 😊" if self.is_center_point else "" # f"Please look at the dot ({total_points - points_left}/{total_points})"
        self.status_label.setText(status_text)
        
        # Schedule next dot
        QTimer.singleShot(self.dot_display_time, self.rest_period)
        
        # Force repaint to show new dot
        self.update()
        
    def rest_period(self):
        """Insert a rest period between dots."""
        self.current_dot_position = None
        # self.status_label.setText("Rest...")
        self.update()
        
        QTimer.singleShot(self.rest_time, self.show_next_dot)
        
    def process_frame(self):
        """Process each camera frame and extract landmarks."""
        if self.camera is None or self.current_dot_position is None:
            return
            
        ret, frame = self.camera.read()
        if not ret:
            return
            
        # Process frame with MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.mp_face_mesh.process(frame_rgb)
        
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0]
            
            # Record timestamp and current dot position
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            dot_x = self.current_dot_position[0] * self.width()
            dot_y = self.current_dot_position[1] * self.height()
            
            # Prepare landmark data
            landmark_row = [timestamp, dot_x, dot_y]
            
            # Add all landmark coordinates
            for landmark in landmarks.landmark:
                landmark_row.extend([landmark.x, landmark.y, landmark.z])
            
            self.landmarks_data.append(landmark_row)
        
    def paintEvent(self, event):
        """Handle painting of the dot."""
        super().paintEvent(event)
        
        if self.current_dot_position is None:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw dot with white border
        x = self.current_dot_position[0] * self.width()
        y = self.current_dot_position[1] * self.height()
        
        # Draw white border
        painter.setPen(QPen(QColor(255, 255, 255), 3))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QPoint(int(x), int(y)), self.dot_radius + 2, self.dot_radius + 2)
        
        # Draw dot - green for center point, red for others
        color = QColor(0, 255, 0) if self.is_center_point else QColor(255, 0, 0)
        painter.setPen(QPen(color, 2))
        painter.setBrush(color)
        painter.drawEllipse(QPoint(int(x), int(y)), self.dot_radius, self.dot_radius)
        
    def finish_experiment(self):
        """Save data and clean up."""
        self.status_label.setText("Saving data...")
        
        try:
            # Create header row
            header = ["timestamp", "target_x", "target_y"]
            for i in range(468):  # MediaPipe face mesh has 468 landmarks
                header.extend([f"landmark_{i}_x", f"landmark_{i}_y", f"landmark_{i}_z"])
            
            # Save landmarks data
            self.data_manager.save_landmark_data(
                self.trial_dir,
                self.landmarks_data,
                header
            )
            
            QMessageBox.information(self, "Success", 
                                  "Experiment completed successfully!")
            self.finished.emit()
            self.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", 
                               f"Failed to save experiment data: {str(e)}")
            self.close()
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Escape:
            self.close()
            
    def closeEvent(self, event):
        """Clean up resources when window is closed."""
        if self.camera is not None:
            self.camera.release()
        if self.mp_face_mesh is not None:
            self.mp_face_mesh.close()
        if hasattr(self, 'capture_timer'):
            self.capture_timer.stop()
        event.accept()


def main():
    """Main function for testing the ExperimentWindow independently."""
    app = QApplication(sys.argv)
    
    # Create test data manager and directories
    from data_manager import DataManager
    dm = DataManager()
    subject_dir = dm.create_subject_directory("001")
    trial_dir = dm.create_trial_directory(subject_dir)
    
    # Create test configuration
    test_config = {
        "trial_id": "001",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "setup": {
            "yaw": 15,
            "pitch": -15,
            "distance": 60
        },
        "conditions": {
            "dot_display_time": 2000,
            "rest_time": 1000,
            "grid_size": 3,
            "dot_radius": 15
        }
    }
    
    # Create and show the experiment window
    window = ExperimentWindow(dm, trial_dir, test_config)
    window.show()
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
