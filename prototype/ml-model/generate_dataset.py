import os
import cv2
import numpy as np
import random
import shutil

# --- Configuration ---
IMG_SIZE = 640
NUM_IMAGES = 500
TRAIN_SPLIT = 0.8

# Dataset structure
# dataset/
# └── images/
# │   └─ train/
# │   └─ val/
# └─ labels/
#     └─ train/
#     └─ val/

# --- Class Definitions ---
# class_id: (class_name, color_for_drawing)
CLASSES = {
    0: ("scratch", (0, 0, 0)),        # Black
    1: ("dent", (0, 0, 255)),          # Red
    2: ("discoloration", (0, 255, 255)) # Yellow
}

def create_dataset_dirs():
    """Creates the directory structure for the YOLO dataset."""
    base_dir = "dataset_synthetic"
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    
    # Main directories
    images_dir = os.path.join(base_dir, "images")
    labels_dir = os.path.join(base_dir, "labels")

    # Subdirectories
    for d in [images_dir, labels_dir]:
        os.makedirs(os.path.join(d, "train"), exist_ok=True)
        os.makedirs(os.path.join(d, "val"), exist_ok=True)
        
    return base_dir

def generate_random_defect(image):
    """
    Draws a random defect on the product and returns its YOLO annotation.
    """
    h, w, _ = image.shape
    
    # Choose a random defect type
    class_id = random.choice(list(CLASSES.keys()))
    class_name, color = CLASSES[class_id]
    
    # Product is a grey rectangle in the center
    prod_w, prod_h = 300, 500
    prod_x1, prod_y1 = (w - prod_w) // 2, (h - prod_h) // 2
    prod_x2, prod_y2 = prod_x1 + prod_w, prod_y1 + prod_h
    
    x_center, y_center, width, height = 0, 0, 0, 0
    
    if class_name == "scratch":
        # Draw a line
        len = random.randint(50, 150)
        angle = random.uniform(0, np.pi)
        x1 = random.randint(prod_x1 + 20, prod_x2 - 20)
        y1 = random.randint(prod_y1 + 20, prod_y2 - 20)
        x2 = int(x1 + len * np.cos(angle))
        y2 = int(y1 + len * np.sin(angle))
        thickness = random.randint(1, 3)
        cv2.line(image, (x1, y1), (x2, y2), color, thickness)
        
        # Bounding box
        box_x1 = min(x1, x2)
        box_y1 = min(y1, y2)
        box_x2 = max(x1, x2)
        box_y2 = max(y1, y2)
        
        width = box_x2 - box_x1
        height = box_y2 - box_y1
        x_center = box_x1 + width / 2
        y_center = box_y1 + height / 2

    elif class_name == "dent":
        # Draw a small circle
        radius = random.randint(5, 15)
        x_center = random.randint(prod_x1 + radius, prod_x2 - radius)
        y_center = random.randint(prod_y1 + radius, prod_y2 - radius)
        cv2.circle(image, (x_center, y_center), radius, color, -1)
        width, height = 2 * radius, 2 * radius

    elif class_name == "discoloration":
        # Draw a semi-transparent rectangle
        dis_w, dis_h = random.randint(30, 80), random.randint(30, 80)
        x1 = random.randint(prod_x1, prod_x2 - dis_w)
        y1 = random.randint(prod_y1, prod_y2 - dis_h)
        
        overlay = image.copy()
        cv2.rectangle(overlay, (x1, y1), (x1 + dis_w, y1 + dis_h), color, -1)
        alpha = 0.4
        cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)

        width, height = dis_w, dis_h
        x_center = x1 + width / 2
        y_center = y1 + height / 2

    # Normalize for YOLO: (x_center, y_center, width, height)
    x_center_norm = x_center / w
    y_center_norm = y_center / h
    width_norm = width / w
    height_norm = height / h
    
    return f"{class_id} {x_center_norm} {y_center_norm} {width_norm} {height_norm}"

def create_image_and_label(image_path, label_path):
    """
    Creates a single image with a product and defects, and its corresponding label file.
    """
    # Create a blank background
    image = np.ones((IMG_SIZE, IMG_SIZE, 3), dtype=np.uint8) * 200 # Light grey background
    
    # Draw the "product" (a darker grey rectangle)
    prod_w, prod_h = 300, 500
    prod_x1, prod_y1 = (IMG_SIZE - prod_w) // 2, (IMG_SIZE - prod_h) // 2
    cv2.rectangle(image, (prod_x1, prod_y1), (prod_x1 + prod_w, prod_y1 + prod_h), (150, 150, 150), -1)

    # Add 1 to 3 defects
    num_defects = random.randint(1, 3)
    annotations = []
    for _ in range(num_defects):
        annotation = generate_random_defect(image)
        annotations.append(annotation)

    # Save the image
    cv2.imwrite(image_path, image)
    
    # Save the labels
    with open(label_path, "w") as f:
        f.write("\n".join(annotations))

def main():
    print("Generating synthetic dataset for factory quality assurance...")
    base_dir = create_dataset_dirs()
    
    num_train = int(NUM_IMAGES * TRAIN_SPLIT)
    
    for i in range(NUM_IMAGES):
        set_name = "train" if i < num_train else "val"
        
        image_path = os.path.join(base_dir, "images", set_name, f"product_{i:04d}.jpg")
        label_path = os.path.join(base_dir, "labels", set_name, f"product_{i:04d}.txt")
        
        create_image_and_label(image_path, label_path)

    print(f"\n✅ Dataset generation complete.")
    print(f"  - Total images: {NUM_IMAGES}")
    print(f"  - Training images: {num_train}")
    print(f"  - Validation images: {NUM_IMAGES - num_train}")
    print(f"Dataset created in: '{base_dir}'")
    print("\nNext steps:")
    print("1. Update 'ml-model/data.yaml' to point to this new dataset.")
    print("2. Run 'ml-model/train.py' to train the new model.")

if __name__ == "__main__":
    main()
