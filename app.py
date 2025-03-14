from flask import Flask, render_template, request, send_file, jsonify
import yt_dlp
import os
import time

app = Flask(__name__)

def get_video_formats(url):
    """Fetch available video formats for the given URL."""
    options = {"quiet": True}
    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = [
            {"format_id": f["format_id"], "resolution": f.get("height", "Unknown"), "ext": f["ext"]}
            for f in info["formats"] if f.get("height")
        ]
    return formats

def download_video(url, format_id):
    """Download video in the selected resolution."""
    options = {
        "format": format_id,
        "outtmpl": "%(title)s.%(ext)s",
    }
    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
    return os.path.abspath(filename), os.path.basename(filename)

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/get_formats", methods=["POST"])
def get_formats():
    url = request.json.get("url")
    try:
        formats = get_video_formats(url)
        return jsonify(formats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download", methods=["POST"])
def download():
    url = request.form["url"]
    format_id = request.form["format_id"]

    try:
        file_path, filename = download_video(url, format_id)
        
        if not os.path.exists(file_path):
            return "Error: Video download failed.", 500

        time.sleep(1)  # Ensure file is fully saved before sending

        return send_file(
            file_path,
            as_attachment=True,
            mimetype="video/mp4",
            download_name=filename
        )
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True)

