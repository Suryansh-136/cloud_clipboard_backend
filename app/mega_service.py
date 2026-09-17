import os
import tempfile
from mega import Mega
from fastapi import UploadFile, HTTPException

MEGA_EMAIL = os.getenv("MEGA_EMAIL")
MEGA_PASSWORD = os.getenv("MEGA_PASSWORD")

class MegaStorage:
    def __init__(self):
        self.mega = Mega()
        self.client = None

    def _get_client(self):
        if not self.client:
            if not MEGA_EMAIL or not MEGA_PASSWORD:
                raise HTTPException(status_code=500, detail="MEGA credentials not configured in environment variables.")
            try:
                self.client = self.mega.login(MEGA_EMAIL, MEGA_PASSWORD)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to authenticate with MEGA: {str(e)}")
        return self.client

    def upload_file(self, file: UploadFile) -> str:
        client = self._get_client()
        
        # Save temporary file locally to pass to mega.py
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name

        try:
            # Upload to MEGA root
            uploaded_file = client.upload(tmp_path)
            # Get public access link
            link = client.get_upload_link(uploaded_file)
            return link
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"MEGA upload failed: {str(e)}")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def delete_file_by_url(self, url: str):
        client = self._get_client()
        try:
            # Find the file node on MEGA using its URL link
            file_node = client.find_by_url(url)
            if file_node:
                client.delete(file_node[0])
        except Exception as e:
            print(f"Failed to delete file from MEGA: {e}")

mega_storage = MegaStorage()