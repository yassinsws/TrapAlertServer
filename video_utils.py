import subprocess
import os
import tempfile
import uuid
import logging

logger = logging.getLogger(__name__)

def compress_video(input_bytes: bytes) -> bytes:
    """
    Compresses video bytes using FFmpeg.
    - Re-encodes to H.264
    - Sets a lower bitrate for space efficiency
    - Scales down to 720p if larger
    """
    # Create temporary files for processing
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as input_file:
        input_file.write(input_bytes)
        input_path = input_file.name

    output_path = f"{tempfile.gettempdir()}/{uuid.uuid4()}.mp4"

    try:
        # Construct FFmpeg command
        # -i: input
        # -vcodec libx264: H.264 codec
        # -crf 28: Constant Rate Factor (18-28 is good range, higher is more compressed)
        # -preset faster: encoding speed vs compression ratio
        # -vf "scale='min(1280,iw)':-2": Scale to 720p max width, maintaining aspect ratio
        command = [
            'ffmpeg',
            '-nostdin',
            '-i', input_path,
            '-vcodec', 'libx264',
            '-crf', '28',
            '-preset', 'faster',
            '-vf', "scale='min(1280,iw)':-2",
            '-acodec', 'aac',
            '-b:a', '128k',
            '-y', # Overwrite output if exists
            output_path
        ]

        logger.info(f"Running FFmpeg: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"FFmpeg error: {result.stderr}")
            # If compression fails, return original bytes (fallback)
            return input_bytes

        # Read the compressed file
        with open(output_path, "rb") as f:
            compressed_bytes = f.read()
        
        logger.info(f"Compression successful: {len(compressed_bytes)} bytes")
        return compressed_bytes

    except Exception as e:
        logger.exception("Failed to compress video")
        return input_bytes
    finally:
        # Cleanup
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)
