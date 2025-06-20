import requests
import time
import os

API_KEY = os.environ.get("ASSEMBLY_AI_API_KEY")

def upload_file(file_path):
    headers = {"authorization": API_KEY}
    with open(file_path, "rb") as f:
        response = requests.post(
            "https://api.assemblyai.com/v2/upload",
            headers=headers,
            data=f
        )
    response.raise_for_status()
    return response.json().get("upload_url")

def request_transcription(audio_url):
    endpoint = "https://api.assemblyai.com/v2/transcript"
    json_data = {
        "audio_url": audio_url,
        "language_code": "en_us"
    }
    headers = {
        "authorization": API_KEY,
        "content-type": "application/json"
    }
    response = requests.post(endpoint, json=json_data, headers=headers)
    response.raise_for_status()
    return response.json().get("id")

def get_transcription_result(transcript_id):
    endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
    headers = {"authorization": API_KEY}
    
    while True:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "completed":
            return data
        elif data.get("status") == "error":
            raise Exception(f"Transcription failed: {data.get('error')}")
        time.sleep(3)
