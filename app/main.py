from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import uuid
from app.audio_utils import convert_mp4_to_mp3
from app.assembly_ai import upload_file, request_transcription, get_transcription_result

import asyncio

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
AUDIO_DIR = os.path.join(BASE_DIR, "audio")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

app = FastAPI()

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

@app.post("/transcribe-video")
async def transcribe_video(file: UploadFile = File(...)):
    if not file.filename.endswith(".mp4"):
        raise HTTPException(status_code=400, detail="Only .mp4 files are supported")
    
    video_filename = f"{uuid.uuid4()}.mp4"
    video_path = os.path.join(UPLOAD_DIR, video_filename)
    
    with open(video_path, "wb") as buffer:
        buffer.write(await file.read())
    
    audio_filename = f"{uuid.uuid4()}.mp3"
    audio_path = os.path.join(AUDIO_DIR, audio_filename)

    try:
        convert_mp4_to_mp3(video_path, audio_path)
    except Exception as e:
        os.remove(video_path)
        raise HTTPException(status_code=500, detail=f"Audio conversion failed: {str(e)}")

    try:
        audio_url = upload_file(audio_path)
        transcript_id = request_transcription(audio_url)
        if not transcript_id:
            raise Exception("No transcript ID returned")
        result = get_transcription_result(transcript_id)
    except Exception as e:
        os.remove(video_path)
        os.remove(audio_path)
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

    os.remove(video_path)
    os.remove(audio_path)

    return JSONResponse(content=result)

