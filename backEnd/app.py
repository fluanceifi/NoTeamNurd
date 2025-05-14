from flask import Flask, render_template, Response, request, jsonify
from camera import camera  # Camera 인스턴스를 가져옴
from face_parser import analyze_face

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/video_feed')
def video_feed():
    return Response(camera.get_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/capture', methods=['POST'])
def capture():
    filename = camera.capture()
    print(f"Captured: {filename}")

    if filename:
        result = analyze_face(filename)
        if result is not None:
            return jsonify({
                'success': True,
                'image_url': '/' + filename,  # static 폴더 기준 상대 경로
                'result': result
            })
        else:
            return jsonify({'success': False, 'error': 'No skin detected'})

    return jsonify({'success': False, 'error': 'Capture failed'})


if __name__ == '__main__':
    app.run(debug=True)
