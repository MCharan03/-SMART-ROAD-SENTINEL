# SMART ROAD SENTINEL - Comprehensive Project Documentation

This document provides a detailed explanation of the SMART ROAD SENTINEL project, covering its architecture, functionality, operation, and maintenance.

## 1. Project Overview

**SMART ROAD SENTINEL** is a comprehensive system designed to automate the process of road defect detection and reporting. It uses a car-mounted system to capture real-time video of the road, an AI model to detect defects like potholes and cracks, and a web-based dashboard to visualize the location and details of these defects.

The primary goal is to improve the efficiency and speed of road maintenance by providing an accurate, near real-time log of road damage, complete with GPS coordinates and visual evidence.

The project is built on a modern technology stack, including Python for the backend and in-car software, a YOLOv8 AI model for object detection, and a React/TypeScript frontend for the user-facing dashboard.

---

## 2. Core Components

The project is divided into four main directories, each housing a distinct component of the system:

1.  **`car-software`**: This is the in-car data acquisition unit. It's a Python application that runs on a computer inside the vehicle. Its job is to capture camera feed, run the AI model, and upload findings.
2.  **`ml-model`**: This directory contains everything related to the Artificial Intelligence model, including the training scripts, dataset configuration, and the trained model weights.
3.  **`backend`**: This is the central server that acts as the bridge between the data collected by the car and the user dashboard. It provides an API for the frontend to consume.
4.  **`frontend`**: This is the web dashboard that users interact with. It visualizes the collected data on a map and in a table, and displays key analytics.

---

## 3. System Architecture & Data Flow (How it's Connected)

The four components work together in a continuous loop. Here is the step-by-step data flow from detection to visualization:

1.  **Data Acquisition (`car-software`):**
    *   The `main.py` script in the `car-software` directory is executed in the car.
    *   It uses `OpenCV` to capture a live video feed from a connected camera.
    *   Simultaneously, the `GPSSimulator` generates a continuous stream of GPS coordinates (latitude and longitude) to simulate the car's movement.
    *   Frame by frame, the video feed is passed to the `DetectionEngine`.

2.  **AI Inference (`car-software`):**
    *   The `DetectionEngine` loads a pre-trained YOLOv8 model (`best.pt`) specified in `config.py`.
    *   It runs an inference on the current video frame to detect road defects (e.g., 'Pothole', 'Crack'). The model outputs the class of the defect, a confidence score, and the bounding box coordinates on the image.

3.  **Data Packaging & Upload (`car-software`):**
    *   If a defect is detected, the `main.py` script packages the relevant data:
        *   The current video frame is saved as a JPG image.
        *   The GPS coordinates (`latitude`, `longitude`).
        *   The current `timestamp`.
        *   A list of all defects detected in that frame.
    *   This data is then uploaded to a **Google Firebase** project using the `CloudStorage` module. The image is uploaded to Firebase Storage, and the metadata (GPS, timestamp, defect details, image URL) is saved as a new document in a **Firestore** database collection named `road_data`.

4.  **Data Processing & API (`backend`):**
    *   The `backend/server.py` (a FastAPI application) runs on a server.
    *   The frontend dashboard calls the `/api/status` endpoint on this server every 2 seconds.
    *   When called, the endpoint connects to the same Google Firebase project.
    *   It queries the `road_data` collection in Firestore, fetching the 50 most recent defect documents.
    *   It then transforms this raw data into a clean, flat list of individual defects, which is more suitable for the frontend.

5.  **Data Visualization (`frontend`):**
    *   The `frontend` (a React application) receives the list of defects and telemetry data from the backend's API.
    *   The `DefectsContext` manages this state.
    *   The `Roadmap` component uses the latitude and longitude of each defect to plot markers on an interactive map (Leaflet).
    *   The `DefectTable` component displays the same data in a sortable, filterable grid.
    *   The `AnalyticsWidgets` component displays high-level statistics like total defects and defects found today.

---

## 4. How it Functions (Component Deep Dive)

### Car Software (`car-software`)
*   **`main.py`**: The heart of the application. It uses the Kivy framework to create a simple graphical user interface that displays the camera feed. It orchestrates all other modules.
*   **`detection.py` (`DetectionEngine`):** This class is responsible for loading the YOLOv8 model from the path in `config.py` and running inference on video frames passed to it. It draws bounding boxes on the frames and returns a list of detected objects.
*   **`gps_module.py` (`GPSSimulator`):** Simulates a moving car by generating incrementally changing GPS coordinates over time.
*   **`cloud_storage.py` (`CloudStorage`):** Handles all communication with Google Firebase. It contains methods to upload files to Firebase Storage and to add data records to the Firestore database.
*   **`config.py`**: A centralized configuration file. It stores important paths (like the model and credentials file), the Firestore collection name, and simulator settings, making the application easier to manage.

### Backend (`backend`)
*   **`server.py`**: A modern web server built using the **FastAPI** framework.
*   **`/api/status` Endpoint**: This is the main GET endpoint. It fetches data from Firestore, transforms it, and sends it to the frontend as a JSON response. It also includes simulated telemetry data (CPU, FPS, etc.).
*   **`/api/control/start` & `/api/control/stop` Endpoints**: These POST endpoints allow the frontend to control the `is_scanning` flag in the telemetry simulation.
*   **`.env` file**: This file stores the path to the Google application credentials, keeping sensitive information out of the code.

### Frontend (`frontend`)
*   **Technology**: Built with React, TypeScript, and the Vite build tool for a fast development experience.
*   **`DefectsContext.tsx`**: This is the central state management solution for the application. It fetches data from the backend every 2 seconds and makes it available to all other components, preventing the need to pass data down through many layers.
*   **Components:**
    *   `DashboardLayout.tsx`: Provides the main structure, including the top navigation bar and background.
    *   `Roadmap.tsx`: A key component that uses `react-leaflet` to render an interactive map and plots defect locations using `Marker` components.
    *   `DefectTable.tsx`: Uses the `@mui/x-data-grid` library to create a powerful table that shows defect details. It includes built-in sorting and pagination.
    *   `AnalyticsWidgets.tsx`: Displays high-level statistics.
    *   `ControlPanel.tsx`: Provides buttons to start/stop the scanning process (as simulated by the backend telemetry).

---

## 5. How to Operate the Project

To run the entire system, you need to have three separate terminal windows open and running each component simultaneously.

1.  **Install Dependencies:** Before the first run, ensure you have installed all dependencies for `backend`, `car-software`, and `frontend` as described in the `README.md` file.
2.  **Start the Backend:**
    *   Open a terminal, navigate to the `backend` directory, and run `uvicorn server:app --reload --port 8000`.
    *   This terminal must remain open.
3.  **Start the Car Software:**
    *   Open a *second* terminal, navigate to the `car-software` directory, and run `python main.py`.
    *   A Kivy window will appear. This window simulates the in-car system. It must remain open to send data to the database.
4.  **Start the Frontend:**
    *   Open a *third* terminal, navigate to the `frontend` directory, and run `npm run dev`.
    *   This will open the dashboard in your default web browser.

You can now interact with the dashboard. The map and table will update in near real-time as the "car" (the Kivy window) "drives" and detects "defects".

---

## 6. Management and Maintenance

*   **Project Structure:** The project is modular, with each core component in its own directory. This separation makes it easier to work on one part of the system without affecting the others.
*   **Dependency Management:**
    *   The Python projects (`backend`, `car-software`) use `requirements.txt` files. To add a new dependency, add it to the file and run `pip install -r requirements.txt`.
    *   The JavaScript project (`frontend`) uses `package.json`. To add a new dependency, run `npm install <package-name>`.
*   **Configuration:**
    *   **`car-software/config.py`**: This is the primary place to change settings for the in-car application, such as the model path or simulator settings.
    *   **`backend/.env`**: This file is crucial for the backend to connect to Firebase. It should not be committed to version control for security reasons.
*   **ML Model Management:**
    *   The `ml-model` directory is where all AI model work should happen.
    *   The `train.py` script is set up to use **MLflow**, a tool for tracking experiments. When you run `train.py`, it will log the model's performance, parameters, and save the model itself.
    *   To view these experiments, navigate to the `ml-model` directory and run `mlflow ui`. This will start a local web server where you can compare different training runs.
    *   To deploy a new model, you would train it here, note the path to the new `best.pt` file from the MLflow run, and update the `MODEL_PATH` in `car-software/config.py`.
