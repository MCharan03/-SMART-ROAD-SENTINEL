import collections # Added import for deque
import threading
import time
import math
import cv2
import datetime
import os
import random
from flask import Flask, jsonify, render_template, Response, request, make_response
import numpy as np

from detection import DetectionEngine
from data_manager import DataManager # Import the new DataManager
from car_software import config # Import config for LOCAL_DATA_DIR and DATA_RETENTION_DAYS

# --- App Initialization ---
app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'),
    static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
)

# --- Initialize DataManager ---
data_manager = DataManager(
    db_path='database.db',
    local_data_dir=config.LOCAL_DATA_DIR,
    retention_days=config.DATA_RETENTION_DAYS
)

# --- Configuration (Moved to config.py or kept minimal here) ---
# MODEL_PATH is now accessed from config.py

# G-Force history settings
G_FORCE_HISTORY_LENGTH = 60 # Number of data points to keep (e.g., 60 seconds at 1Hz update)
IMPACT_THRESHOLD = 2.0 # G-force value to consider an impact

# --- Hardware & Simulation Management ---
class HardwareManager:
    """
    Simulates connecting to and reading from real hardware.
    If a connection fails, it provides simulated data instead.
    """
    def __init__(self):
        self.gps_status = "DISCONNECTED"
        self.obd_status = "DISCONNECTED"
        self.imu_status = "DISCONNECTED"
        self._connect_devices()

        # Simulation parameters if hardware fails
        self._sim_angle = 0
        self._center_lat, self._center_lon = 12.9716, 77.5946
        self._radius = 0.01

    def _connect_devices(self):
        print("Attempting to connect to hardware...")
        self.gps_status = "SIMULATED"
        self.obd_status = "SIMULATED"
        self.imu_status = "SIMULATED"
        print(f"GPS Connection Failed. Status: {self.gps_status}")
        print(f"OBD-II Connection Failed. Status: {self.obd_status}")
        print(f"IMU Connection Failed. Status: {self.imu_status}")

    def get_location(self):
        self._sim_angle += 0.0001
        lat = self._center_lat + self._radius * math.cos(self._sim_angle)
        lon = self._center_lon + self._radius * math.sin(self._sim_angle)
        return lat, lon

    def get_speed(self):
        return 45 + 5 * math.sin(self._sim_angle * 10)

    def get_g_force(self):
        g_force = 0.8 + 0.2 * math.sin(self._sim_angle * 50)
        if time.time() % 10 < 0.1: # Fake a bump every ~10 seconds
             g_force += 1.5
        return g_force

# --- Global State ---
state = {
    "current_speed": 0.0,
    "g_force": 0.0,
    "g_force_history": collections.deque([0.0] * G_FORCE_HISTORY_LENGTH, maxlen=G_FORCE_HISTORY_LENGTH), # G-force history
    "impact_events_history": [], # Store detected impacts {timestamp, g_force}
    "pothole_detected": False,
    "pothole_confidence": 0.0, 
    "suspension_status": "ACTIVE",
    "latitude": 12.9716,
    "longitude": 77.5946,
    "pothole_cooldown": 0,
    "latest_event": None,
    "gps_status": "INIT",
    "obd_status": "INIT",
    "imu_status": "INIT",
    "camera_active": False,
    "current_session_timestamp": None 
}
state_lock = threading.Lock()

# --- ML Model & Video Initialization ---
detection_engine = DetectionEngine(model_path=config.MODEL_PATH)
video_capture = cv2.VideoCapture(0)
hw_manager = HardwareManager()

def main_loop():
    """Main background loop for simulation and detection."""
    global state
    
    while True:
        if not state.get("camera_active"):
            time.sleep(1)
            continue
            
        lat, lon = hw_manager.get_location()
        speed = hw_manager.get_speed()
        g_force_base = hw_manager.get_g_force()

        # Update G-force history
        state["g_force_history"].append(g_force_base)
        if g_force_base >= IMPACT_THRESHOLD:
            state["impact_events_history"].append({
                "timestamp": datetime.datetime.now().isoformat(),
                "g_force": g_force_base
            })

        success, frame = video_capture.read()
        if not success:
            time.sleep(0.1)
            continue
        
        original_frame = frame.copy() 
        detected_defects, _ = detection_engine.detect(frame.copy())
        pothole_in_frame = any(d['class'] == 'Pothole' for d in detected_defects)

        with state_lock:
            state.update({
                "current_speed": speed,
                "latitude": lat,
                "longitude": lon,
                "gps_status": hw_manager.gps_status,
                "obd_status": hw_manager.obd_status,
                "imu_status": hw_manager.imu_status
            })

            if state["pothole_cooldown"] > 0:
                state["pothole_cooldown"] -= 1
            else:
                state["pothole_detected"] = False
                state["suspension_status"] = "ACTIVE"
                state["pothole_confidence"] = 0.0 

            if pothole_in_frame and state["pothole_cooldown"] == 0:
                highest_confidence = 0.0
                for defect in detected_defects:
                    if defect['class'] == 'Pothole' and defect['confidence'] > highest_confidence:
                        highest_confidence = defect['confidence']

                session_timestamp = state['current_session_timestamp']
                image_filename = f"frame_{int(time.time())}.jpg"
                if session_timestamp and config.LOCAL_DATA_DIR: 
                    session_dir = os.path.join(config.LOCAL_DATA_DIR, session_timestamp)
                    os.makedirs(session_dir, exist_ok=True)
                    cv2.imwrite(os.path.join(session_dir, image_filename), original_frame)
                    print(f"Pothole image saved: {os.path.join(session_dir, image_filename)}")
                else:
                    image_filename = None 

                state.update({
                    "pothole_detected": True,
                    "pothole_confidence": highest_confidence, 
                    "suspension_status": "STABILIZING",
                    "pothole_cooldown": 15,
                    "g_force": g_force_base * 0.5, 
                    "latest_event": {
                        "timestamp": datetime.datetime.now().isoformat(),
                        "type": "POTHOLE",
                        "details": f"Detected at {lat:.4f}, {lon:.4f}"
                    }
                })
                # Log to DB using DataManager
                data_manager.add_pothole_entry(lat, lon, datetime.datetime.now(), 
                                               session_timestamp, image_filename, highest_confidence)
            else:
                state["g_force"] = g_force_base 

        time.sleep(0.2) 

def generate_frames_with_detection():
    """Generator for streaming video with detection overlays."""
    while True:
        if not state.get("camera_active"):
            placeholder = cv2.imencode('.jpg', np.zeros((480, 640, 3), dtype=np.uint8))[1].tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + placeholder + b'\r\n')
            time.sleep(1)
            continue

        success, frame = video_capture.read()
        if not success:
            break
        
        _, frame_with_boxes = detection_engine.detect(frame)

        ret, buffer = cv2.imencode('.jpg', frame_with_boxes)
        if not ret: continue
        
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.05)


# --- Flask Routes ---
@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/data")
def get_data():
    with state_lock:
        # Create a copy of the state to modify for JSON serialization
        serializable_state = dict(state)
        # Convert deque to list for JSON serialization
        serializable_state["g_force_history"] = list(state["g_force_history"])
        
        # Get impact events to send and then clear them from the state
        # This ensures impacts are only sent once to the frontend
        impacts_to_send = list(state["impact_events_history"])
        serializable_state["impact_events_history"] = impacts_to_send
        state["impact_events_history"].clear() # Clear after sending
        
        return jsonify(serializable_state)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames_with_detection(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_camera', methods=['POST'])
def start_camera():
    with state_lock:
        state['camera_active'] = True
        state['current_session_timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') # Initialize session
    return jsonify({"status": "camera started"})

@app.route('/stop_camera', methods=['POST'])
def stop_camera():
    with state_lock:
        state['camera_active'] = False
        state['current_session_timestamp'] = None # Clear session on stop
    return jsonify({"status": "camera stopped"})

@app.route('/export_data')
def export_data_route(): 
    return data_manager.export_pothole_data()

@app.route('/api/historical_potholes')
def historical_potholes_route(): 
    potholes_list, status_code = data_manager.get_historical_potholes_data(request.args.get('date_filter'))
    if status_code != 200:
        return jsonify(potholes_list), status_code
    return jsonify(potholes_list)

@app.route('/api/summary_statistics')
def summary_statistics_route(): 
    summary_data, status_code = data_manager.get_summary_statistics_data()
    if status_code != 200:
        return jsonify(summary_data), status_code
    return jsonify(summary_data)

@app.route('/api/defect_details/<int:defect_id>')
def defect_details_route(defect_id):
    defect_data, status_code = data_manager.get_defect_details(defect_id)
    if status_code != 200:
        return jsonify(defect_data), status_code
    return jsonify(defect_data)

# --- Main Execution ---
if __name__ == "__main__":
    main_thread = threading.Thread(target=main_loop)
    main_thread.daemon = True
    main_thread.start()
    
    # Schedule data cleanup to run periodically (e.g., once every 24 hours)
    def cleanup_scheduler():
        while True:
            data_manager.cleanup_old_data() 
            time.sleep(24 * 60 * 60) 
    
    cleanup_thread = threading.Thread(target=cleanup_scheduler)
    cleanup_thread.daemon = True
    cleanup_thread.start()

    print("🚀 SENTINEL Dashboard is running!")
    print("Navigate to http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# --- Cleanup ---
@app.teardown_appcontext
def cleanup(exception=None):
    video_capture.release()
    data_manager.close() 
