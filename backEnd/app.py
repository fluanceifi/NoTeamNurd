from flask import Flask, render_template, Response, request, jsonify
from camera import camera  # Camera 인스턴스를 가져옴
import clipping as cp
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

#이게 배경흰색으로만 clippingg한거임
@app.route('/white_back_ground', methods=['POST'])
def background():
    try:
        input_path = f'static/captured.jpg'
        output_path = f'static/captured_clipping.jpg'

        bg_removed = remove_background(input_path)
        filled = fill_transparent_background(bg_removed, color_rgb=(255, 255, 255)) #일단 흰색 (나중에 변수로 받아서 퍼스널컬러에 맞게 변환)
        filled.save(output_path, 'JPEG')

        return jsonify({'success': True, 'image_url': output_path, 'result': bg_removed})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True)
