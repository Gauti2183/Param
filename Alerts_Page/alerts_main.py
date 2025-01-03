from flask import Flask, Response, request, send_file
import sqlite3
app = Flask(__name__)

def get_vehicle_count(database_path):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Query to count unique emp_id
        query = "SELECT COUNT(DISTINCT alpr) FROM object_log where name in ('car','truck','van');"
        cursor.execute(query)

        # Fetch the count
        result = cursor.fetchone()[0]
        print(f"Count of unique vehicle: {result}")

    except sqlite3.Error as e:
        print(f"Error occurred: {e}")
        result=4

    return result

def get_people_count(database_path):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Query to count unique emp_id
        query = "SELECT COUNT(DISTINCT emp_id) FROM employeelog;"
        cursor.execute(query)

        # Fetch the count
        result = cursor.fetchone()[0]
        print(f"Count of unique emp_id: {result}")

    except sqlite3.Error as e:
        print(f"Error occurred: {e}")
        result=1

    return result

def get_alerts(database_path):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Query to count unique emp_id
        query = "SELECT * FROM alert_review where DATE(Alert_Time) = today()';"
        cursor.execute(query)

        # Fetch the count
        alerts = cursor.fetchall()[0]

    except sqlite3.Error as e:
        print(f"Error occurred: {e}")
        alerts = [
            {
                'time_stamp': '2023-10-01 12:34:56',
                'reason': 'Unauthorized Access',
                'section': 'Section A',
                'alert_image_link': 'alert_image_link_1',
                'video_link': 'video_link_1'
            },
            {
                'time_stamp': '2023-10-02 13:45:00',
                'reason': 'Suspicious Activity',
                'section': 'Section B',
                'alert_image_link': 'alert_image_link_2',
                'video_link': 'video_link_2'
            },

        ]

    return alerts


@app.route('/')
def home():
    database_path="C:/PARAM/Param-Main"
    people_count = get_people_count(database_path)  # Example value, you can replace this with your actual data
    vehicle_count = get_vehicle_count(database_path)  # Example value, you can replace this with your actual data
    alerts = get_alerts(database_path)  # Example value, you can replace this with your actual data
    num_alerts = len(alerts)

    return render_template('index.html', people_count=people_count, vehicle_count=vehicle_count, num_alerts=num_alerts, alerts=alerts)

@app.route('/people-details')
def people_details():
    # Example data for people details
    people_entries = [
        {"id": 1, "name": "John Doe", "time": "2024-11-18 09:00:00", "section": "Lobby"},
        # Add more people entries
    ]
    return render_template('people_details.html', people_entries=people_entries)

@app.route('/vehicle-details')
def vehicle_details():
    # Example data for vehicle details
    vehicle_entries = [
        {"id": 1,"vehicle_type":"Truck", "vehicle_no": "AB123CD", "time": "2024-11-18 09:15:00", "section": "Parking Lot"},
        # Add more vehicle entries
    ]
    return render_template('vehicle_details.html', vehicle_entries=vehicle_entries)


@app.route('/<path:filename>')
def stream_video(filename):
    file_path = os.path.join(r"E:\_data_store_\video_files", filename)

    if not os.path.exists(file_path):
        return "File not found", 404

    range_header = request.headers.get('Range', None)
    if not range_header:
        return send_file(file_path)

    try:
        start, end = range_header.replace("bytes=", "").split("-")
        start = int(start)
        file_size = os.path.getsize(file_path)
        end = int(end) if end else file_size - 1
        chunk_size = end - start + 1

        with open(file_path, 'rb') as f:
            f.seek(start)
            data = f.read(chunk_size)

        response = Response(data, 206, mimetype="video/mp4", content_type="video/mp4")
        response.headers.add('Content-Range', f'bytes {start}-{end}/{file_size}')
        response.headers.add('Accept-Ranges', 'bytes')
        return response
    except ValueError:
        return "Invalid Range Header", 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
