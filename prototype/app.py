import threading
import time
import math
import cv2
import sqlite3
import datetime
import os
import random
from flask import Flask, jsonify, render_template, Response

from detection import DetectionEngine

# --- App Initialization ---
app = Flask(__name__, template_folder='templates', static_folder='static')

# --- Configuration ---
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'ml-model', 'runs', 'detect', 'train', 'weights', 'best.pt')

# --- Database ---
def init_db():
    # Use check_same_thread=False for SQLite in a multi-threaded Flask app
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS potholes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            timestamp DATETIME NOT NULL
        )
    ''')
    conn.commit()
    return conn

db_conn = init_db()

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
        # In a real app, you'd have try/except blocks here to connect to hardware.
        # For this demo, we'll just show that they fail and we fall back to simulation.
        print("Attempting to connect to hardware...")
        # self.gps = connect_to_gps_dongle() -> would return a device object or raise Exception
        # self.obd = connect_to_obd_adapter() -> would return a device object or raise Exception
        # self.imu = connect_to_imu_sensor()  -> would return a device object or raise Exception
        
        # Since we have no hardware, connections "fail".
        self.gps_status = "SIMULATED"
        self.obd_status = "SIMULATED"
        self.imu_status = "SIMULATED"
        print(f"GPS Connection Failed. Status: {self.gps_status}")
        print(f"OBD-II Connection Failed. Status: {self.obd_status}")
        print(f"IMU Connection Failed. Status: {self.imu_status}")

    def get_location(self):
        if self.gps_status == "LIVE":
            # return self.gps.get_real_location()
            pass
        # Fallback to simulation
        self._sim_angle += 0.0001
        lat = self._center_lat + self._radius * math.cos(self._sim_angle)
        lon = self._center_lon + self._radius * math.sin(self._sim_angle)
        return lat, lon

    def get_speed(self):
        if self.obd_status == "LIVE":
            # return self.obd.get_real_speed()
            pass
        # Fallback to simulation
        return 45 + 5 * math.sin(self._sim_angle * 10)

    def get_g_force(self):
        if self.imu_status == "LIVE":
            # return self.imu.get_real_g_force()
            pass
        # Fallback to simulation
        g_force = 0.8 + 0.2 * math.sin(self._sim_angle * 50)
        if time.time() % 10 < 0.1: # Fake a bump every ~10 seconds
             g_force += 1.5
        return g_force

# --- Global State ---
state = {
    "current_speed": 0.0,
    "g_force": 0.0,
    "pothole_detected": False,
    "suspension_status": "ACTIVE",
    "latitude": 12.9716,
    "longitude": 77.5946,
    "pothole_cooldown": 0,
    "latest_event": None,
    "gps_status": "INIT",
    "obd_status": "INIT",
    "imu_status": "INIT"
}
state_lock = threading.Lock()

# --- ML Model & Video Initialization ---
detection_engine = DetectionEngine(model_path=MODEL_PATH)
video_capture = cv2.VideoCapture(0)
hw_manager = HardwareManager()

def main_loop():
    """Main background loop for simulation and detection."""
    global state
    
    while True:
        # --- Get data from hardware manager (real or simulated) ---
        lat, lon = hw_manager.get_location()
        speed = hw_manager.get_speed()
        g_force_base = hw_manager.get_g_force()

        # --- ML Detection on Video Frame ---
        success, frame = video_capture.read()
        if not success:
            time.sleep(0.1)
            continue
        
        detected_defects, _ = detection_engine.detect(frame.copy())
        pothole_in_frame = any(d['class'] == 'Pothole' for d in detected_defects)

        # --- Update State (Thread-Safe) ---
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

            if pothole_in_frame and state["pothole_cooldown"] == 0:
                state.update({
                    "pothole_detected": True,
                    "suspension_status": "STABILIZING",
                    "pothole_cooldown": 15,
                    "g_force": g_force_base * 0.5, # System reacted, G-force is absorbed
                    "latest_event": {
                        "timestamp": datetime.datetime.now().isoformat(),
                        "type": "POTHOLE",
                        "details": f"Detected at {lat:.4f}, {lon:.4f}"
                    }
                })
                # Log to DB
                cursor = db_conn.cursor()
                cursor.execute("INSERT INTO potholes (latitude, longitude, timestamp) VALUES (?, ?, ?)",
                               (lat, lon, datetime.datetime.now()))
                db_conn.commit()
            else:
                state["g_force"] = g_force_base # No reaction, normal G-force

        time.sleep(0.2) # Loop runs approx 5 times per second

def generate_frames_with_detection():
    """Generator for streaming video with detection overlays."""
    while True:
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
        return jsonify(state)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames_with_detection(), mimetype='multipart/x-mixed-replace; boundary=frame')

# --- Main Execution ---
if __name__ == "__main__":
    main_thread = threading.Thread(target=main_loop)
    main_thread.daemon = True
    main_thread.start()
    
    print("🚀 SENTINEL Dashboard is running!")
    print("Navigate to http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# --- Cleanup ---
@app.teardown_appcontext
def cleanup(exception=None):
    video_capture.release()
    db_conn.close()