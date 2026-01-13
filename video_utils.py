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
        logger.error("Supabase client not initialized. Check SUPABASE_URL and SUPABASE_KEY env vars.")
        return None

    try:
        file_name = f"{uuid.uuid4()}.webm"
        bucket_name = "videos"
        
        logger.info(f"Uploading video: {file_name} ({len(video_bytes)} bytes)")

        # Upload file
        response = supabase.storage.from_(bucket_name).upload(
            file=video_bytes,
            path=file_name,
            file_options={"content-type": content_type}
        )
        
        logger.info(f"Upload response: {response}")

        # Get public URL
        public_url_response = supabase.storage.from_(bucket_name).get_public_url(file_name)
        
        # Check if the public URL is wrapped in a response object or is a string
        if hasattr(public_url_response, 'publicURL'):
             public_url = public_url_response.publicURL
        else:
             public_url = public_url_response
             
        logger.info(f"Video uploaded successfully: {public_url}")
        return public_url

    except Exception as e:
        logger.error(f"Failed to upload video to Supabase: {e}", exc_info=True)
        return None
