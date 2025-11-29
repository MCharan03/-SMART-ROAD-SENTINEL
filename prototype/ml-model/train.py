import os
import mlflow
from ultralytics import YOLO

def main():
    """
    Main function to train the YOLOv8 model with MLflow tracking.
    """
    # --- MLflow Setup ---
    # Set the experiment name. If it doesn't exist, MLflow creates it.
    mlflow.set_experiment("Road Defect Detection")

    # Start an MLflow run. All subsequent logging will be associated with this run.
    with mlflow.start_run() as run:
        print(f"MLflow Run ID: {run.info.run_id}")
        mlflow.log_param("model_type", "yolov8n")
        mlflow.log_param("epochs", 50)
        mlflow.log_param("image_size", 640)

        # --- Model Training ---
        # Load a pre-trained YOLOv8n model
        model = YOLO('yolov8n.pt')

        # Define the path to the data.yaml file
        data_yaml_path = os.path.join(os.path.dirname(__file__), 'data.yaml')
        mlflow.log_param("dataset", data_yaml_path)

        print("Starting model training with MLflow tracking...")
        
        # Train the model
        # Ultralytics' native MLflow integration will automatically log metrics,
        # parameters, and model artifacts.
        results = model.train(data=data_yaml_path, epochs=50, imgsz=640)

        print("Training complete.")
        
        # --- Post-Training ---
        # The model is automatically saved by Ultralytics and logged by MLflow.
        # You can find the run details and artifacts in the MLflow UI.
        
        # You could add additional logging here if needed, for example,
        # logging a confusion matrix plot as an artifact.
        # confusion_matrix_path = os.path.join(results.save_dir, 'confusion_matrix.png')
        # if os.path.exists(confusion_matrix_path):
        #     mlflow.log_artifact(confusion_matrix_path, "plots")

    print("\n--- MLflow Summary ---")
    print("Model training has been tracked with MLflow.")
    print(f"To view the results, run the following command in your terminal:")
    print(f"cd '{os.path.dirname(__file__)}' && mlflow ui")
    print(f"Then open http://localhost:5000 in your browser.")

if __name__ == '__main__':
    main()