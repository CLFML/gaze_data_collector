# Data Collection Protocol for Gaze Direction Estimation

## Equipment Setup
- Laptop with high-quality webcam (1080p recommended)
- Python app for experiment management
- Adjustable laptop stand or mount
- Digital inclinometer for angle measurement
- Distance measurement tools (e.g., laser distance meter)
- Screen size measurement tools
- Consistent room lighting
- Adequate background for face detection

## Python App Features
- User-friendly interface for experiment management
- Real-time facial landmark visualization
- Progress tracking for experimental combinations
- Automatic data organization
- Session progress monitoring
- Data quality validation

## Experimental Procedure

1. Launch Application
   ```bash
   python main.py
   ```

2. Enter Session Metadata (via Metadata Window)
   - Experimenter ID and information
   - Subject demographics
   - Vision information (correction type, dominant eye)
   - Session notes
   - Software automatically records system information

3. Subject Preparation
   - Position subject at designated distance (30cm, 60cm, or 90cm)
   - Explain experiment process and obtain consent
   - Verify adequate lighting conditions
   - Ensure minimal background distractions

4. Camera Setup (via Setup Window)
   - Select camera angles:
     - Yaw: 0°, ±15°, ±30°
     - Pitch: 0°, ±15°, ±30°
   - Select subject distance
   - Use Setup Window's live preview to verify:
     - Face detection quality
     - Landmark visualization
     - Iris detection
   - Validate setup using the "Validate Setup" button

5. Trial Execution (via Experiment Window)
   - System displays 3x3 grid of points
   - Random dot presentation
   - 2-second display time per point
   - 1-second rest period between points
   - Real-time data collection of:
     - 468 facial landmarks
     - Iris positions
     - Target dot positions
     - Timestamps

6. Post-Trial Options
   - Continue with next trial
   - Start new subject
   - End session

## Data Structure

```
YYYYMMDD_GazeEstimationExperiment/
└── SubjectID/
    ├── Metadata.json           # Subject and session information
    ├── Trial_001/
    │   ├── setup_config.json   # Camera angles and distance
    │   ├── landmark_data.csv   # MediaPipe outputs
    │   └── experiment_data.csv # Dot positions and timestamps
    ├── Trial_002/
    └── ...
```

### Data Files Content

1. Metadata.json
   - Subject information (ID, age, gender, vision correction, dominant eye)
   - Session details (date, times, experimenter)
   - Equipment specifications (webcam, screen, laptop)
   - Environmental conditions
   - Setup measurements
   - Session notes

2. setup_config.json
   - Trial identifier
   - Timestamp
   - Camera setup (yaw, pitch, distance)
   - Experiment parameters (dot display time, rest time, grid size)

3. landmark_data.csv
   - Timestamps
   - Target coordinates
   - 468 facial landmarks (x, y, z coordinates)
   - Iris landmark positions

## Quality Control

1. Real-time Validation
   - Face detection verification
   - Landmark quality monitoring
   - Setup validation before each trial
   - Prevention of duplicate angle/distance combinations

2. Data Quality Checks
   - Automatic validation of setup parameters
   - Real-time monitoring of landmark detection
   - Face positioning feedback
   - Trial completion verification

3. Progress Tracking
   - Total combinations completed
   - Remaining combinations display
   - Trial count per subject
   - Session duration monitoring

## Best Practices

1. Environment Setup
   - Ensure consistent lighting
   - Minimize background distractions
   - Use stable camera mounting
   - Maintain constant room temperature

2. Subject Positioning
   - Use distance markers
   - Verify face centering
   - Monitor subject comfort
   - Allow breaks as needed

3. Data Collection
   - Validate setup before each trial
   - Monitor landmark detection quality
   - Save data after each trial
   - Document any anomalies
   - Take regular breaks
   - Keep detailed session notes

## Troubleshooting

Common issues and solutions:
- Poor face detection: Adjust lighting, check background, reposition subject
- Failed setup validation: Verify camera angles, check distance measurements
- Data saving errors: Check storage space, verify file permissions
- System performance: Close unnecessary applications, monitor resource usage

## Data Backup

- Automatic data saving after each trial
- Organized file structure for easy backup
- Recommendation to backup data after each session
- Maintain multiple copies of data in secure locations
