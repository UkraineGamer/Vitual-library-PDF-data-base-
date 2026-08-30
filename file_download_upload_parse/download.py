from pymongo import MongoClient
from pymongo.server_api import ServerApi
from gridfs import GridFS
from dotenv import load_dotenv
from pathlib import Path
import os
import re

class Books_download:
    def __init__(self):
        load_dotenv()
        self.mongo_uri = self._normalise_mongo_uri(
            self._required_env("MONGO_URI")
        )
        self.client = MongoClient(self.mongo_uri, server_api=ServerApi('1'))

        try:
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as exc:
            raise ConnectionError(
                "Could not authenticate with MongoDB Atlas. Check MONGO_URI, "
                "the Atlas database user, and Network Access settings."
            ) from exc

        self.mongo_db = self._required_env("MONGO_DB_NAME")
        collection_name = self._required_env("MONGO_COLLECTION_NAME")
        self.fs = GridFS(self.client[self.mongo_db])
        self.mongo_collection = self.client[self.mongo_db][collection_name]

    @staticmethod
    def _required_env(name: str) -> str:
        value = os.getenv(name)
        if not value:
            raise RuntimeError(f"Missing required environment variable: {name}")
        return value

    @staticmethod
    def _normalise_mongo_uri(uri: str) -> str:
        """Remove Atlas UI's optional <password> placeholder brackets."""
        return re.sub(r":<([^>]*)>@", r":\1@", uri)

    def download_file_gfs(self, file_id: str | bytes, output_path: str | Path):
        output_folder = Path(output_path)
        output_folder.mkdir(parents=True, exist_ok=True)

        file_data = self.fs.get(file_id)
        output_file_path = output_folder / file_data.filename

        with output_file_path.open("wb") as f:
            f.write(file_data.read())