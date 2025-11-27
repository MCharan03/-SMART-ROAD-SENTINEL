import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.graphics import Color, Rectangle
import cv2
from gps_module import GPSSimulator
from cloud_storage import CloudStorage
import os
import datetime
import csv
import threading
from detection import DetectionEngine

import config

kivy.require('2.1.0')

class AlertBox(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.padding = 10
        self.spacing = 10
        with self.canvas.before:
            Color(0, 0, 0, 0.5) # Semi-transparent black
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        # Placeholder for icon
        self.add_widget(Label(text="!", size_hint_x=0.2))
        self.alert_text_label = Label(text="No defects detected.")
        self.add_widget(self.alert_text_label)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class SentinelApp(App):
    def build(self):
        # Main layout
        root_layout = FloatLayout()

        # Video display area
        video_layout = BoxLayout(orientation='vertical')
        self.video_display = Image()
        video_layout.add_widget(self.video_display)

        # GPS display
        self.gps_label = Label(text="GPS: N/A", size_hint=(1, 0.1), pos_hint={'bottom': 1})
        video_layout.add_widget(self.gps_label)

        root_layout.add_widget(video_layout)

        # Alert area
        self.alert_box = AlertBox(size_hint=(0.5, 0.1), pos_hint={'center_x': 0.5, 'top': 0.9})
        self.alert_box.opacity = 0 # Initially hidden
        root_layout.add_widget(self.alert_box)

        # Initialize camera, GPS, and Detection Engine
        self.capture = cv2.VideoCapture(0)
        self.gps = GPSSimulator(start_lat=config.START_LAT, start_lon=config.START_LON)
        self.detection_engine = DetectionEngine()

        # Initialize data storage
        self.setup_storage()

        # Schedule updates
        Clock.schedule_interval(self.update, 1.0 / config.UI_UPDATE_HZ) # UI update
        Clock.schedule_interval(self.save_data, 1.0 / config.DATA_SAVE_HZ) # Data saving

        return root_layout

    def setup_storage(self):
        self.session_timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.data_dir = os.path.join(config.LOCAL_DATA_DIR, self.session_timestamp)
        os.makedirs(self.data_dir, exist_ok=True)

        self.metadata_file_path = os.path.join(self.data_dir, 'metadata.csv')
        self.metadata_file = open(self.metadata_file_path, 'w', newline='')
        self.metadata_writer = csv.writer(self.metadata_file)
        self.metadata_writer.writerow(['filename', 'timestamp', 'latitude', 'longitude', 'detections'])

        self.current_frame = None
        self.current_location = None
        self.current_detections = []

        # Initialize cloud storage
        if os.path.exists(config.CREDENTIALS_FILE):
            self.cloud_storage = CloudStorage(
                credentials_path=config.CREDENTIALS_FILE,
                project_id=config.PROJECT_ID
            )
        else:
            self.cloud_storage = None
            print("WARNING: Firebase credentials not found. Cloud upload will be disabled.")

    def save_data(self, dt):
        if self.current_frame is not None and self.current_location is not None:
            timestamp = self.current_location['timestamp']
            lat = self.current_location['latitude']
            lon = self.current_location['longitude']

            # Save frame locally
            image_filename = f"frame_{timestamp}.jpg"
            image_path = os.path.join(self.data_dir, image_filename)
            cv2.imwrite(image_path, self.current_frame)

            # Save metadata locally
            self.metadata_writer.writerow([image_filename, timestamp, lat, lon, str(self.current_detections)])

            # Upload to cloud in a separate thread
            if self.cloud_storage:
                thread = threading.Thread(target=self.upload_to_cloud, args=(image_path, self.current_location, self.current_detections))
                thread.start()

    def upload_to_cloud(self, image_path, location_data, detections):
        # Upload image
        destination_blob_name = f"{self.session_timestamp}/{os.path.basename(image_path)}"
        image_url = self.cloud_storage.upload_file(image_path, destination_blob_name)

        # Add metadata to Firestore
        if image_url:
            data_to_upload = location_data.copy()
            data_to_upload['image_url'] = image_url
            data_to_upload['detections'] = detections
            self.cloud_storage.add_document(config.FIRESTORE_COLLECTION, data_to_upload)

    def show_alert(self, message):
        self.alert_box.alert_text_label.text = message
        self.alert_box.opacity = 1
        Clock.schedule_once(self.hide_alert, 5)

    def hide_alert(self, dt):
        self.alert_box.opacity = 0
        self.alert_box.alert_text_label.text = "No defects detected."


    def update(self, dt):
        # Read frame from camera
        ret, frame = self.capture.read()

        if ret:
            self.current_frame = frame
            # Get GPS location
            self.current_location = self.gps.get_location()
            self.gps_label.text = f"GPS: {self.current_location['latitude']:.4f}, {self.current_location['longitude']:.4f}"

            # Perform ML inference
            self.current_detections, frame_with_boxes = self.detection_engine.detect(frame)

            if self.current_detections:
                alert_message = ", ".join([f"{d['class']} ({d['confidence']:.2f})" for d in self.current_detections])
                self.show_alert(f"Defect Detected: {alert_message}")
            else:
                self.hide_alert(None) # Hide alert if no defects

            # Convert it to texture for display
            buf1 = cv2.flip(frame_with_boxes, 0)
            buf = buf1.tostring()
            image_texture = Texture.create(
                size=(frame_with_boxes.shape[1], frame_with_boxes.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            # Display image from the texture
            self.video_display.texture = image_texture

    def on_stop(self):
        # Release the camera and close the metadata file
        self.capture.release()
        self.metadata_file.close()

if __name__ == '__main__':
    SentinelApp().run()
