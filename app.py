from flask import Flask, render_template, Response, jsonify, request
import threading
from camera import VideoCamera, music_rec

app = Flask(__name__)

# Define column headings for the table
headings = ("Name", "Album", "Artist")

# Fetch initial music recommendations and limit to 15 rows
df1 = music_rec()
df1 = df1.head(15)

# Flag to control video capture
capture_flag = False

# Initialize VideoCamera
camera = VideoCamera()

@app.route('/')
def index():
    print(df1.to_json(orient='records'))
    return render_template('index.html', headings=headings, data=df1)

# Function to generate video frames from the camera
def gen(camera):
    global capture_flag
    while True:
        global df1
        if capture_flag:
            frame, df1 = camera.get_frame()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# Route for video feed, utilizing the video streaming generator function
@app.route('/video_feed')
def video_feed():
    return Response(gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Route to get the current DataFrame as JSON
@app.route('/t')
def gen_table():
    return df1.to_json(orient='records')

# Route to start capturing
@app.route('/start_capture', methods=['POST'])
def start_capture():
    global capture_flag
    capture_flag = True
    return jsonify(success=True)

# Route to stop capturing
@app.route('/stop_capture', methods=['POST'])
def stop_capture():
    global capture_flag
    capture_flag = False
    return jsonify(success=True)

# Run the Flask app
if __name__ == '__main__':
    app.debug = True
    app.run()
