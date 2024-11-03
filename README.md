# Gaze Estimation Experiment Application

This application collects facial landmark data for gaze estimation research using MediaPipe and OpenCV. 
It provides a complete workflow for conducting multi-trial gaze estimation experiments with multiple subjects.


Note: This application is designed for Windows systems only.

## Features

### Data Collection
- MediaPipe face mesh detection with iris landmarks
- Real-time visualization of facial and iris landmarks
- Automatic data organization by subject and trial
- Support for multiple trials per subject
- Progress tracking for experimental combinations

### Experimental Setup
- Configurable camera angles, e.g.:
  - Yaw: 0°, ±15°, ±30°
  - Pitch: 0°, ±15°, ±30°
- Multiple subject distances, e.g.: 30cm, 60cm, 90cm
- Real-time face detection validation
- Visual feedback for proper subject positioning

### Experiment Workflow
1. Metadata Collection
   - Experimenter information
   - Subject demographics
   - Vision information
   - Session notes
   - Automatic system information collection

2. Trial Setup
   - Live landmark visualization
   - Camera angle guidance
   - Distance verification
   - Setup validation
   - Progress tracking
   - Prevents duplicate angle/distance combinations

3. Gaze Data Collection
   - 3x3 grid dot display
   - Randomized dot presentation
   - Configurable display and rest times
   - Automatic landmark recording
   - Trial-by-trial data saving

4. Session Management
   - Multiple trials per subject
   - New subject initialization
   - Session continuation options
   - Progress tracking
   - Session summary   

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd gaze-estimation-app
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python main.py
```

2. Experiment Workflow:
   a. Enter experimenter and subject information
   b. Configure camera setup (angle and distance)
   c. Validate setup using landmark visualization
   d. Run the trial
   e. Choose to:
      - Continue with next trial
      - Start new subject
      - End session

## Project Structure

```
gaze-data_collector/
├── main.py                 # Application entry point
├── metadata_window.py      # Subject and experimenter data collection
├── setup_window.py         # Camera and position setup
├── experiment_window.py    # Gaze data collection
├── data_manager.py         # Data organization and storage
├── requirements.txt        # Project dependencies
└── README.md               # Documentation
```

## Data Structure

Data is organized as follows:
```
YYYYMMDD_GazeEstimationExperiment/
└── SubjectID/
    ├── Metadata.json           # Subject and session information
    ├── Trial_001/
    │   ├── setup_config.json   # Camera angles and distance
    │   └── landmark_data.csv   # MediaPipe outputs, dot positions and timestamps
    ├── Trial_002/
    └── ...
```

### Data Files

1. Metadata.json
   - Subject demographics
   - Experimenter information
   - Session timestamp
   - Software versions
   - Session notes

2. setup_config.json
   - Trial identifier
   - Camera angles (yaw, pitch)
   - Subject distance
   - Experiment parameters

3. landmark_data.csv
   - Timestamps
   - 468 facial landmarks (x, y, z)
   - Iris landmarks
   - Target dot positions

## Requirements

- Windows 10 or later
- Python 3.8 or higher
- High-quality webcam (1080p recommended)
- Digital inclinometer for angle measurement
- Screen size measurement tools
- Distance measurement tools
- Adequate lighting conditions

## Technical Dependencies

- OpenCV
- MediaPipe
- PyQt5
- NumPy
- Screeninfo

## Experimental Details

### Camera Angles
- Yaw: 0°, ±15°, ±30°
- Pitch: 0°, ±15°, ±30°
- Total angle combinations: 25

### Subject Distances
- Near: 30cm
- Medium: 60cm
- Far: 90cm

### Gaze Target
- 3x3 grid pattern
- Randomized presentation
- 2-second display time
- 1-second rest period

## Best Practices

1. Environment Setup
   - Consistent lighting
   - Minimal background distractions
   - Stable camera mounting

2. Subject Positioning
   - Use distance markers
   - Verify face is centered
   - Check iris detection quality

3. Data Collection
   - Validate setup before each trial
   - Monitor landmark detection quality
   - Allow breaks between trials
   - Save data frequently

## License

This work is licensed under the Apache 2.0 license.