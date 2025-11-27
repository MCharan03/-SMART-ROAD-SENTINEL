import asyncio
import random
from datetime import datetime
from threading import Thread
import time
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# --- App Initialization ---
app = FastAPI(
    title="SMART ROAD SENTINEL API",
    description="API for the road defect detection dashboard.",
    version="1.0.0"
)

# --- Environment and Firebase Setup ---
load_dotenv()

try:
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable not set.")
    
    if not os.path.isabs(cred_path):
        cred_path = os.path.join(os.path.dirname(__file__), cred_path)

    if not os.path.exists(cred_path):
         raise FileNotFoundError(f"Firebase credentials not found at: {cred_path}")

    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Firebase connection successful.")
except Exception as e:
    db = None
    print(f"❌ ERROR: Firebase connection failed. The API will run without real defect data. Error: {e}")


# --- Pydantic Data Models ---
class Telemetry(BaseModel):
    cpuUsage: float
    gpuUsage: float
    fps: int
    temperature: int
    is_scanning: bool = Field(..., alias="isScanning")

class Defect(BaseModel):
    id: str # Document ID
    type: str
    confidence: float
    timestamp: int
    latitude: float
    longitude: float
    image_url: str

# --- System State (Simulation) ---
# We simulate telemetry, but defects will be from Firestore
telemetry_data = Telemetry(cpuUsage=12.5, gpuUsage=45.0, fps=60, temperature=55, isScanning=False)

def telemetry_simulation():
    global telemetry_data
    while True:
        if telemetry_data.is_scanning:
            telemetry_data.cpuUsage = round(random.uniform(30, 60), 1)
            telemetry_data.gpuUsage = round(random.uniform(50, 90), 1)
            telemetry_data.fps = int(random.uniform(58, 64))
        else:
            telemetry_data.cpuUsage = round(random.uniform(5, 15), 1)
            telemetry_data.gpuUsage = round(random.uniform(10, 20), 1)
        time.sleep(0.5)

# --- Firestore Data Fetching and Transformation ---
def transform_firestore_docs_to_defects(docs: list) -> list[Defect]:
    defect_list = []
    for doc_snapshot in docs:
        doc_data = doc_snapshot.to_dict()
        doc_id = doc_snapshot.id
        
        if 'detections' in doc_data and isinstance(doc_data['detections'], list):
            for detection in doc_data['detections']:
                if isinstance(detection, dict):
                    defect_list.append(
                        Defect(
                            id=f"{doc_id}-{detection.get('class', 'unknown')}",
                            type=detection.get('class', 'N/A'),
                            confidence=detection.get('confidence', 0.0),
                            timestamp=doc_data.get('timestamp', 0),
                            latitude=doc_data.get('latitude', 0.0),
                            longitude=doc_data.get('longitude', 0.0),
                            image_url=doc_data.get('image_url', '')
                        )
                    )
    return defect_list


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

@app.get("/api/status", response_model=StatusResponse)
async def get_status():
    defect_list = []
    if db:
        try:
            docs = db.collection('road_data').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(50).stream()
            defect_list = transform_firestore_docs_to_defects(list(docs))
        except Exception as e:
            print(f"Error fetching from Firestore: {e}")
            defect_list = []

    return StatusResponse(telemetry=telemetry_data, defects=defect_list)

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