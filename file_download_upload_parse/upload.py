from pymongo import MongoClient
from pymongo.server_api import ServerApi
from gridfs import GridFS
from dotenv import load_dotenv
import os

class Books_open:
    def __init__(self):
        load_dotenv()
        self.mongo_uri = os.getenv("MONGO_URI")
        self.client = MongoClient(self.mongo_uri, server_api=ServerApi('1'))

        try:
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print("Error connecting to MongoDB: ", e)

        self.mongo_db = os.getenv("MONGO_DB_NAME")
        self.mongo_collection = os.getenv("MONGO_COLLECTION_NAME")
        self.fs = GridFS(self.client[self.mongo_db])

    def upload_file_gfs(self, file_path):
        with file_path.open("rb") as f:
                file_id = self.fs.put(f, filename=file_path.name)
        
        file_saved = {
            "file_id": file_id,
            "filename": file_path.name,
            }
        result = self.mongo_collection.insert_one(file_saved)
        return result.inserted_id

open_books = Books_open()
open_books.upload_file_gfs("testing.pdf")