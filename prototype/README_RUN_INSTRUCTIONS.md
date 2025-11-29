# SENTINEL Live Demonstration - Run Instructions

The project has been consolidated into a single, powerful demonstration application. All previous components (`backend`, `car-software`, etc.) have been merged into the main `prototype` directory.

The new demo provides a futuristic car dashboard UI that shows live pothole detection from your webcam and simulates the car's "reaction" to them.

## 1. Installation

First, ensure you have Python 3.8+ installed.

1.  **Navigate to the Project Root:**
    Open your terminal and navigate to the `Ideathon 25` directory.

2.  **Create a Virtual Environment (Recommended):**
    ```shell
    python -m venv venv
    ```

3.  **Activate the Virtual Environment:**
    *   On Windows:
        ```shell
        .\venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```shell
        source venv/bin/activate
        ```

4.  **Install Dependencies:**
    A new, simplified `requirements.txt` has been created. Install all necessary packages with this single command:
    ```shell
    pip install -r prototype/requirements.txt
    ```
    *(This will install Flask, OpenCV, and Ultralytics along with their dependencies like PyTorch.)*

## 2. Running the Live Demo

1.  **Ensure Webcam is Available:** Make sure your webcam is connected and not being used by another application.

2.  **Run the Application:**
    From the `Ideathon 25` root directory, run the following command:
    ```shell
    python prototype/app.py
    ```

3.  **Open the Dashboard:**
    Once the server is running, it will print a message to your console. Open your web browser (Chrome or Firefox recommended) and navigate to:

    **http://127.0.0.1:5000**

You should now see the SENTINEL live dashboard. Point your webcam at a picture or video of a road with potholes to see the system detect them and react in real-time on the dashboard.