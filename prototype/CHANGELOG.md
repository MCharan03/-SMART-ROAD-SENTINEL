# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-11-18

### Added
- Initial project setup.
- Created `CHANGELOG.md` to document project changes.
- Established the initial project plan based on the "SMART ROAD SENTINEL" presentation.
- Created `requirements.txt` and `README.md` for the car software environment setup.
- Created `main.py` with a basic Kivy UI structure for the car software.
- Added `gps_module.py` to simulate GPS data.
- Added `cloud_storage.py` to handle Firebase integration.
- Created `requirements.txt` and `README.md` for the ML model training environment.
- Created `data.yaml` for YOLOv8 dataset configuration.
- Created `train.py` for YOLOv8 model training.
- Created `predict.py` for YOLOv8 model prediction.
- Created `requirements.txt` and `README.md` for the backend environment.
- Created `app.py` and `templates` directory for the basic Flask application.
- Created `index.html` for the dashboard frontend.
- Created `split_dataset.py` to split the dataset into train, val, and test sets.

### Changed
- Set up the project directory structure with folders for `car-software`, `ml-model`, `backend`, and `docs`.
- Integrated live camera feed into the car software using OpenCV.
- Replaced basic alert label with a more advanced `AlertBox` overlay.
- Integrated GPS data into the main application to display live coordinates.
- Implemented local storage system to save captured images and metadata.
- Integrated Firebase to upload captured data to cloud storage.
- Downloaded and placed the road damage dataset in `ml-model/dataset`.
- Integrated the YOLOv8 ML model into the car software for real-time defect detection, including alerts and bounding box display.
- Implemented Firebase Firestore data fetching in the Flask backend.
- Integrated a Leaflet map into the dashboard to visualize defect locations.
- Split the dataset into training, validation, and test sets.
