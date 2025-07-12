# Enhanced Stream Analyzer with Styled UI, Adaptive Bitrate, Error Pattern, and Device Simulation

from flask import Flask, render_template_string, jsonify, request
import cv2
import time
import yt_dlp
import random

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Stream Analyzer</title>
  <style>
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(to right, #f7f7f7, #e0f7fa);
      padding: 40px;
      text-align: center;
    }
    h2 {
      color: #00796b;
    }
    input[type=text], select {
      width: 60%;
      padding: 10px;
      font-size: 16px;
      margin-bottom: 20px;
      border: 1px solid #ccc;
      border-radius: 5px;
    }
    button {
      padding: 10px 20px;
      font-size: 16px;
      background-color: #00796b;
      color: white;
      border: none;
      border-radius: 5px;
      cursor: pointer;
    }
    button:hover {
      background-color: #004d40;
    }
    .status-box {
      background: white;
      padding: 30px;
      border-radius: 10px;
      box-shadow: 0 0 15px rgba(0,0,0,0.1);
      display: inline-block;
      margin-top: 30px;
      width: 50%;
    }
    .online { color: green; font-weight: bold; }
    .offline { color: red; font-weight: bold; }
    .metric { font-size: 16px; margin: 5px 0; }
  </style>
</head>
<body>
  <h2>📡 Advanced Stream Analyzer</h2>
  <form id="streamForm">
    <input type="text" id="stream_url" placeholder="Enter video URL (YouTube, HLS, MP4)..." required><br>
    <select id="device">
      <option value="desktop">Desktop</option>
      <option value="mobile">Mobile</option>
      <option value="smart_tv">Smart TV</option>
    </select><br>
    <button type="submit">Analyze</button>
  </form>
  <div class="status-box" id="status">
    <p class="metric">Stream status will appear here...</p>
  </div>
  <script>
    document.getElementById("streamForm").onsubmit = function(e) {
      e.preventDefault();
      const url = document.getElementById("stream_url").value;
      const device = document.getElementById("device").value;
      fetch(`/api/stream?url=${encodeURIComponent(url)}&device=${device}`)
        .then(response => response.json())
        .then(data => {
          const statusBox = document.getElementById('status');
          statusBox.innerHTML = `
            <p class="metric">Status: <span class="${data.status === 'Online' ? 'online' : 'offline'}">${data.status}</span></p>
            <p class="metric">Latency: ${data.latency !== null ? data.latency + ' sec' : 'N/A'}</p>
            <p class="metric">Dropped Frames: ${data.frame_drops !== null ? data.frame_drops : 'N/A'}</p>
            <p class="metric">Adaptive Bitrate: ${data.bitrate} kbps</p>
            <p class="metric">Error Pattern: ${data.error_pattern}</p>
            <p class="metric">Device Simulated: ${data.device}</p>
          `;
        })
        .catch(err => {
          document.getElementById('status').innerHTML = '<p class="metric">Error loading data.</p>';
        });
    }
  </script>
</body>
</html>
"""


def get_youtube_stream_url(youtube_url):
    ydl_opts = {"quiet": True, "no_warnings": True, "format": "best"}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            return info["url"]
    except Exception:
        return None


def simulate_adaptive_bitrate(device):
    if device == "mobile":
        return random.choice([300, 480, 720])
    elif device == "smart_tv":
        return random.choice([720, 1080, 2160])
    else:
        return random.choice([480, 720, 1080])


def simulate_error_pattern():
    return random.choice(
        ["None", "Pixelation at 5s", "Buffering spikes", "Audio Desync"]
    )


def analyze_stream(url):
    cap = cv2.VideoCapture(url)
    if not cap.isOpened():
        return {"status": "Offline", "latency": None, "frame_drops": None}

    latencies = []
    frame_drops = 0
    total_frames = 30

    for _ in range(total_frames):
        start = time.time()
        ret, frame = cap.read()
        end = time.time()
        if not ret:
            frame_drops += 1
        else:
            latencies.append(end - start)

    cap.release()
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    return {
        "status": "Online",
        "latency": round(avg_latency, 3),
        "frame_drops": frame_drops,
    }


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/api/stream")
def stream_status():
    url = request.args.get("url")
    device = request.args.get("device", "desktop")

    if not url:
        return jsonify({"error": "Missing URL"}), 400

    if "youtube.com" in url or "youtu.be" in url:
        stream_url = get_youtube_stream_url(url)
        if not stream_url:
            return jsonify({"status": "Offline", "latency": None, "frame_drops": None})
    else:
        stream_url = url

    result = analyze_stream(stream_url)
    result["bitrate"] = simulate_adaptive_bitrate(device)
    result["error_pattern"] = simulate_error_pattern()
    result["device"] = device.replace("_", " ").title()
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
