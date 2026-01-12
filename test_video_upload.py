import requests
import os

# Configuration
API_URL = "http://localhost:8000"
TENANT_API_KEY = "demo-tenant-001" # From the DB

def create_dummy_report():
    # 1. Create a dummy video file if it doesn't exist
    video_path = "dummy_video.mp4"
    if not os.path.exists(video_path):
        print("Creating dummy video file with silent audio...")
        # Use ffmpeg to create a 3-second black video with silent audio
        os.system("ffmpeg -f lavfi -i color=c=black:s=640x480:d=3 -f lavfi -i anullsrc=r=44100:cl=mono -t 3 -c:v libx264 -c:a aac -pix_fmt yuv420p dummy_video.mp4")

    # 2. Prepare the feedback request
    print("Sending feedback with video...")
    files = {
        'video': ('dummy_video.mp4', open(video_path, 'rb'), 'video/mp4')
    }
    data = {
        'dom': '<html><body><h1>Test Page</h1></body></html>',
        'metadata': '{"browser": "ManualTest", "os": "MacOS"}',
        'tenantId': TENANT_API_KEY,
        'description': 'This is a test report with a real video blob.',
        'struggleScore': 85.5
    }

    response = requests.post(f"{API_URL}/feedback", files=files, data=data)
    
    if response.status_code == 200:
        print(f"✅ Success! Created report ID: {response.json().get('id')}")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    create_dummy_report()
