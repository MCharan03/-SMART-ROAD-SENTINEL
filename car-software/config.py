import os

# Base directory of the car-software component
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..'))

# --- Firebase Configuration ---
# The service account key for Firebase Admin SDK
CREDENTIALS_FILE = os.path.join(PROJECT_ROOT, 'asphalt-ai-firebase-adminsdk-fbsvc-f7762d42b3.json')
# Your Firebase Project ID
PROJECT_ID = 'asphalt-ai'
# Name of the Firestore collection to store data
FIRESTORE_COLLECTION = 'road_data'


# --- ML Model Configuration ---
# Path to the original trained road defect YOLOv8 model weights
MODEL_PATH = os.path.join(PROJECT_ROOT, 'ml-model', 'runs', 'detect', 'train', 'weights', 'best.pt')


# --- Data Storage Configuration ---
# Directory to save local data (images and metadata)
LOCAL_DATA_DIR = os.path.join(BASE_DIR, 'data')

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