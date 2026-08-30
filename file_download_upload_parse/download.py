from pymongo import MongoClient
from pymongo.server_api import ServerApi
from gridfs import GridFS
from gridfs.errors import NoFile
from bson import ObjectId
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

    def download_file_gfs(self, file_id: str | ObjectId, output_path: str | Path):
        if isinstance(file_id, str):
            if not ObjectId.is_valid(file_id):
                raise ValueError(
                    "file_id must be a 24-character hexadecimal MongoDB ObjectId."
                )
            file_id = ObjectId(file_id)

        output_folder = Path(output_path)
        output_folder.mkdir(parents=True, exist_ok=True)

        try:
            file_data = self.fs.get(file_id)
        except NoFile as exc:
            raise FileNotFoundError(
                f"No GridFS file exists with ID: {file_id}"
            ) from exc
        output_file_path = output_folder / file_data.filename

        with output_file_path.open("wb") as f:
            f.write(file_data.read())

        print(f"File '{file_data.filename}' downloaded from GridFS to: {output_file_path}")

if __name__ == "__main__":
    open_books = Books_download()
    # Replace 'your_file_id_here' with the actual file ID you want to download
    file_id_to_download = '6a9422cbedceb9192d302b4a'
    open_books.download_file_gfs(file_id_to_download, Path(__file__).resolve().parents[1] / "downloads")
