
from flask import Flask, Response, abort, jsonify,stream_with_context
import cv2
import os
import logging
import subprocess
import pandas as pd
import time
import sqlite3
from urllib.parse import unquote
from config_file import *
app = Flask(__name__)



# Configure logging
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    df = get_camera_log_df(sqlite_db_url)
    if df is not None:
        logging.info("Camera log DataFrame:")
        logging.info(df.head())
        return jsonify({"message": "Video Streaming Server is running", "data": df.to_dict(orient='records')})
    else:
        return jsonify({"message": "Failed to retrieve data from database."})

def get_camera_log_df(sqlite_db_url):
    try:
        conn = sqlite3.connect(sqlite_db_url)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM camera_log")
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
        return df
    except sqlite3.Error as e:
        logging.error(f"Error: {e}")
        return None
    finally:
        if conn:
            conn.close()


def generate_image_stream(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logging.error(f"Error opening video file: {video_path}")
        yield b"Error opening video file: " + video_path.encode()
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 25  # Default to 25 if fps is not available

    #frame_delay = 1.0 / fps

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convert frame to JPEG format
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        # Yield the JPEG image in byte stream format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        #time.sleep(frame_delay)

    cap.release()

def generate_ffmpeg_stream(video_path):
    command = [
        'ffmpeg',
        '-i', video_path,
        '-f', 'mpegts',  # Using MPEG-TS format for streaming
        '-codec:v', 'mpeg1video',  # Video codec
        '-b:v', '500k',  # Bitrate
        '-r', '30',  # Frame rate
        '-'
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process.stdout

@app.route('/<path:filename>')
def video(filename):
    video_path = '/'+unquote(filename)  # Decode the URL-encoded path
    logging.info(f"Requested video path: {video_path}")

    # Ensure the path is absolute
    if not os.path.isabs(video_path):
        video_path = os.path.join(stream_capture, video_path)

    logging.info(f"Absolute video path: {video_path}")

    if not os.path.isfile(video_path):
        logging.error(f"Video file not found: {video_path}")
        return abort(404, description="Video file not found")

    try:
        return Response(generate_ffmpeg_stream(video_path), mimetype='video/mp2t')  # Changed to 'video/mp2t' for MPEG-TS
    except Exception as e:
        logging.error(f"Error in /video route: {e}")
        return abort(500, description=str(e))


# def find_video_file(filename):
#     # List of possible video file extensions
#     extensions = ['.mp4', '.avi', '.mov', '.mkv']
#     #for root, _, files in os.walk(VIDEO_DIR):
#     for ext in extensions:
#         video_filename = f"{filename}{ext}"
#         if video_filename in files:
#             return os.path.join(root, video_filename)
#     return None


@app.route('/video/<path:filename>')
def video1(filename):
    video_path = '/'+unquote(filename)
    print(video_path)
    if not video_path:
        logging.error(f"Video file not found: {filename}")
        return abort(404, description="Video file not found")
    try:
        return Response(stream_with_context(generate_image_stream(video_path)), mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        logging.error(f"Error in /video route: {e}")
        return abort(500, description=str(e))

if __name__ == '__main__':
    logging.info("Starting Flask app")
    app.run(debug=True, host='0.0.0.0', port=49155)
