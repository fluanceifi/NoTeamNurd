from flask import Flask, render_template, Response, request, jsonify
import cv2
import os
from face_parser import analyze_face

app = Flask(__name__)
camera = cv2.VideoCapture(0)

@app.route('/')
def index():
    return render_template('upload.html')

def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture', methods=['POST'])
def capture():
    success, frame = camera.read()
    if success:
        path = 'static/captured.jpg'
        cv2.imwrite(path, frame)

        result = analyze_face(path)
        if result is not None:
            return jsonify(result)
        else:
            return jsonify({'error': 'No skin detected'})
    return jsonify({'error': 'Capture failed'})


if __name__ == '__main__':
    app.run(debug=True)
