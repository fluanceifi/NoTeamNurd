from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import base64
from PIL import Image
import cv2
import numpy as np
from rembg import remove
import torch
import facer
import numpy as np
import matplotlib.pyplot as plt


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

    # 1. 이미지 로드
    input_image = Image.open(image_path)

    # 2. rembg를 사용하여 배경 제거
    output_image = remove(input_image)

    return output_image

    # 하얀색 배경 생성
    #white_background = Image.new("RGBA", output_image.size, (255, 255, 255, 255))

    # 배경 제거된 이미지를 하얀색 배경 위에 합성
    # 알파 채널을 마스크로 사용
    #white_background.paste(output_image, (0, 0), output_image)

    # RGB로 변환 (알파 채널 제거)
    #white_background = white_background.convert("RGB")

    #white 이미지 경로 저장 & 이미지 저장
    #white_path = image_path.replace('.jpg', '_whitebg.jpg')
    #white_background.save(white_path)

    # 3. 퍼스널컬러 추출하기



    # 4. 추천 계절톤 배경 색상 RGB 값
    #recommended_colors = get_recommended_backgrounds(hsv_data)  # 여기가 핵심!
    #recommended_paths = []

    #for idx, rgb in enumerate(recommended_colors):
    #    color_bg = Image.new("RGBA", output_image.size, rgb + (255,))
    #    color_bg.paste(output_image, (0, 0), output_image)
    #    color_bg = color_bg.convert("RGB")
    #    path = image_path.replace('.jpg', f'_reco{idx + 1}.jpg')
    #    color_bg.save(path)
    #    recommended_paths.append(path)

    #return recommended_paths

def analyze_face(image_path):


    # 1. 이미지 로드
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    image = facer.hwc2bchw(facer.read_hwc(image_path)).to(device)

    # 2. Face Parsing
    face_detector = facer.face_detector('retinaface/mobilenet', device=device)
    with torch.inference_mode():
        faces = face_detector(image)

    face_parser = facer.face_parser('farl/lapa/448', device=device)
    with torch.inference_mode():
        faces = face_parser(image, faces)

    # 3. 피부 영역 마스크 생성
    seg_logits = faces['seg']['logits']
    seg_probs = seg_logits.softmax(dim=1)
    parsed_classes = seg_probs.argmax(dim=1)

    skin_mask = (parsed_classes == 1).squeeze().cpu().numpy().astype(bool)  # 피부 부위 마스크

    # 🛠 마스크가 정상적으로 생성되었는지 확인
    print(f"🔍 피부 영역 픽셀 개수: {skin_mask.sum()}")
    if skin_mask.sum() == 0:
        print("❗ 피부 영역이 검출되지 않았습니다.")
        return None

    # 4. RGB 색상 분석
    image_np = image[0].permute(1, 2, 0).cpu().numpy()
    skin_pixels = image_np[skin_mask]  # 피부 영역 픽셀 추출

    mean_rgb = np.mean(skin_pixels, axis=0) if skin_pixels.shape[0] > 0 else [0, 0, 0]
    print(f"📊 평균 RGB 값: R={mean_rgb[0]:.1f}, G={mean_rgb[1]:.1f}, B={mean_rgb[2]:.1f}")

    # 5. HSV 변환
    skin_pixels = skin_pixels.astype(np.float32) / 255.0  # 0~1 정규화
    r, g, b = skin_pixels[:, 0], skin_pixels[:, 1], skin_pixels[:, 2]

    cmax = np.max(skin_pixels, axis=1)
    cmin = np.min(skin_pixels, axis=1)
    delta = cmax - cmin

    # H 계산 (회색 계열 방지)
    h = np.zeros_like(cmax)
    mask = delta != 0

    r_eq = (cmax == r) & mask
    g_eq = (cmax == g) & mask
    b_eq = (cmax == b) & mask

    h[r_eq] = (60 * ((g[r_eq] - b[r_eq]) / delta[r_eq])) % 360
    h[g_eq] = (60 * ((b[g_eq] - r[g_eq]) / delta[g_eq]) + 120) % 360
    h[b_eq] = (60 * ((r[b_eq] - g[b_eq]) / delta[b_eq]) + 240) % 360

    h[~mask] = 0  # 회색 계열 (delta == 0)일 경우 H = 0

    # S 계산
    s = np.zeros_like(cmax)
    s[cmax != 0] = delta[cmax != 0] / cmax[cmax != 0]

    # V 계산
    v = cmax

    # 평균 HSV 계산
    mean_h = np.mean(h) if h.size > 0 else 0
    mean_s = np.mean(s) * 100 if s.size > 0 else 0
    mean_v = np.mean(v) * 100 if v.size > 0 else 0

    print(f"📊 평균 HSV 값: H={mean_h:.1f}, S={mean_s:.1f}, V={mean_v:.1f}")

    return {
        #'r': float(round(mean_rgb[0], 1)), rgb는 필요 x
        #'g': float(round(mean_rgb[1], 1)),
        #'b': float(round(mean_rgb[2], 1)),
        'h': float(round(mean_h, 1)),
        's': float(round(mean_s, 1)),
        'v': float(round(mean_v, 1))
    }


def get_recommended_backgrounds(hsv_data: dict) -> list:
    h, s, v = hsv_data['h'], hsv_data['s'] / 100, hsv_data['v'] / 100
    print(f"🔥 분석된 HSV 값: H={h:.1f}, S={s:.2f}, V={v:.2f}")
    tone_table = [
        # (톤 이름, 계절 카테고리, H 범위, S 범위, V 범위)
        # 🌸 봄 (따뜻하고 밝음)
        ('봄 라이트', '봄', (10, 60), (0.2, 0.6), (0.75, 1.0)),
        ('봄 브라이트', '봄', (5, 50), (0.4, 1.0), (0.75, 1.0)),
        ('봄 웜', '봄', (5, 50), (0.35, 0.75), (0.6, 1.0)),

        # 🌊 여름 (차갑고 부드러움)
        ('여름 라이트', '여름', (170, 260), (0.1, 0.5), (0.65, 1.0)),
        ('여름 뮤트', '여름', (160, 260), (0.1, 0.5), (0.45, 0.8)),
        ('여름 쿨', '여름', (170, 280), (0.2, 0.6), (0.55, 0.85)),

        # 🍂 가을 (따뜻하고 깊이감 있음)
        ('가을 뮤트', '가을', (10, 60), (0.2, 0.6), (0.35, 0.7)),
        ('가을 웜', '가을', (5, 55), (0.5, 1.0), (0.35, 0.7)),
        ('가을 다크', '가을', (5, 50), (0.4, 0.8), (0.2, 0.5)),

        # ❄️ 겨울 (차갑고 또렷함)
        ('겨울 브라이트', '겨울', (240, 300), (0.5, 1.0), (0.75, 1.0)),
        ('겨울 딥', '겨울', (230, 310), (0.4, 0.8), (0.25, 0.5)),
        ('겨울 쿨', '겨울', (220, 300), (0.4, 1.0), (0.5, 0.9)),
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

def apply_recommended_backgrounds(foreground_img: Image.Image, base_path: str, rgb_list: list) -> list:
    paths = []
    for idx, rgb in enumerate(rgb_list):
        bg = Image.new("RGBA", foreground_img.size, rgb + (255,))
        bg.paste(foreground_img, (0, 0), foreground_img)
        bg = bg.convert("RGB")

        path = base_path.replace('.jpg', f'_reco{idx + 1}.jpg')
        bg.save(path)
        paths.append(path)
    return paths

def generate_recommended_images(image_path: str) -> list:
    foreground = remove_background_rembg(image_path)          # 배경 제거된 인물 이미지
    hsv_data = analyze_face(image_path)                       # 피부 HSV 분석
    if hsv_data is None:
        raise Exception("HSV 분석 실패")

    palette = get_recommended_backgrounds(hsv_data)           # 퍼스널컬러 추천 배경 3가지
    return apply_recommended_backgrounds(foreground, image_path, palette)


app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def image_to_base64(path):
    with open(path, 'rb') as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')


latest_paths = []  # 전역 변수


@app.route('/upload', methods=['POST'])
def upload_image():
    global latest_paths

    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '파일이 없습니다'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '파일명이 비어 있습니다'}), 400

    save_path = os.path.join(UPLOAD_FOLDER, 'capture.jpg')
    file.save(save_path)
    print(f' 원본 이미지 저장 완료: {save_path}')

    # Create ID photo style image
    try:
        # 1. 먼저 ID 사진 스타일로 크롭
        id_photo_path = create_id_photo(save_path)
        print(f' ID 사진 스타일 변환 완료: {id_photo_path}')

        # 2. 배경 제거 및 하얀색 배경 적용 << 퍼스널컬러로 대체
        #whitebg_path = remove_background_rembg(id_photo_path)
        #print(f' 배경 제거 및 하얀색 배경 적용 완료: {whitebg_path}')

        # 2. 배경 제거 및 퍼스널 컬러 배경 적용
        latest_paths = generate_recommended_images(id_photo_path)
        print(f' 배경 제거 및 퍼스널 배경 적용 완료: {latest_paths}')

    except Exception as e:
        print(f' 이미지 처리 중 오류 발생: {str(e)}')
        return jsonify({'success': False, 'message': f'이미지 처리 오류: {str(e)}'}), 500

    return jsonify({'success': True, 'message': 'ID 사진 변환 완료'})


@app.route('/uploaded', methods=['GET'])
def get_uploaded_images():
    if latest_paths and all(os.path.exists(p) for p in latest_paths):
        base64_imgs = [image_to_base64(p) for p in latest_paths]
        return jsonify({
            'success': True,
            'images': base64_imgs #[base64_img, base64_img, base64_img]를 for문으로 만들었기 때문에 이렇게 대체 가능함. 향후 정장 합성 버전으로 대체됨
        })
    else:
        return jsonify({'success': False, 'message': '업로드된 이미지가 없습니다'}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)