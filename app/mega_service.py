import os
import tempfile
from mega import Mega
from fastapi import UploadFile, HTTPException
from app.config import settings  # Import the instantiated settings object, not Settings class


class MegaStorage:
    def __init__(self):
        self.mega = Mega()
        self.client = None

    def _get_client(self):
        if not self.client:
            # Access variables via the imported settings instance
            if not settings.MEGA_EMAIL or not settings.MEGA_PASSWORD:
                raise HTTPException(
                    status_code=500,
                    detail="MEGA credentials not configured in environment variables."
                )
            try:
                self.client = self.mega.login(settings.MEGA_EMAIL, settings.MEGA_PASSWORD)
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to authenticate with MEGA: {str(e)}"
                )
        return self.client

    def upload_file(self, file: UploadFile) -> str:
        client = self._get_client()

        # Ensure file pointer is at the beginning before reading
        file.file.seek(0)
        content = file.file.read()

        # Save temporary file locally to pass to mega.py
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp:
            tmp.write(content)
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