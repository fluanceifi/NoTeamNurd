from flask import Flask, render_template, Response, jsonify
from camera import Camera
import os
import time

camera = Camera()

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/video_feed')
def video_feed():
    return Response(camera.get_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture', methods=['POST'])
def capture():
    image_path = camera.capture()
    if image_path:
        return jsonify({'success': True, 'image_rul' : image_path})
    return jsonify({'success': False})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)