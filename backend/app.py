from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import base64
from PIL import Image
import cv2
import numpy as np
from rembg import remove


def create_id_photo(image_path: str, target_ratio=(3, 4)) -> str:
    """
    Create an ID photo by detecting face and cropping to include face and some shoulders
    """
    # Load the image
    img = cv2.imread(image_path)
    if img is None:
        raise Exception("Failed to load image")

    # Convert to RGB for face detection (OpenCV uses BGR by default)
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Load the face detection model
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Detect faces
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    if len(faces) == 0:
        print("No face detected, using default resizing")
        # Fall back to your original resize function if no face is detected
        pil_img = Image.open(image_path)
        width, height = pil_img.size
        target_width = width
        target_height = int(width * target_ratio[1] / target_ratio[0])

        if target_height > height:
            padding = (target_height - height) // 2
            new_image = Image.new("RGB", (width, target_height), (255, 255, 255))
            new_image.paste(pil_img, (0, padding))
        else:
            top = (height - target_height) // 2
            new_image = pil_img.crop((0, top, width, top + target_height))
    else:
        # Get the largest face (in case multiple faces are detected)
        (x, y, w, h) = max(faces, key=lambda f: f[2] * f[3])

        # Calculate the ID photo crop dimensions
        img_height, img_width = img.shape[:2]

        # Face center
        face_center_x = x + w // 2
        face_center_y = y + h // 2

        # 증명사진 스타일에 맞게 얼굴 비율 조정
        # 얼굴이 이미지에서 차지하는 비율 (세 번째 이미지 스타일)
        face_scale = 0.4  # 얼굴이 전체 높이의 40% 정도 차지하도록 설정

        # Calculate new height based on face height
        new_height = int(h / face_scale)

        # Calculate new width based on target aspect ratio
        new_width = int(new_height * target_ratio[0] / target_ratio[1])

        # 얼굴 위치 조정 - 상단에 더 많은 여백을 주기 위해 위치를 아래로 조정
        # 세 번째 이미지처럼 얼굴이 중앙보다 약간 위쪽에 위치하도록 설정
        face_top_position = 0.38  # 얼굴 상단이 이미지 상단에서 38% 위치에 오도록 조정

        # Calculate top-left corner of crop area
        crop_x = max(0, face_center_x - new_width // 2)
        crop_y = max(0, face_center_y - int(face_top_position * new_height))

        # 위쪽이 잘리지 않도록 추가 조정
        if crop_y < 0:
            # 상단 여백이 부족하면 하단을 더 포함
            crop_y = 0

        # Adjust if crop area goes beyond image boundaries
        if crop_x + new_width > img_width:
            crop_x = img_width - new_width
        if crop_y + new_height > img_height:
            crop_y = img_height - new_height

        # Ensure crop coordinates are non-negative
        crop_x = max(0, crop_x)
        crop_y = max(0, crop_y)

        # Crop the image
        cropped = img[crop_y:crop_y + new_height, crop_x:crop_x + new_width]

        # Convert back to PIL for saving
        new_image = Image.fromarray(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB))

    # 결과 이미지 크기 조정
    # 이미지 크기 조정 대신 비율만 유지
    output_path = image_path.replace('.jpg', '_idphoto.jpg')
    new_image.save(output_path)
    return output_path


def remove_background_rembg(image_path: str) -> str:
    """
    rembg 라이브러리를 사용하여 배경을 제거하고 하얀색 배경으로 변경
    """
    from rembg import remove

    # 이미지 로드
    input_image = Image.open(image_path)

    # rembg를 사용하여 배경 제거
    output_image = remove(input_image)

    # 하얀색 배경 생성
    white_background = Image.new("RGBA", output_image.size, (255, 255, 255, 255))

    # 배경 제거된 이미지를 하얀색 배경 위에 합성
    # 알파 채널을 마스크로 사용
    white_background.paste(output_image, (0, 0), output_image)

    # RGB로 변환 (알파 채널 제거)
    white_background = white_background.convert("RGB")

    #white 이미지 경로 저장 & 이미지 저장
    white_path = image_path.replace('.jpg', '_whitebg.jpg')
    white_background.save(output_path)

    # 추천 계절톤 배경 색상 RGB 값들
    recommended_colors = get_recommended_backgrounds(hsv_data)  # 여기가 핵심!
    recommended_paths = []

    for idx, rgb in enumerate(recommended_colors):
        color_bg = Image.new("RGBA", output_image.size, rgb + (255,))
        color_bg.paste(output_image, (0, 0), output_image)
        color_bg = color_bg.convert("RGB")
        path = image_path.replace('.jpg', f'_reco{idx + 1}.jpg')
        color_bg.save(path)
        recommended_paths.append(path)

    return [white_path] + recommended_paths


def get_recommended_backgrounds(hsv_data):
    h, s, v = hsv_data['h'], hsv_data['s'] / 100, hsv_data['v'] / 100
    tone_table = [
        # (톤 이름, 계절 카테고리, 색상(H) 범위, 채도(S) 범위, 명도(V) 범위)
        ('봄 라이트', '봄', (15, 50), (0.3, 0.6), (0.8, 1.0)),
        ('봄 브라이트', '봄', (10, 45), (0.6, 1.0), (0.8, 1.0)),
        ('봄 웜', '봄', (10, 40), (0.5, 0.8), (0.7, 1.0)),

        ('여름 라이트', '여름', (180, 260), (0.1, 0.4), (0.7, 1.0)),
        ('여름 뮤트', '여름', (180, 250), (0.1, 0.5), (0.5, 0.8)),
        ('여름 쿨', '여름', (190, 260), (0.2, 0.6), (0.6, 0.9)),

        ('가을 뮤트', '가을', (20, 50), (0.2, 0.6), (0.4, 0.7)),
        ('가을 웜', '가을', (10, 40), (0.6, 1.0), (0.4, 0.7)),
        ('가을 다크', '가을', (10, 40), (0.4, 0.7), (0.2, 0.5)),

        ('겨울 브라이트', '겨울', (250, 290), (0.6, 1.0), (0.8, 1.0)),
        ('겨울 딥', '겨울', (250, 300), (0.4, 0.8), (0.2, 0.5)),
        ('겨울 쿨', '겨울', (240, 300), (0.5, 1.0), (0.6, 0.9)),
    ]


    # 계절 매핑 (3가지 추천색 각각 RGB값이다)
    tone_palette = {
        '봄': [(255, 242, 204), (255, 223, 186), (255, 213, 153)],
        '여름': [(204, 229, 255), (186, 215, 255), (153, 204, 255)],
        '가을': [(255, 214, 165), (204, 153, 102), (153, 102, 51)],
        '겨울': [(204, 204, 255), (153, 153, 255), (102, 102, 255)]
    }

    # 계절 카테고리 판단
    for tone_name, category, hr, sr, vr in tone_table:
        if hr[0] <= h <= hr[1] and sr[0] <= s <= sr[1] and vr[0] <= v <= vr[1]:
            return tone_palette[category] #이게 129Line에서 사용됨

    # fallback
    return [(200, 200, 200), (180, 180, 180), (160, 160, 160)]  # 회색 계열




app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def image_to_base64(path):
    with open(path, 'rb') as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')


latest_path = None  # 전역 변수


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
    print(f'✅ 원본 이미지 저장 완료: {save_path}')

    # Create ID photo style image
    try:
        # 1. 먼저 ID 사진 스타일로 크롭
        id_photo_path = create_id_photo(save_path)
        print(f'✅ ID 사진 스타일 변환 완료: {id_photo_path}')

        # 2. 배경 제거 및 하얀색 배경 적용
        whitebg_path = remove_background_rembg(id_photo_path)
        print(f'✅ 배경 제거 및 하얀색 배경 적용 완료: {whitebg_path}')

        latest_path = whitebg_path
    except Exception as e:
        print(f'❌ 이미지 처리 중 오류 발생: {str(e)}')
        return jsonify({'success': False, 'message': f'이미지 처리 오류: {str(e)}'}), 500

    return jsonify({'success': True, 'message': 'ID 사진 변환 완료'})


@app.route('/uploaded', methods=['GET'])
def get_uploaded_images():
    if latest_path and os.path.exists(latest_path):
        base64_img = image_to_base64(latest_path)
        return jsonify({
            'success': True,
            'images': [base64_img, base64_img, base64_img]  # 향후 정장 합성 버전으로 대체됨
        })
    else:
        return jsonify({'success': False, 'message': '업로드된 이미지가 없습니다'}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)