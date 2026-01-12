import os

from fastapi import UploadFile
from google.genai import types
from google import genai
from pydantic import BaseModel, Field
from models import BugReport
from faster_whisper import WhisperModel
import logging
from dotenv import load_dotenv
# Set up the logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO) # Ensures INFO level logs are shown
load_dotenv()

class AiEngine:
    def __init__(self):
        self.client = genai.Client()
        self.model_size = "small"
        self.model = WhisperModel(self.model_size, device="cpu", compute_type="float32")

    def generate_labels(self, description):
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction="You are a product manager that want to extract labels for a bug ticket out"
                                   " of this description."
                                   " Give back a list of labels that are very specific to this description of the bug"
                                   " all separated only by a comma in a json schema like: button1, focus, contrast."
                                   " Here is the description now: "),

            contents=description
        )
        return response.text


    def stuctured_output(self, model: BaseModel, prompt: str):
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type= "application/json",
                response_json_schema= BugReport.model_json_schema() )
        )

        bug_report = BugReport.model_validate_json(response.text)
        print(bug_report)

    async def transcribe(self, file: UploadFile):
        temp_path = f"temp_{file.filename}"

        # Use a chunked write for better reliability
        with open(temp_path, "wb") as f:
            while content := await file.read(1024 * 1024):  # 1MB chunks
                f.write(content)

        try:
            logger.info(f"--- Starting transcription for {file.filename} ---")

            segments, info = self.model.transcribe(temp_path, beam_size=5, vad_filter=True)

            full_text = []
            for segment in segments:
                # Print just the NEW segment so you can see progress
                logger.info(f"[Segment]: {segment.text}")
                full_text.append(segment.text)

            final_transcript = " ".join(full_text).strip()

            return final_transcript

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                logger.info(f"--- Cleaned up {temp_path} ---")



