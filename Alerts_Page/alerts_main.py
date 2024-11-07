from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    people_count = 42  # Example value, you can replace this with your actual data
    vehicle_count = 15  # Example value, you can replace this with your actual data
    num_alerts = 5  # Example value, you can replace this with your actual data

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
        # Add more alerts as needed
    ]

    return render_template('index.html', people_count=people_count, vehicle_count=vehicle_count, num_alerts=num_alerts, alerts=alerts)

if __name__ == '__main__':
    app.run(debug=True)
