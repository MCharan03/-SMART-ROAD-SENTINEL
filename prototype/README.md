# SMART ROAD SENTINEL

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
    *   The `DetectionEngine` loads a pre-trained YOLOv8 model (`yolov8n.pt`) specified in `config.py`.
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

## 4. Getting Started

### Prerequisites
*   Python 3.8+
*   Node.js (LTS recommended) and npm (usually comes with Node.js)
*   Git
*   Firebase account and project setup.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    ```
3.  **Activate the virtual environment:**
    *   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```
4.  **Install the required dependencies:**
    ```bash
    pip install -r prototype/requirements.txt
    ```

5.  **Set up environment variables:**
    Create a file named `.env` in the `prototype` directory and add the following lines:
    ```
    CREDENTIALS_FILE=asphalt-ai-firebase-adminsdk-fbsvc-f7762d42b3.json
    PROJECT_ID=asphalt-ai
    FIRESTORE_COLLECTION=road_data
    GOOGLE_APPLICATION_CREDENTIALS=asphalt-ai-firebase-adminsdk-fbsvc-f7762d42b3.json
    ```
    **Note:** Make sure you have the `asphalt-ai-firebase-adminsdk-fbsvc-f7762d42b3.json` file in the `prototype` directory.

---

## 5. Running the Full Application

To run the complete SMART ROAD SENTINEL system, follow these steps in **separate terminal windows**:

### 1. Start the Backend Server

*   From the `prototype` directory, run the server:
    ```bash
    uvicorn backend.server:app --reload --port 8000
    ```
*   **Leave this terminal running.** It will serve data to your dashboard.

### 2. Start the Car Software (Data Acquisition)

*   From the `prototype` directory, open a **second terminal**.
*   Run the application:
    ```bash
    python car-software/main.py
    ```
*   This will open a **Kivy window** showing a simulated camera feed and GPS data. It will perform defect detection and send data to Firebase. **Leave this running in the background.**

### 3. Start the Frontend Dashboard

*   The frontend code is currently missing from the project.

---

## 6. Management and Maintenance

*   **Project Structure:** The project is modular, with each core component in its own directory. This separation makes it easier to work on one part of the system without affecting the others.
*   **Dependency Management:**
    *   The Python dependencies are managed in the `prototype/requirements.txt` file. To add a new dependency, add it to the file and run `pip install -r prototype/requirements.txt`.
    *   The JavaScript project (`frontend`) uses `package.json`. To add a new dependency, run `npm install <package-name>`.
*   **Configuration:**
    *   **`car-software/config.py`**: This is the primary place to change settings for the in-car application, such as the model path or simulator settings.
    *   **`prototype/.env`**: This file is crucial for the backend to connect to Firebase. It should not be committed to version control for security reasons.
*   **ML Model Management:**
    *   The `ml-model` directory is where all AI model work should happen.
    *   The `train.py` script is set up to use **MLflow**, a tool for tracking experiments. When you run `train.py`, it will log the model's performance, parameters, and save the model itself.
    *   To view these experiments, navigate to the `ml-model` directory and run `mlflow ui`. This will start a local web server where you can compare different training runs.
    *   To deploy a new model, you would train it here, note the path to the new `best.pt` file from the MLflow run, and update the `MODEL_PATH` in `car-software/config.py`.