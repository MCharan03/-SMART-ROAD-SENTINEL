# SMART ROAD SENTINEL

## Project Overview
The SMART ROAD SENTINEL project is a comprehensive system designed for real-time detection and reporting of road defects from a car. It leverages an in-car system equipped with a camera, GPS, and a machine learning model to identify defects, stores this data in the cloud, and provides a web-based dashboard for visualization and analysis. The project aims to improve road maintenance efficiency and safety by providing timely and accurate information about road conditions.

The system consists of three main components:
*   **Car Software (`car-software`):** An in-car application that captures live camera feed, detects road defects using an integrated ML model, logs GPS coordinates, and uploads data to Firebase.
*   **ML Model (`ml-model`):** A YOLOv8 object detection model specifically trained to identify various types of road damage.
*   **Backend:** A FastAPI application that serves as an API for the frontend dashboard, fetching defect data from Firebase Firestore.
*   **Frontend:** A React-based web application that provides a dashboard to visualize detected road defects on a map, display analytics, and manage defect information.

## Getting Started

### Prerequisites
*   Python 3.8+
*   Node.js (LTS recommended) and npm (usually comes with Node.js)
*   Git
*   Firebase account and project setup (including a `asphalt-ai-firebase-adminsdk-fbsvc-f7762d42b3.json` file for service account access)

### General Installation

For each Python-based component (`backend`, `car-software`, `ml-model`):

1.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    ```
2.  **Activate the virtual environment:**
    *   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```
3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

For the Frontend (`frontend`):

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```
2.  **Install Node.js dependencies:**
    ```bash
    npm install
    ```
    *(If `npm install` fails due to `react-leaflet` or `leaflet` peer dependency issues, try `npm install --legacy-peer-deps`)*

---

## Running the Full Application

To run the complete SMART ROAD SENTINEL system, follow these steps in **separate terminal windows**:

### 1. Start the Backend Server

*   **Ensure:** You have a `backend/.env` file in the `backend` directory, pointing to your Firebase service account key. For example:
    ```
    GOOGLE_APPLICATION_CREDENTIALS="../asphalt-ai-firebase-adminsdk-fbsvc-f7762d42b3.json"
    ```
*   From the project root (`D:\Hackathon\Ideathon 25`), navigate to the `backend` directory and run the server:
    ```bash
    cd backend
    uvicorn server:app --reload --port 8000
    ```
*   **Leave this terminal running.** It will serve data to your dashboard.

### 2. Start the Car Software (Data Acquisition)

*   **Ensure:** You have a trained YOLOv8 model for road defect detection at `ml-model/runs/detect/train/weights/best.pt`.
*   From the project root (`D:\Hackathon\Ideathon 25`), open a **second terminal**.
*   Navigate to the `car-software` directory and run the application:
    ```bash
    cd car-software
    python main.py
    ```
*   This will open a **Kivy window** showing a simulated camera feed and GPS data. It will perform defect detection and send data to Firebase. **Leave this running in the background.**

### 3. Start the Frontend Dashboard

*   From the project root (`D:\Hackathon\Ideathon 25`), open a **third terminal**.
*   Navigate to the `frontend` directory and start the development server:
    ```bash
    cd frontend
    npm run dev
    ```
*   This will typically open the dashboard in your web browser (e.g., Chrome, Firefox) at `http://localhost:5173`.

You should now see the SMART ROAD SENTINEL dashboard displaying real-time road defect data on a map and in a table, based on the simulated car software data.

---

### Additional Notes:

*   **ML Model Training:** If you need to re-train the ML model (e.g., with new data), navigate to the `ml-model` directory and run `python train.py`. Ensure `ml-model/data.yaml` is configured correctly for your dataset.
*   **Firebase Project:** Remember to set up your Firebase project and ensure the necessary services (Firestore, Storage) are enabled.
