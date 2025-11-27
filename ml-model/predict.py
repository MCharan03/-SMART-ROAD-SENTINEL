from ultralytics import YOLO
import os
import cv2

# Load the trained model (assuming it's saved in runs/detect/train/weights/best.pt)
# You might need to adjust this path based on your training results
model_path = os.path.join(os.path.dirname(__file__), 'runs', 'detect', 'train', 'weights', 'best.pt')
model = YOLO(model_path)

# Path to a sample image for prediction
# Adjust this path to a valid image in your dataset
sample_image_path = os.path.join(os.path.dirname(__file__), 'dataset', 'archive', 'data', 'images', 'val', 'italy_000000.jpg')

if not os.path.exists(sample_image_path):
    print(f"Error: Sample image not found at {sample_image_path}")
    print("Please update 'sample_image_path' in predict.py to a valid image in your dataset.")
else:
    # Perform inference
    results = model(sample_image_path)

    # Show results
    for r in results:
        im_bgr = r.plot()  # plot a BGR numpy array of predictions
        cv2.imshow('YOLOv8 Inference', im_bgr)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    print("Prediction complete. Displayed results for sample image.")
