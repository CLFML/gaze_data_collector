import sys
from PyQt5.QtWidgets import QApplication
from data_manager import DataManager
import os
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

        # # Add QMessageBox style
        # self.app.setStyleSheet("""
        #     QMessageBox {
        #         font-size: 14pt;
        #     }
        #     QMessageBox QPushButton {
        #         font-size: 14pt;
        #         padding: 5px 20px;
        #     }
        # """)

        # Set global font size for all UI elements
        base_font_size = 14  # Adjust this single value to scale all UI elements
        
        # Apply global stylesheet with the base font size
        self.app.setStyleSheet(f"""
            * {{
                font-size: {base_font_size}pt;
            }}
            
            /* Preserve relative scaling for headers and special elements */
            QGroupBox {{
                font-size: {base_font_size + 1}pt;
                font-weight: bold;
                padding-top: 15px;
            }}
            
            QPushButton {{
                padding: 8px 15px;
                min-height: 30px;
            }}
            
            QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
                padding: 5px;
                min-height: 30px;
            }}
        """)        
        
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
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow logging

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
