import os

# Base directory of the car-software component
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..'))

from dotenv import load_dotenv
dotenv_path = os.path.join(PROJECT_ROOT, 'backend', '.env')
load_dotenv(dotenv_path=dotenv_path)
# --- Firebase Configuration ---
# The service account key for Firebase Admin SDK
CREDENTIALS_FILE = os.path.abspath(os.path.join(PROJECT_ROOT, 'backend', os.getenv('GOOGLE_APPLICATION_CREDENTIALS')))
# Your Firebase Project ID
PROJECT_ID = os.getenv('PROJECT_ID')
# Name of the Firestore collection to store data
FIRESTORE_COLLECTION = os.getenv('FIRESTORE_COLLECTION')


# --- ML Model Configuration ---
# Path to the original trained road defect YOLOv8 model weights
MODEL_PATH = os.path.join(PROJECT_ROOT, 'ml-model', 'yolov8n.pt')


# --- Data Storage Configuration ---
# Directory to save local data (images and metadata)
LOCAL_DATA_DIR = os.path.join(BASE_DIR, 'data')
# Data retention policy (in days)
DATA_RETENTION_DAYS = int(os.getenv('DATA_RETENTION_DAYS', 30))

# --- Kivy UI Configuration ---
# Update frequency for the UI (in Hz)
UI_UPDATE_HZ = 30
# Frequency for saving data (in Hz)
DATA_SAVE_HZ = 1

# --- GPS Simulator Configuration ---
# Starting latitude for the simulator
START_LAT = 12.9716
# Starting longitude for the simulator
START_LON = 77.5946