import os
import logging
from fastapi import UploadFile
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
load_dotenv()

class AiEngine:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            logger.error("GEMINI_API_KEY not found in environment variables")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "gemini-1.5-flash"

    def generate_labels(self, description: str) -> str:
        """
        Generates a comma-separated list of labels based on the bug report description.
        """
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                config=types.GenerateContentConfig(
                    system_instruction="You are a product manager analyzing a bug report. "
                                       "Extract a list of specific, relevant labels (e.g., 'ui', 'contrast', 'button', 'login'). "
                                       "Return ONLY a comma-separated list of strings. No markdown, no json."
                ),
                contents=description
            )
            return response.text
        except Exception as e:
            logger.error(f"Error generating labels: {e}")
            return "bug, issue"

    async def transcribe(self, file: UploadFile) -> str:
        """
        Transcribes the video/audio file using Gemini 2.5 Flash multimodal capabilities.
        """
        try:
            logger.info(f"--- Starting transcription for {file.filename} using Gemini ---")
            
            # Read file content
            # Note: For very large files, we might need to use the File API, 
            # but for bug report clips, direct byte transfer is usually fine (limit is ~20MB for inline)
            # Vercel limit is 4.5MB for payload, but here we are processing the file uploaded to FastAPI.
            # Wait, if we are on Vercel, the whole request body is limited. 
            # But we are deploying to Vercel, so we must be careful.
            # Assuming the file is already uploaded to the FastAPI temporary storage mechanism.
            
            # Reset cursor to start
            await file.seek(0)
            content = await file.read()
            
            # Create a Part object with the video data
            # Gemini supports passing bytes directly for audio/video in 'parts'
            prompt = "Transcribe the audio in this video exactly."
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    types.Part.from_bytes(data=content, mime_type=file.content_type or "video/mp4"),
                    prompt
                ]
            )
            
            transcript = response.text
            logger.info("Transcription complete")
            return transcript

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return "Transcription failed. Please check the video."
        finally:
            # Reset file pointer for subsequent operations (like upload)
            await file.seek(0)
