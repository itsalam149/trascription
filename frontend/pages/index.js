import { useState } from "react";

export default function Home() {
  const [file, setFile] = useState(null);
  const [transcription, setTranscription] = useState("");
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return alert("Please upload a video file");

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);

    const res = await fetch("https://your-render-url.onrender.com/transcribe-video", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    setTranscription(data.text || "No transcription available");
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-900 text-white px-4">
      <h1 className="text-3xl font-bold mb-4">Video Transcriber</h1>
      <input
        type="file"
        accept=".mp4"
        onChange={(e) => setFile(e.target.files[0])}
        className="mb-4"
      />
      <button
        onClick={handleUpload}
        className="bg-blue-500 px-4 py-2 rounded hover:bg-blue-600"
      >
        {loading ? "Transcribing..." : "Upload & Transcribe"}
      </button>

      {transcription && (
        <div className="mt-6 w-full max-w-xl">
          <h2 className="text-xl font-semibold mb-2">Transcription:</h2>
          <p className="bg-gray-800 p-4 rounded">{transcription}</p>
        </div>
      )}
    </div>
  );
}
