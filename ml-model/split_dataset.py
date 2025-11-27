import os
import random
import shutil

# Define paths
base_dir = os.path.join('dataset', 'archive', 'data')
images_dir = os.path.join(base_dir, 'images')
labels_dir = os.path.join(base_dir, 'labels')

# Get all image filenames
all_images = [f for f in os.listdir(images_dir) if os.path.isfile(os.path.join(images_dir, f))]
random.shuffle(all_images)

# Define split ratios
train_ratio = 0.8
val_ratio = 0.1
# test_ratio is implicitly 0.1

# Calculate split indices
train_split = int(len(all_images) * train_ratio)
val_split = int(len(all_images) * (train_ratio + val_ratio))

# Split the data
train_images = all_images[:train_split]
val_images = all_images[train_split:val_split]
test_images = all_images[val_split:]

# Function to move files
def move_files(filenames, split_name):
    for filename in filenames:
        # Move image
        src_image_path = os.path.join(images_dir, filename)
        dst_image_path = os.path.join(images_dir, split_name, filename)
        shutil.move(src_image_path, dst_image_path)

        # Move corresponding label
        label_filename = os.path.splitext(filename)[0] + '.txt'
        src_label_path = os.path.join(labels_dir, label_filename)
        dst_label_path = os.path.join(labels_dir, split_name, label_filename)
        if os.path.exists(src_label_path):
            shutil.move(src_label_path, dst_label_path)

# Move the files
move_files(train_images, 'train')
move_files(val_images, 'val')
move_files(test_images, 'test')

print("Dataset split complete.")
print(f"Total images: {len(all_images)}")
print(f"Training images: {len(train_images)}")
print(f"Validation images: {len(val_images)}")
print(f"Test images: {len(test_images)}")
