import asyncio
import random
from datetime import datetime
from threading import Thread
import time
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio
import random
from datetime import datetime
from threading import Thread, Lock
import time
import os
import csv
import pathlib
import ast
import io
import cv2

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel, Field

# Add parent directories to sys.path to allow imports from other folders
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'car-software')))

from detection import DetectionEngine
from car-software.gps_module import GPSSimulator
import car-software.config as config

# --- Global State & Configuration ---
# Using a dictionary to hold state that the background thread will modify
app_state = {
    "camera": None,
    "gps_simulator": None,
    "detection_engine": None,
    "latest_frame": None,
    "frame_lock": Lock(),
    "data_dir": None,
    "session_timestamp": None,
    "metadata_writer": None,
    "metadata_file": None,
    "is_scanning": False, # Control scanning state
}

# --- App Initialization ---
app = FastAPI(
    title="SMART ROAD SENTINEL API",
    description="API for the road defect detection dashboard.",
    version="1.0.0"
)

# --- Template and Static File Setup ---
app.mount("/static", StaticFiles(directory="prototype/backend/static"), name="static")
app.mount("/images", StaticFiles(directory="prototype/car-software/data"), name="images")
templates = Jinja2Templates(directory="prototype/backend/templates")

# --- Pydantic Data Models ---
class Telemetry(BaseModel):
    cpuUsage: float
    gpuUsage: float
    fps: int
    temperature: int
    is_scanning: bool = Field(..., alias="isScanning")

class Defect(BaseModel):
    id: str
    type: str
    confidence: float
    timestamp: int
    latitude: float
    longitude: float
    image_url: str

# --- System State (Simulation) ---
telemetry_data = Telemetry(cpuUsage=12.5, gpuUsage=45.0, fps=60, temperature=55, isScanning=False)

def telemetry_simulation():
    """Simulates telemetry data changes."""
    global telemetry_data
    while True:
        if app_state["is_scanning"]:
            telemetry_data.cpuUsage = round(random.uniform(30, 60), 1)
            telemetry_data.gpuUsage = round(random.uniform(50, 90), 1)
            telemetry_data.fps = int(random.uniform(28, 32))
        else:
            telemetry_data.cpuUsage = round(random.uniform(5, 15), 1)
            telemetry_data.gpuUsage = round(random.uniform(10, 20), 1)
        time.sleep(0.5)

# --- Data Saving Logic ---
def save_defect_data(frame, location, detections):
    """Saves the captured frame and its metadata."""
    timestamp = location['timestamp']
    image_filename = f"frame_{timestamp}.jpg"
    image_path = os.path.join(app_state["data_dir"], image_filename)
    
    # Save frame locally
    cv2.imwrite(image_path, frame)
    
    # Save metadata to CSV
    if app_state["metadata_writer"]:
        app_state["metadata_writer"].writerow([image_filename, timestamp, location['latitude'], location['longitude'], str(detections)])
        app_state["metadata_file"].flush()


# --- Camera & Detection Background Thread ---
def camera_thread_func():
    """Main loop for camera capture and defect detection."""
    while True:
        if not app_state["is_scanning"]:
            time.sleep(1)
            continue

        ret, frame = app_state["camera"].read()
        if not ret:
            print("❌ Failed to grab frame from camera.")
            time.sleep(1)
            continue

        original_frame = frame.copy() # Keep an original copy for saving
        location = app_state["gps_simulator"].get_location()
        
        # Perform ML inference
        detections, frame_with_boxes = app_state["detection_engine"].detect(frame)
        
        if detections:
            save_defect_data(original_frame, location, detections)
            
        # Update the frame for streaming
        with app_state["frame_lock"]:
            app_state["latest_frame"] = frame_with_boxes
        
        time.sleep(1 / config.UI_UPDATE_HZ)

# --- Video Streaming Generator ---
def generate_frames():
    """Generator function to yield frames for the MJPEG stream."""
    while True:
        with app_state["frame_lock"]:
            if app_state["latest_frame"] is not None:
                ret, buffer = cv2.imencode('.jpg', app_state["latest_frame"])
                if ret:
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(1 / config.UI_UPDATE_HZ)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Endpoints ---
class StatusResponse(BaseModel):
    telemetry: Telemetry
    defects: list[Defect]

@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/api/status", response_model=StatusResponse)
async def get_status():
    defect_list = []
    data_dir = pathlib.Path(__file__).parent.parent / "car-software" / "data"

    try:
        session_dirs = sorted([d for d in data_dir.iterdir() if d.is_dir()], reverse=True)
        if not session_dirs:
            return StatusResponse(telemetry=telemetry_data, defects=[])

        for session_dir in session_dirs[:5]: # Check last 5 sessions
            metadata_path = session_dir / 'metadata.csv'
            if metadata_path.exists():
                with open(metadata_path, 'r', newline='') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        try:
                            detections = ast.literal_eval(row.get('detections', '[]'))
                        except (ValueError, SyntaxError):
                            continue

                        for detection in detections:
                            defect_id = f"{session_dir.name}-{row.get('filename')}-{detection.get('class')}"
                            image_url = f"/images/{session_dir.name}/{row.get('filename')}"
                            
                            defect_list.append(
                                Defect(
                                    id=defect_id,
                                    type=detection.get('class', 'N/A'),
                                    confidence=float(detection.get('confidence', 0.0)),
                                    timestamp=int(row.get('timestamp', 0)),
                                    latitude=float(row.get('latitude', 0.0)),
                                    longitude=float(row.get('longitude', 0.0)),
                                    image_url=image_url
                                )
                            )
    except Exception as e:
        print(f"Error reading local data: {e}")

    # Update telemetry scanning status
    telemetry_data.is_scanning = app_state["is_scanning"]
    # Sort defects by timestamp descending and limit to 50
    defect_list.sort(key=lambda x: x.timestamp, reverse=True)
    return StatusResponse(telemetry=telemetry_data, defects=defect_list[:50])

class ControlResponse(BaseModel):
    status: str

@app.post("/api/control/start", response_model=ControlResponse)
async def start_scan():
    if not app_state["is_scanning"]:
        app_state["is_scanning"] = True
        # Create new session directory for saving data
        app_state["session_timestamp"] = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        app_state["data_dir"] = os.path.join(config.LOCAL_DATA_DIR, app_state["session_timestamp"])
        os.makedirs(app_state["data_dir"], exist_ok=True)
        
        metadata_path = os.path.join(app_state["data_dir"], 'metadata.csv')
        app_state["metadata_file"] = open(metadata_path, 'w', newline='')
        app_state["metadata_writer"] = csv.writer(app_state["metadata_file"])
        app_state["metadata_writer"].writerow(['filename', 'timestamp', 'latitude', 'longitude', 'detections'])
    return ControlResponse(status="started")

@app.post("/api/control/stop", response_model=ControlResponse)
async def stop_scan():
    if app_state["is_scanning"]:
        app_state["is_scanning"] = False
        if app_state["metadata_file"]:
            app_state["metadata_file"].close()
            app_state["metadata_file"] = None
            app_state["metadata_writer"] = None
    return ControlResponse(status="stopped")

# --- Application Lifecycle ---
@app.on_event("startup")
async def startup_event():
    # Initialize components
    app_state["camera"] = cv2.VideoCapture(0)
    app_state["gps_simulator"] = GPSSimulator(start_lat=config.START_LAT, start_lon=config.START_LON)
    app_state["detection_engine"] = DetectionEngine(model_path=config.MODEL_PATH)
    
    # Start background threads
    telemetry_thread = Thread(target=telemetry_simulation, daemon=True)
    camera_thread = Thread(target=camera_thread_func, daemon=True)
    telemetry_thread.start()
    camera_thread.start()
    
    print("🚀 SMART ROAD SENTINEL API ACTIVE")
    print("📡 API Running at http://localhost:8000")

@app.on_event("shutdown")
async def shutdown_event():
    if app_state["camera"]:
        app_state["camera"].release()
    if app_state["metadata_file"]:
        app_state["metadata_file"].close()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

class ControlResponse(BaseModel):
    status: str

@app.post("/api/control/start", response_model=ControlResponse)
async def start_scan():
    telemetry_data.is_scanning = True
    return ControlResponse(status="started")

@app.post("/api/control/stop", response_model=ControlResponse)
async def stop_scan():
    telemetry_data.is_scanning = False
    return ControlResponse(status="stopped")

# --- Application Lifecycle ---
@app.on_event("startup")
async def startup_event():
    simulation_thread = Thread(target=telemetry_simulation, daemon=True)
    simulation_thread.start()
    print("🚀 SMART ROAD SENTINEL API ACTIVE")
    print("📡 API Running at http://localhost:8000")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})