import os
import cv2
from ultralytics import YOLO

class DetectionEngine:
    """
    A class to encapsulate the YOLOv8 model loading and inference logic.
    """
    def __init__(self, model_path):
        """
        Initializes the DetectionEngine by loading the YOLOv8 model.
        :param model_path: The absolute or relative path to the .pt model file.
        """
        self.model = self._load_model(model_path)

    def _load_model(self, model_path):
        """
        Loads the YOLOv8 model from the specified path.
        Returns the model object or None if the model file doesn't exist.
        """
        if os.path.exists(model_path):
            model = YOLO(model_path)
            print(f"✅ DetectionEngine: Model loaded successfully from {model_path}")
            return model
        else:
            print(f"❌ ERROR: DetectionEngine - Model not found at {model_path}. Detection will be disabled.")
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
            # The ultralytics results object can be iterated over directly
            for box in r.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = self.model.names.get(class_id, 'Unknown') # Use .get for safety
                
                # For this project, we are primarily interested in 'Pothole'
                if class_name == 'Pothole':
                    detected_defects.append({
                        'class': class_name,
                        'confidence': round(confidence, 2)
                    })
                    
                    # Draw bounding box and label on the frame
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2) # Red for potholes
                    label = f"{class_name} {confidence:.2f}"
                    cv2.putText(frame, label, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        return detected_defects, frame
