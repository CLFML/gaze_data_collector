# Data Collection Protocol for Gaze Direction Estimation

  ## Equipment setup
  - Laptop with high-quality webcam (1080p or higher)
  - Python app for experiment management (Laptop/computer for running the gaze pattern display application)
  - Consistent room lighting
  - Laptop plan printed on A3 for Yaw: 0°, ±15°, ±30°
  - Phone app for setting camera pitch: 0°, ±15°, ±30°
  - Laser distance meter for subject-to-screen distance measurement

## Experimental procedure

1. Launch Python App
   - Open the gaze estimation experiment app on the laptop

2. Enter session metadata
   - Input experimenter name, date, and session ID
   - Enter subject details (age, gender, vision correction, dominant eye, etc.)

3. Subject preparation
   - Seat the subject at the designated distance from the laptop
   - Explain the experiment process and obtain consent

4. Camera angle setup
   - Follow app instructions for setting initial pitch and yaw camera angle
   - Use digital angle meter to verify and adjust the pitch angle as needed

5. Calibration
   - Run the app's calibration routine (not sure what that is right now?)
   - Ensure successful calibration before proceeding

6. Data collection
   - Start the gaze pattern sequence as prompted by the app
   - Monitor subject comfort and data quality in real-time

7. Angle changes
   - Follow app prompts for changing camera angles
   - Verify new angles with the digital meter
   - Recalibrate after each angle change


## Data storage and organization

Data is stored according to this folder structure:

```
YYYYMMDD_GazeEstimationExperiment/
└── SubjectID/
    ├── Metadata.json
    └── AngleSetups/
        ├── Y00_P00/
        │   ├── LandmarkData.csv
        │   └── ExperimentData.csv
        ├── Y15_P-15/
        │   ├── LandmarkData.csv
        │   └── ExperimentData.csv
        └── ... (other angle combinations)
```
Where:
- YYYYMMDD: Date of the experiment
- SubjectID: Unique identifier for the subject (e.g., S001, S002)
- ExperimentType: Short code for the experiment type (e.g., GP for Gaze Patterns)
- YawAngle: Yaw angle of the camera (e.g., Y00, Y15, Y-30)
- PitchAngle: Pitch angle of the camera (e.g., P00, P-15, P30)

Metadata.json could look like this:
```json
{
  "subject": {
    "id": "S001",
    "age": 28,
    "gender": "Female",
    "vision_correction": "Contact lenses",
    "dominant_eye": "Right",
    "medical_conditions": "None"
  },
  "session": {
    "date": "2023-10-22",
    "start_time": "14:30:00",
    "end_time": "16:15:00",
    "experimenter": "John Doe"
  },
  "equipment": {
    "webcam": {
      "model": "Logitech C920",
      "resolution": "1920x1080",
      "frame_rate": 30
    },
    "screen": {
      "size": "15.6 inches",
      "resolution": "1920x1080"
    },
    "laptop": {
      "model": "Dell XPS 15",
      "os": "Windows 10"
    }
  },
  "environment": {
    "lighting": "Controlled, 500 lux",
    "room_temperature": "22°C"
  },
  "setup": {
    "head_to_screen_distance": 60,
    "camera_to_screen_distance": 2,
    "distance_unit": "cm"
  },
  "experiment": {
    "total_duration": 105,
    "duration_unit": "minutes",
    "number_of_angle_setups": 25,
    "breaks_taken": 4
  },
  "angle_setups": [
    {
      "order": 1,
      "yaw": 0,
      "pitch": 0,
      "roll": 0,
      "angle_unit": "degrees",
      "start_time": "14:35:00",
      "end_time": "14:39:00",
      "calibration_accuracy": 0.95
    },
    {
      "order": 2,
      "yaw": 15,
      "pitch": -15,
      "roll": 0,
      "angle_unit": "degrees",
      "start_time": "14:41:00",
      "end_time": "14:45:00",
      "calibration_accuracy": 0.93
    }
  ],
  "notes": [
    {
      "timestamp": "14:50:00",
      "note": "Subject reported slight eye strain, took a 5-minute break"
    },
    {
      "timestamp": "15:30:00",
      "note": "Recalibrated due to subject movement"
    }
  ],
  "data_files": {
    "base_path": "YYYYMMDD_GazeEstimationExperiment/S001/",
    "angle_setups": [
      {
        "folder": "Y00_P00",
        "landmark_file": "LandmarkData.csv",
        "experiment_file": "ExperimentData.csv"
      },
      {
        "folder": "Y15_P-15",
        "landmark_file": "LandmarkData.csv",
        "experiment_file": "ExperimentData.csv"
      }
    ]
  },
  "software": {
    "app_version": "1.0.3",
    "mediapipe_version": "0.8.9"
  }
}
```




## Data to Record

1. Facial Landmarks
   - 468 3D facial landmarks from MediaPipe Face Mesh
   - Iris landmarks from MediaPipe Iris model

2. Subject Metadata
   - Age
   - Gender
   - Presence of vision correction (glasses/contacts)

3. Additional Data to Record
   - Head-to-screen distance (measured at the start of each session)
   - Screen size and resolution
   - Webcam model and settings (e.g., frame rate, resolution)
   - Room lighting conditions (e.g., lux level if measurable)
   - Time and date of the experiment
   - Subject's dominant eye
   - Any relevant medical conditions affecting vision or eye movement
   - Experiment duration
   - Breaks taken during the experiment
   - Experimenter's name or ID

4. Experiment-specific Data
   - Gaze target coordinates and timestamps
   - Head pose estimation (if available from MediaPipe)
   - Blink detection timestamps
   - Calibration data (e.g., accuracy metrics from the 9-point calibration)

5. Qualitative Data
   - Subject's comfort level during the experiment (pre and post)
   - Any issues or anomalies noticed during the session

## Standardized Naming Convention

Use the following format for naming your data files:

`YYYYMMDD_SubjectID_ExperimentType_DataType.csv`

Where:
- `YYYYMMDD`: Date of the experiment
- `SubjectID`: Unique identifier for the subject (e.g., S001, S002)
- `ExperimentType`: Short code for the experiment type (e.g., GP for Gaze Patterns)
- `DataType`: Type of data in the file (e.g., LM for Landmarks, MD for Metadata)

Examples:
- `20231021_S001_GP_LM.csv` (Landmark data for Subject 001 on October 21, 2023)
- `20231021_S001_GP_MD.csv` (Metadata for Subject 001 on October 21, 2023)

## Data Storage and Organization

1. Create a main experiment folder with the date and experiment name.
2. Within this folder, create subfolders for each subject.
3. Store all files related to a subject in their respective folder.
4. Keep a master spreadsheet linking SubjectIDs to their metadata for easy reference.

## Data Backup

1. Implement a regular backup system for all collected data.
2. Store backups in a separate physical location or secure cloud storage.
3. Ensure all data is anonymized before backing up or sharing.

