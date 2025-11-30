import firebase_admin
from firebase_admin import credentials, firestore, storage
import os

class CloudStorage:
    def __init__(self, credentials_path, project_id):
        """
        Initializes the Firebase connection.
        :param credentials_path: Path to the Firebase service account JSON file.
        :param project_id: Your Firebase project ID.
        """
        if not firebase_admin._apps:
            cred = credentials.Certificate(credentials_path)
            firebase_admin.initialize_app(cred, {
                'storageBucket': f'{project_id}.appspot.com'
            })
        self.db = firestore.client()
        self.bucket = storage.bucket()

    def upload_file(self, file_path, destination_blob_name):
        """
        Uploads a file to Firebase Storage.
        :param file_path: Path to the file to upload.
        :param destination_blob_name: The name of the blob in Firebase Storage.
        """
        try:
            blob = self.bucket.blob(destination_blob_name)
            blob.upload_from_filename(file_path)
            print(f"File {file_path} uploaded to {destination_blob_name}.")
            return blob.public_url
        except Exception as e:
            print(f"Error uploading file: {e}")
            return None

    def add_document(self, collection_name, data):
        """
        Adds a document to a Firestore collection.
        :param collection_name: The name of the Firestore collection.
        :param data: A dictionary representing the document data.
        """
        try:
            doc_ref = self.db.collection(collection_name).add(data)
            print(f"Document added with ID: {doc_ref[1].id}")
            return doc_ref[1].id
        except Exception as e:
            print(f"Error adding document: {e}")
            return None

if __name__ == '__main__':
    # Example Usage (requires the credentials file)
    # cred_path = '../asphalt-ai-firebase-adminsdk-fbsvc-f7762d42b3.json'
    # if os.path.exists(cred_path):
    #     cloud = CloudStorage(credentials_path=cred_path, project_id='asphalt-ai')
    #     # Create a dummy file to upload
    #     with open("test.txt", "w") as f:
    #         f.write("This is a test file.")
    #     cloud.upload_file("test.txt", "test_uploads/test.txt")
    #     cloud.add_document("test_collection", {"name": "test", "value": 42})
    # else:
    #     print("Credentials file not found. Cannot run example.")
    pass
