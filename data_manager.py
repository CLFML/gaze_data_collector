import json
import csv
from datetime import datetime
import shutil
import logging
from pathlib import Path

class DataManager:
    """Handles all data saving and organization for the gaze estimation experiment."""
    
    def __init__(self, base_directory=None, app_version='1.0.0'):
        """
        Initialize the data manager.
        
        Args:
            base_directory: Optional path to base directory
            app_version: Version string for the application
        """
        # Store app version
        self.app_version = app_version
        
        # Set up base directory
        if base_directory is None:
            self.base_directory = self._create_base_directory()
        else:
            self.base_directory = Path(base_directory)
            
        # Set up logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Configure logging for the data manager."""
        log_file = self.base_directory / 'experiment.log'
        logging.basicConfig(
            filename=str(log_file),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def _create_base_directory(self):
        """Create the base directory with current date."""
        current_date = datetime.now().strftime("%Y%m%d")
        base_dir = Path(f"{current_date}_GazeEstimationExperiment")
        base_dir.mkdir(parents=True, exist_ok=True)
        return base_dir
    
    def create_subject_directory(self, subject_id):
        """Create directory structure for a new subject."""
        try:
            # Create subject directory with padded ID
            subject_dir = self.base_directory / f"S{str(subject_id).zfill(3)}"
            subject_dir.mkdir(exist_ok=True)
            
            logging.info(f"Created directory structure for subject {subject_id}")
            return subject_dir
            
        except Exception as e:
            logging.error(f"Error creating subject directory: {str(e)}")
            raise
    
    def create_trial_directory(self, subject_dir):
        """Create a new trial directory with incrementing trial number."""
        try:
            # Find existing trial directories
            existing_trials = list(subject_dir.glob("Trial_*"))
            trial_num = len(existing_trials) + 1
            
            # Create new trial directory
            trial_dir = subject_dir / f"Trial_{str(trial_num).zfill(3)}"
            trial_dir.mkdir(exist_ok=True)
            
            logging.info(f"Created trial directory: {trial_dir}")
            return trial_dir
            
        except Exception as e:
            logging.error(f"Error creating trial directory: {str(e)}")
            raise
    
    def save_metadata(self, subject_dir, metadata):
        """Save subject metadata to JSON file."""
        try:
            metadata_file = subject_dir / "Metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logging.info(f"Saved metadata to {metadata_file}")
            
        except Exception as e:
            logging.error(f"Error saving metadata: {str(e)}")
            raise
    
    def save_trial_config(self, trial_dir, config):
        """Save trial configuration including setup parameters."""
        try:
            config_file = trial_dir / "setup_config.json"
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            logging.info(f"Saved trial configuration to {config_file}")
            
        except Exception as e:
            logging.error(f"Error saving trial configuration: {str(e)}")
            raise
    
    def save_landmark_data(self, trial_dir, landmarks_data, column_names):
        """Save landmarks data to CSV file."""
        try:
            landmarks_file = trial_dir / "landmark_data.csv"
            with open(landmarks_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(column_names)
                writer.writerows(landmarks_data)
            
            logging.info(f"Saved landmarks data to {landmarks_file}")
            
        except Exception as e:
            logging.error(f"Error saving landmarks data: {str(e)}")
            raise
    
    def save_experiment_data(self, trial_dir, data):
        """Save experiment-specific data to CSV file."""
        try:
            experiment_file = trial_dir / "experiment_data.csv"
            with open(experiment_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(data['headers'])
                writer.writerows(data['rows'])
            
            logging.info(f"Saved experiment data to {experiment_file}")
            
        except Exception as e:
            logging.error(f"Error saving experiment data: {str(e)}")
            raise

    def get_trial_count(self, subject_dir):
        """Get the number of existing trials for a subject."""
        try:
            return len(list(subject_dir.glob("Trial_*")))
        except Exception as e:
            logging.error(f"Error counting trials: {str(e)}")
            return 0

    def backup_data(self, backup_path):
        """Create a backup of all experiment data."""
        try:
            backup_dir = Path(backup_path)
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"GazeEstimation_Backup_{timestamp}"
            backup_path = backup_dir / backup_name
            
            shutil.copytree(self.base_directory, backup_path)
            
            logging.info(f"Created backup at {backup_path}")
            return backup_path
            
        except Exception as e:
            logging.error(f"Error creating backup: {str(e)}")
            raise

def main():
    """Test the DataManager functionality."""
    dm = DataManager()
    
    try:
        # Test subject creation
        subject_dir = dm.create_subject_directory("001")
        
        # Test metadata saving
        test_metadata = {
            "subject": {
                "id": "001",
                "age": 25,
                "gender": "Female"
            },
            "session": {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "experimenter": "Test"
            }
        }
        dm.save_metadata(subject_dir, test_metadata)
        
        # Test trial creation and data saving
        trial_dir = dm.create_trial_directory(subject_dir)
        
        # Test trial config saving
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
        dm.save_trial_config(trial_dir, test_config)
        
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"Test failed: {str(e)}")

if __name__ == "__main__":
    main()