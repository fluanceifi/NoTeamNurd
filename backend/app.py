from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import base64

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def image_to_base64(path):
    with open(path, 'rb') as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

latest_path = None  # 전역 변수로 저장

@app.route('/upload', methods=['POST'])
def upload_image():
    global latest_path
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '파일이 없습니다'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '파일명이 비어 있습니다'}), 400

    save_path = os.path.join(UPLOAD_FOLDER, 'capture.jpg')
    file.save(save_path)
    latest_path = save_path  # ✅ 나중에 GET에서도 쓰기 위해 저장
    print(f'✅ 이미지 저장 완료: {save_path}')

    return jsonify({'success': True, 'message': '이미지 업로드 완료'})  # ✅ 간단 응답

@app.route('/uploaded', methods=['GET'])
def get_uploaded_images():
    if latest_path and os.path.exists(latest_path):
        base64_img = image_to_base64(latest_path)
        return jsonify({
            'success': True,
            'images': [base64_img, base64_img, base64_img]  # 임시 3장
        })
    else:
        return jsonify({'success': False, 'message': '업로드된 이미지가 없습니다'}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
