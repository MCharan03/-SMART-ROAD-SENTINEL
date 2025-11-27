import os
import cv2
from ultralytics import YOLO
import config

class DetectionEngine:
    """
    A class to encapsulate the YOLOv8 model loading and inference logic.
    """
    def __init__(self):
        """
        Initializes the DetectionEngine by loading the YOLOv8 model.
        """
        self.model = self._load_model()

    def _load_model(self):
        """
        Loads the YOLOv8 model from the path specified in the config.
        Returns the model object or None if the model file doesn't exist.
        """
        if os.path.exists(config.MODEL_PATH):
            model = YOLO(config.MODEL_PATH)
            print(f"✅ DetectionEngine: Model loaded successfully from {config.MODEL_PATH}")
            return model
        else:
            print(f"❌ ERROR: DetectionEngine - Model not found at {config.MODEL_PATH}. Detection will be disabled.")
            return None

    def detect(self, frame):
        """
        Performs object detection on a single frame.

        Args:
            frame: The input image/frame from OpenCV.

        Returns:
            A tuple containing:
            - A list of dictionaries, where each dictionary represents a detected defect.
            - The frame with bounding boxes and labels drawn on it.
        """
        if not self.model:
            return [], frame

        detected_defects = []
        # Perform inference
        results = self.model(frame, verbose=False) # verbose=False suppresses console output

        for r in results:
            if r.boxes:  # Check if any boxes are detected
                for box in r.boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    class_name = self.model.names[class_id]
                    
                    detected_defects.append({
                        'class': class_name,
                        'confidence': round(confidence, 2)
                    })
                    
                    # Draw bounding box and label on the frame
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    label = f"{class_name} {confidence:.2f}"
                    cv2.putText(frame, label, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return detected_defects, frame
