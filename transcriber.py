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
        self.model_name = "gemini-2.5-flash"

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
            return response.text if response.text else "bug, issue"
        except Exception as e:
            logger.error(f"Error generating labels: {e}")
            return "bug, issue"

    async def transcribe_bytes(self, video_bytes: bytes, content_type: str, filename: str) -> str:
        """
        Transcribes video bytes using Gemini 1.5 Flash multimodal capabilities.
        """
        try:
            logger.info(f"--- Starting transcription for {filename} using Gemini ---")
            
            # Create a Part object with the video data
            prompt = "Transcribe the audio in this video exactly."
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    types.Part.from_bytes(data=video_bytes, mime_type=content_type),
                    prompt
                ]
            )
            
            transcript = response.text
            logger.info("Transcription complete")
            return transcript

        except Exception as e:
            logger.error(f"Transcription failed: {e}", exc_info=True)
            return "Transcription failed. Please check the video."
