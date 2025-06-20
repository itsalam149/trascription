import librosa
import numpy as np
import matplotlib.pyplot as plt

def generate_audio_energy_graph(audio_path, output_image_path):
    y, sr = librosa.load(audio_path)

    frame_length = 2048
    hop_length = 512
    energy = np.array([
        sum(abs(y[i:i+frame_length]**2))
        for i in range(0, len(y), hop_length)
    ])
    energy /= np.max(energy)
    times = librosa.frames_to_time(np.arange(len(energy)), sr=sr, hop_length=hop_length)

    plt.figure(figsize=(10, 4))
    plt.plot(times, energy, color="cyan")
    plt.xlabel("Time (s)")
    plt.ylabel("Energy")
    plt.title("Audio Energy Over Time")
    plt.tight_layout()
    plt.savefig(output_image_path)
    plt.close()
