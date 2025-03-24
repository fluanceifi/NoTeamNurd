import cv2
from flask import Flask, render_template, Response, session, redirect, url_for

app = Flask(__name__)


camera = cv2.VideoCapture(0)

def get_frames():
    while True:
        success, frame = camera.read()
        cv2.waitKey(33)  # 30 프레임

        if not success:
            yield "fail :("
            continue
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # 프레임을 연결하고 결과를 반환
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
@app.route('/')
def index():
    return render_template('upload.html')




@app.route('/upload')
def upload():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('index'))
    return render_template('upload.html')

@app.route('/video_feed')
def video_feed():
    return Response(get_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
