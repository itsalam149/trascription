from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import librosa
import numpy as np


from app.audio_utils import convert_mp4_to_mp3
from app.assembly_ai import upload_file, request_transcription, get_transcription_result

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
STATIC_DIR = os.path.join(BASE_DIR, "static")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def serve_index():
    return FileResponse("index.html")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    file_path = os.path.join(AUDIO_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/mpeg", filename=filename)
    raise HTTPException(status_code=404, detail="Audio file not found")

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

    try:
        y, sr = librosa.load(audio_path)
        frame_length = 2048
        hop_length = 512
        energy = np.array([
            sum(abs(y[i:i+frame_length]**2))
            for i in range(0, len(y), hop_length)
        ])
        energy /= np.max(energy)
        times = librosa.frames_to_time(np.arange(len(energy)), sr=sr, hop_length=hop_length)

        for word in result.get("words", []):
            start_sec = word["start"] / 1000.0
            end_sec = word["end"] / 1000.0
            indices = np.where((times >= start_sec) & (times <= end_sec))[0]
            avg_energy = float(np.mean(energy[indices])) if len(indices) > 0 else 0.0
            word["energy"] = round(avg_energy, 10)
    except Exception as e:
        print("Energy computation failed:", e)

    os.remove(video_path)

    return JSONResponse(content={
        "transcription": result,
        "audio_path": f"/audio/{os.path.basename(audio_path)}"
    })
