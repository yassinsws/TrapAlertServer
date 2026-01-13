import os
import uuid
import logging
from supabase import create_client, Client

logger = logging.getLogger(__name__)

# Initialize Supabase Client
url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_KEY", "")

supabase: Client = None

if url and key:
    try:
        supabase = create_client(url, key)
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")

def upload_video_to_supabase(video_bytes: bytes, content_type: str = "video/webm") -> str | None:
    """
    Uploads video bytes to Supabase Storage 'videos' bucket.
    Returns the public URL of the uploaded video.
    """
    if not supabase:
        logger.warning("Supabase client not initialized. Skipping upload.")
        return None

    try:
        file_name = f"{uuid.uuid4()}.webm"
        bucket_name = "videos"

        # Upload file
        response = supabase.storage.from_(bucket_name).upload(
            file=video_bytes,
            path=file_name,
            file_options={"content-type": content_type}
        )

        # Get public URL
        public_url_response = supabase.storage.from_(bucket_name).get_public_url(file_name)
        
        # Check if the public URL is wrapped in a response object or is a string
        # Newer supabase-py might return a string directly or an object
        if hasattr(public_url_response, 'publicURL'): # Legacy check
             return public_url_response.publicURL
        
        return public_url_response # Use directly if string

    except Exception as e:
        logger.error(f"Failed to upload video to Supabase: {e}")
        return None
