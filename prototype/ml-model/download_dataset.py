import os
from kaggle.api.kaggle_api_extended import KaggleApi

# Set the KAGGLE_CONFIG_DIR environment variable
os.environ['KAGGLE_CONFIG_DIR'] = os.path.join(os.getcwd(), '.kaggle')

# Initialize the Kaggle API
api = KaggleApi()
api.authenticate()

# Download the dataset
dataset_name = 'saifullah23/road-damage-dataset'
path_to_download = 'ml-model/dataset'

print(f"Downloading dataset '{dataset_name}' to '{path_to_download}'...")
api.dataset_download_files(dataset_name, path=path_to_download, unzip=True)
print("Dataset download complete.")
