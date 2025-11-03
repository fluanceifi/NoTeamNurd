from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import base64
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
from rembg import remove
import torch
import facer
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
from flask_mail import Mail, Message
from gradio_client import Client, file
import shutil

latest_paths = []
outfit_preview_paths = {}  # {'original': 'path1', 'formal': 'path2', 'casual': 'path3'}
final_image_path = None
selected_gender = None
latest_color_category = None

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


def apply_natural_enhancement(image: Image.Image, enhancement_level: str = "medium") -> Image.Image:
    """
    자연스러운 뽀샵 효과를 적용합니다.
    enhancement_level: "light", "medium", "strong"
    """

    # 강도 설정
    enhancement_settings = {
        "light": {
            "brightness": 1.05,
            "contrast": 1.03,
            "color": 1.02,
            "sharpness": 1.02,
            "smooth_strength": 0.3
        },
        "medium": {
            "brightness": 1.08,
            "contrast": 1.05,
            "color": 1.05,
            "sharpness": 1.05,
            "smooth_strength": 0.5
        },
        "strong": {
            "brightness": 1.12,
            "contrast": 1.08,
            "color": 1.08,
            "sharpness": 1.08,
            "smooth_strength": 0.7
        }
    }

    settings = enhancement_settings.get(enhancement_level, enhancement_settings["medium"])

    # PIL Image를 numpy array로 변환
    img_array = np.array(image)

    # 1. 피부 스무딩 (자연스러운 블러 효과)
    # 가우시안 블러로 부드럽게 만들기
    blurred = cv2.GaussianBlur(img_array, (15, 15), 0)

    # 원본과 블러된 이미지를 적절히 혼합
    smooth_strength = settings["smooth_strength"]
    smoothed = cv2.addWeighted(img_array, 1 - smooth_strength, blurred, smooth_strength, 0)

    # numpy array를 다시 PIL Image로 변환
    enhanced_image = Image.fromarray(smoothed.astype(np.uint8))

    # 2. 밝기 조정 (자연스럽게 밝게)
    brightness_enhancer = ImageEnhance.Brightness(enhanced_image)
    enhanced_image = brightness_enhancer.enhance(settings["brightness"])

    # 3. 대비 조정 (선명하게)
    contrast_enhancer = ImageEnhance.Contrast(enhanced_image)
    enhanced_image = contrast_enhancer.enhance(settings["contrast"])

    # 4. 색상 채도 조정 (생기있게)
    color_enhancer = ImageEnhance.Color(enhanced_image)
    enhanced_image = color_enhancer.enhance(settings["color"])

    # 5. 선명도 조정 (자연스럽게 또렷하게)
    sharpness_enhancer = ImageEnhance.Sharpness(enhanced_image)
    enhanced_image = sharpness_enhancer.enhance(settings["sharpness"])

    return enhanced_image


def detect_face_region(image_path: str) -> tuple:
    """
    얼굴 영역을 감지하여 좌표를 반환합니다.
    """
    img = cv2.imread(image_path)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    if len(faces) > 0:
        return max(faces, key=lambda f: f[2] * f[3])  # 가장 큰 얼굴 반환
    return None


def apply_selective_enhancement(image: Image.Image, face_coords: tuple = None,
                                enhancement_level: str = "medium") -> Image.Image:
    """
    얼굴 영역에만 집중적으로 뽀샵을 적용합니다.
    """
    if face_coords is None:
        return apply_natural_enhancement(image, enhancement_level)

    x, y, w, h = face_coords
    img_array = np.array(image)

    # 얼굴 영역 추출
    face_region = img_array[y:y + h, x:x + w]
    face_img = Image.fromarray(face_region)

    # 얼굴 영역에만 강화 효과 적용
    enhanced_face = apply_natural_enhancement(face_img, enhancement_level)
    enhanced_face_array = np.array(enhanced_face)

    # 원본 이미지에 enhanced 얼굴 영역을 다시 합성
    result_array = img_array.copy()
    result_array[y:y + h, x:x + w] = enhanced_face_array

    return Image.fromarray(result_array)


def remove_background_rembg(image_path: str) -> Image.Image:
    """
    rembg 라이브러리를 사용하여 배경을 제거합니다.
    """
    from rembg import remove
    input_image = Image.open(image_path)
    output_image = remove(input_image)
    return output_image


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

    skin_mask = (parsed_classes[0] == 1).squeeze(0).squeeze(0).cpu().numpy().astype(bool)

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
        'h': float(round(mean_h, 1)),
        's': float(round(mean_s, 1)),
        'v': float(round(mean_v, 1))
    }


def get_recommended_backgrounds(hsv_data: dict) -> list:
    global latest_color_category

    h, s, v = hsv_data['h'], hsv_data['s'] / 100, hsv_data['v'] / 100
    print(f"🔥 분석된 HSV 값: H={h:.1f}, S={s:.2f}, V={v:.2f}")

    # 개선된 톤 테이블 - 더 넓은 범위로 수정
    tone_table = [
        # (톤 이름, 계절 카테고리, H 범위, S 범위, V 범위)

        # 🌸 봄 (따뜻하고 밝음) - H: 0-90도 (따뜻한 색조)
        # 특징: High V (밝음)
        ('봄 라이트', '봄', (0, 70), (0.1, 0.5), (0.75, 1.0)),  # 저채도, 고명도
        ('봄 브라이트', '봄', (0, 80), (0.6, 1.0), (0.7, 1.0)),  # 고채도, 고명도
        ('봄 웜', '봄', (0, 70), (0.3, 0.8), (0.6, 0.95)),  # (True) 중~고채도, 중~고명도

        # 🌊 여름 (차갑고 부드러움) - H: 180-300도 (차가운 색조)
        # 특징: Low S (부드러움)
        ('여름 라이트', '여름', (180, 300), (0.05, 0.35), (0.75, 1.0)),  # 저채도, 고명도
        ('여름 뮤트', '여름', (160, 280), (0.1, 0.4), (0.4, 0.8)),  # 저채도, 중명도
        ('여름 쿨', '여름', (170, 320), (0.15, 0.5), (0.5, 0.9)),  # (True) 저~중채도, 중~고명도

        # 🍂 가을 (따뜻하고 깊이감 있음) - H: 10-80도, 낮은 명도
        # 특징: Low V (어두움)
        ('가을 뮤트', '가을', (10, 80), (0.1, 0.45), (0.3, 0.7)),  # 저채도, 저~중명도
        ('가을 웜', '가을', (0, 60), (0.4, 0.9), (0.3, 0.75)),  # (True) 중~고채도, 저~중명도
        ('가을 다크', '가을', (5, 50), (0.3, 0.9), (0.15, 0.55)),  # 중~고채도, 저명도

        # ❄️ 겨울 (차갑고 또렷함) - H: 240-360도 (쿨톤) + 0-15 (쿨톤 레드)
        # 특징: High S (선명함) / High Contrast (고대비)
        # (참고: 겨울 톤은 330-360, 0-15 범위의 '쿨톤 레드/핑크'를 포함하는 것이 정확합니다)
        ('겨울 브라이트', '겨울', [(0, 15), (310, 360)], (0.7, 1.0), (0.7, 1.0)),  # 고채도, 고명도
        ('겨울 딥', '겨울', [(0, 20), (220, 340)], (0.5, 1.0), (0.2, 0.6)),  # 고채도, 저명도
        ('겨울 쿨', '겨울', [(0, 15), (180, 320)], (0.6, 1.0), (0.45, 0.9)),  # (True) 고채도, 중명도

        # 🌟 뉴트럴 (중성적) - 낮은 채도의 모든 색조
        ('뉴트럴 라이트', '뉴트럴', (0, 360), (0.0, 0.15), (0.7, 1.0)),  # 매우 연한 중성 톤 (고명도)
        ('뉴트럴 미디엄', '뉴트럴', (0, 360), (0.0, 0.2), (0.4, 0.7)),  # 중간 중성 톤 (중명도)
    ]

    # 계절 매핑 (3가지 추천색 각각 RGB값) - 더 자연스러운 색상으로 수정
    tone_palette = {
        '봄': [(255, 248, 220), (255, 235, 205), (248, 225, 190)],  # 따뜻한 아이보리, 피치, 베이지
        '여름': [(240, 248, 255), (225, 240, 255), (210, 230, 250)],  # 시원한 블루 화이트
        '가을': [(255, 228, 196), (222, 184, 135), (205, 160, 120)],  # 따뜻한 베이지, 카키
        '겨울': [(248, 248, 255), (230, 230, 250), (220, 220, 240)],  # 차가운 화이트, 라벤더
        '뉴트럴': [(245, 245, 245), (235, 235, 235), (225, 225, 225)]  # 중성 그레이 톤
    }

    # 계절 카테고리 판단 - 순서 중요 (더 구체적인 조건부터)
    best_match = None
    best_score = -1

    for tone_name, category, hr, sr, vr in tone_table:
        # 각 조건에 대한 점수 계산
        h_match = hr[0] <= h <= hr[1] or (hr[0] > hr[1] and (h >= hr[0] or h <= hr[1]))  # 360도 순환 고려
        s_match = sr[0] <= s <= sr[1]
        v_match = vr[0] <= v <= vr[1]

        # 매치되는 조건의 개수로 점수 계산
        score = sum([h_match, s_match, v_match])

        # 완전 매치 우선
        if score == 3:
            latest_color_category = tone_name
            print(f"✅ 완전 매치: {tone_name} (카테고리: {category})")
            return tone_palette[category]

        # 부분 매치 중 최고 점수 기록
        if score > best_score:
            best_score = score
            best_match = (tone_name, category)

    # 부분 매치라도 있으면 사용
    if best_match and best_score >= 2:  # 3개 중 2개 이상 매치
        latest_color_category = best_match[0]
        print(f"🔍 부분 매치: {best_match[0]} (점수: {best_score}/3)")
        return tone_palette[best_match[1]]

    # 여전히 매치가 안 되면 HSV 값을 기반으로 추론
    print(f"⚠️ 직접 매치 실패, HSV 기반 추론 시작...")

    # H(색조) 기반 1차 분류
    if 0 <= h <= 90:  # 따뜻한 색조 (빨강~노랑)
        if v >= 0.65:  # 밝은 편
            if s <= 0.3:  # 채도 낮음
                category = '뉴트럴'
                latest_color_category = '뉴트럴 라이트'
            else:  # 채도 높음
                category = '봄'
                latest_color_category = '봄 라이트'
        else:  # 어두운 편
            category = '가을'
            latest_color_category = '가을 뮤트'
    elif 180 <= h <= 300:  # 차가운 색조 (파랑~보라)
        if v >= 0.6:  # 밝은 편
            category = '여름'
            latest_color_category = '여름 라이트'
        else:  # 어두운 편
            category = '겨울'
            latest_color_category = '겨울 딥'
    else:  # 중간 색조 또는 특수한 경우
        if s <= 0.2:  # 매우 낮은 채도
            category = '뉴트럴'
            latest_color_category = '뉴트럴 미디엄'
        elif v >= 0.7:  # 매우 밝음
            category = '여름'
            latest_color_category = '여름 라이트'
        else:
            category = '가을'
            latest_color_category = '가을 뮤트'

    print(f" 추론 결과: {latest_color_category} (카테고리: {category})")
    return tone_palette[category]


def apply_recommended_backgrounds(foreground_img: Image.Image, base_path: str, rgb_list: list,
                                  enhancement_level: str = "light") -> list:  # 기본값도 "light"로 바꿈
    paths = []

    for idx, rgb in enumerate(rgb_list):
        # 배경 적용
        bg = Image.new("RGBA", foreground_img.size, rgb + (255,))
        bg.paste(foreground_img, (0, 0), foreground_img)
        bg = bg.convert("RGB")

        #  항상 light 보정으로 고정
        enhanced_bg = apply_natural_enhancement(bg, enhancement_level)

        path = base_path.replace('.jpg', f'_reco{idx + 1}_{enhancement_level}.jpg')
        enhanced_bg.save(path)
        paths.append(path)

    return paths



def generate_recommended_images(image_path: str) -> list:
    """
    배경 제거, 퍼스널 컬러 분석, 뽀샵 효과가 적용된 이미지들을 생성합니다.
    """
    foreground = remove_background_rembg(image_path)  # 배경 제거된 인물 이미지
    hsv_data = analyze_face(image_path)  # 피부 HSV 분석
    if hsv_data is None:
        raise Exception("HSV 분석 실패")

    palette = get_recommended_backgrounds(hsv_data)  # 퍼스널컬러 추천 배경 3가지
    return apply_recommended_backgrounds(foreground, image_path, palette)


def setup_outfit_assets():
    """
    성별별 옷 이미지 파일들을 설정합니다.
    """
    # 성별별 디렉토리 생성
    male_dir = 'assets/male'
    female_dir = 'assets/female'

    os.makedirs(male_dir, exist_ok=True)
    os.makedirs(female_dir, exist_ok=True)

    # 성별별 필요 파일 목록
    required_files = {
        'male': [
            'assets/male/formal_suit.jpg',  # 남성 정장
            'assets/male/casual_shirt.jpg'  # 남성 캐주얼
        ],
        'female': [
            'assets/female/formal_dress.jpg',  # 여성 정장/드레스
            'assets/female/casual_blouse.jpg'  # 여성 캐주얼
        ]
    }

    # 파일 존재 여부 확인
    missing_files = []
    for gender, files in required_files.items():
        for file_path in files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
                print(f"⚠️  필요한 {gender} 옷 이미지가 없습니다: {file_path}")

    if missing_files:
        print("\n📁 다음 구조로 옷 이미지를 추가해주세요:")
        print("assets/")
        print("├── male/")
        print("│   ├── formal_suit.jpg")
        print("│   └── casual_shirt.jpg")
        print("└── female/")
        print("    ├── formal_dress.jpg")
        print("    └── casual_blouse.jpg")
    else:
        print("✅ 모든 성별별 옷 이미지가 준비되었습니다.")

    return True


def apply_outfit_synthesis(person_image_path: str, outfit_type: str) -> str:
    """
    IDM-VTON API를 사용해서 성별에 맞는 옷을 합성합니다.
    """
    global selected_gender

    try:
        # 성별별 옷 경로 설정
        outfit_paths = {
            'male': {
                'formal': 'assets/male/formal_suit.jpg',
                'casual': 'assets/male/casual_shirt.jpg',
                'original': person_image_path
            },
            'female': {
                'formal': 'assets/female/formal_dress.jpg',
                'casual': 'assets/female/casual_blouse.jpg',
                'original': person_image_path
            }
        }

        if outfit_type == 'original':
            return person_image_path

        # 현재 성별에 맞는 옷 경로 선택
        current_gender = selected_gender or 'male'  # 기본값 male
        cloth_path = outfit_paths.get(current_gender, {}).get(outfit_type)

        if not cloth_path or not os.path.exists(cloth_path):
            print(f"❌ {current_gender} {outfit_type} 옷 이미지를 찾을 수 없습니다: {cloth_path}")
            return person_image_path

        print(f"🔄 {current_gender} {outfit_type} 스타일 합성 시작...")

        # client = Client("yisol/IDM-VTON", hf_token=os.getenv("HF_TOKEN"))

        NGROK_URL = "https://abcd-1234.ngrok-free.app"
        client = Client(NGROK_URL)

        result = client.predict(
            dict={
                "background": file(person_image_path),
                "layers": [],
                "composite": None
            },
            garm_img=file(cloth_path),
            garment_des=f"{current_gender} {outfit_type} clothing",  # 성별 정보도 포함
            is_checked=True,
            is_checked_crop=False,
            denoise_steps=30,
            seed=42,
            api_name="/tryon"
        )

        result_path = person_image_path.replace('.jpg', f'_{current_gender}_{outfit_type}_tryon.jpg')

        if os.path.exists(result[0]):
            shutil.copy2(result[0], result_path)
            print(f"✅ {current_gender} {outfit_type} 합성 완료: {result_path}")
            return result_path
        else:
            print(f"❌ 합성 결과 파일을 찾을 수 없습니다: {result[0]}")
            return person_image_path

    except Exception as e:
        print(f"❌ 옷 합성 중 오류 발생: {str(e)}")
        return person_image_path


app = Flask(__name__)
CORS(app)


load_dotenv()

# Flask-Mail 설정 (Gmail 예시)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'dbtmdwns990203@gmail.com'  # 실제 사용하는 구글 이메일 주소
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")      # 구글 앱 비밀번호
app.config['MAIL_DEFAULT_SENDER'] = ('니톤내톤', 'dbtmdwns990203@gmail.com') # 보내는 사람 이름/주소

# Mail 객체 초기화
mail = Mail(app)


UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def image_to_base64(path):
    with open(path, 'rb') as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')


latest_paths = []  # 전역 변수



@app.route('/upload', methods=['POST'])
def upload_image():
    global latest_paths, selected_gender

    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '파일이 없습니다'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '파일명이 비어 있습니다'}), 400

    # 성별 정보 받기
    selected_gender = request.form.get('gender', 'male')  # 기본값은 'male'
    print(f"🔥 선택된 성별: {selected_gender}")

    save_path = os.path.join(UPLOAD_FOLDER, 'capture.jpg')
    file.save(save_path)
    print(f' 원본 이미지 저장 완료: {save_path}')

    # Create ID photo style image
    try:
        # 1. 먼저 ID 사진 스타일로 크롭
        id_photo_path = create_id_photo(save_path)
        print(f' ID 사진 스타일 변환 완료: {id_photo_path}')

        # 2. 배경 제거 및 퍼스널 컬러 배경 적용 (뽀샵 포함)
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

        # 각 이미지의 뽀샵 강도 정보도 함께 전달
        image_info = []
        for idx, (path, img_b64) in enumerate(zip(latest_paths, base64_imgs)):
            enhancement_level = ["약간", "중간", "강하게"][idx % 3]
            image_info.append({
                'image': img_b64,
                'enhancement': enhancement_level,
                'description': f'퍼스널 컬러 배경 {idx + 1} - {enhancement_level} 보정'
            })

        return jsonify({
            'success': True,
            'images': base64_imgs,  # 기존 호환성 유지
            'image_info': image_info,  # 새로운 상세 정보
            'color_category': latest_color_category
        })
    else:
        return jsonify({'success': False, 'message': '업로드된 이미지가 없습니다'}), 404


# 추가: 사용자가 특정 뽀샵 강도를 선택할 수 있는 엔드포인트
@app.route('/enhance', methods=['POST'])
def enhance_image():
    """
    사용자가 선택한 뽀샵 강도로 이미지를 재처리합니다.
    """
    data = request.json
    enhancement_level = data.get('level', 'medium')  # light, medium, strong
    image_index = data.get('index', 0)  # 어떤 이미지를 기준으로 할지

    if not latest_paths or image_index >= len(latest_paths):
        return jsonify({'success': False, 'message': '처리할 이미지가 없습니다'}), 400

    try:
        base_path = latest_paths[image_index]
        # 원본 이미지 로드
        original_path = base_path.split('_reco')[0] + '_idphoto.jpg'

        # 새로운 강도로 재처리
        foreground = remove_background_rembg(original_path)
        hsv_data = analyze_face(original_path)
        palette = get_recommended_backgrounds(hsv_data)

        # 사용자가 선택한 강도로만 처리
        bg = Image.new("RGBA", foreground.size, palette[0] + (255,))
        bg.paste(foreground, (0, 0), foreground)
        bg = bg.convert("RGB")
        enhanced_bg = apply_natural_enhancement(bg, enhancement_level)

        # 임시 파일로 저장
        temp_path = original_path.replace('.jpg', f'_custom_{enhancement_level}.jpg')
        enhanced_bg.save(temp_path)

        return jsonify({
            'success': True,
            'image': image_to_base64(temp_path),
            'enhancement': enhancement_level
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'이미지 처리 오류: {str(e)}'}), 500


# 전역 변수에 의상별 경로 저장
outfit_preview_paths = {}  # {'original': 'path1', 'formal': 'path2', 'casual': 'path3'}


@app.route('/outfit-preview', methods=['POST'])
def get_outfit_preview():
    global latest_paths, outfit_preview_paths

    data = request.json
    selected_index = data.get('selected_index', 0)

    if not latest_paths or selected_index >= len(latest_paths):
        return jsonify({'success': False, 'message': '선택된 이미지가 없습니다'}), 400

    try:
        selected_image_path = latest_paths[selected_index]
        outfit_types = ['original', 'formal', 'casual']
        previews = []

        # 의상별 경로 초기화
        outfit_preview_paths = {}

        for outfit_type in outfit_types:
            if outfit_type == 'original':
                result_path = selected_image_path
            else:
                result_path = apply_outfit_synthesis(selected_image_path, outfit_type)

            # 경로 저장
            outfit_preview_paths[outfit_type] = result_path

            previews.append({
                'type': outfit_type,
                'image': image_to_base64(result_path),
                'label': {'original': '원본', 'formal': '정장', 'casual': '캐주얼'}[outfit_type]
            })

        return jsonify({
            'success': True,
            'options': previews
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'미리보기 생성 오류: {str(e)}'}), 500


@app.route('/generate-final', methods=['POST'])
def generate_final_image():
    global final_image_path, outfit_preview_paths

    data = request.json
    selected_outfit = data.get('selected_outfit', 'original')

    try:
        # 이미 생성된 이미지 경로 사용 (재합성하지 않음)
        if selected_outfit in outfit_preview_paths:
            final_image_path = outfit_preview_paths[selected_outfit]
            print(f"✅ 기존 {selected_outfit} 이미지 사용: {final_image_path}")
        else:
            return jsonify({'success': False, 'message': '선택된 의상 이미지를 찾을 수 없습니다'}), 400

        return jsonify({
            'success': True,
            'message': '최종 이미지가 설정되었습니다'
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'최종 이미지 설정 오류: {str(e)}'}), 500

@app.route('/final-image', methods=['GET'])
def get_final_image():
    """
    생성된 최종 이미지를 반환합니다.
    """
    global final_image_path

    if not final_image_path or not os.path.exists(final_image_path):
        return jsonify({'success': False, 'message': '최종 이미지가 없습니다'}), 400

    try:
        return jsonify({
            'success': True,
            'image': image_to_base64(final_image_path)
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'이미지 로드 오류: {str(e)}'}), 500

# ... (기존 /final-image 엔드포인트 아래에 추가)

@app.route('/send-email', methods=['POST'])
def send_final_image_email():
    """
    최종 생성된 이미지를 이메일로 전송합니다.
    """
    global final_image_path

    data = request.json
    recipient_email = data.get('email')

    if not recipient_email:
        return jsonify({'success': False, 'message': '수신자 이메일 주소가 필요합니다.'}), 400

    if not final_image_path or not os.path.exists(final_image_path):
        return jsonify({'success': False, 'message': '전송할 최종 이미지가 없습니다.'}), 404

    try:
        # 이메일 메시지 객체 생성
        msg = Message(
            subject="[ID Photo Service] 생성된 증명사진입니다.",
            recipients=[recipient_email]
        )

        # 이메일 본문 설정
        msg.body = "요청하신 증명사진을 첨부합니다. 이용해주셔서 감사합니다."
        msg.html = "<p>요청하신 증명사진을 첨부합니다.</p><p>이용해주셔서 감사합니다.</p>"

        # 파일 첨부
        with app.open_resource(final_image_path) as fp:
            # 파일명만 추출하여 첨부 파일 이름으로 사용
            file_name = os.path.basename(final_image_path)
            msg.attach(file_name, 'image/jpeg', fp.read())

        # 이메일 발송
        mail.send(msg)

        return jsonify({
            'success': True,
            'message': f'{recipient_email}(으)로 이미지를 성공적으로 전송했습니다.'
        })

    except Exception as e:
        print(f"❌ 이메일 전송 오류: {str(e)}")
        return jsonify({'success': False, 'message': f'이메일 전송 중 오류가 발생했습니다: {str(e)}'}), 500



if __name__ == '__main__':
    # 옷 이미지 에셋 설정
    setup_outfit_assets()

    # gradio_client 설치 확인
    try:
        from gradio_client import Client, file

        print("✅ gradio_client 준비 완료")
    except ImportError:
        print("❌ gradio_client가 설치되지 않았습니다.")
        print("다음 명령어로 설치해주세요: pip install gradio_client")
        exit(1)

    app.run(host='0.0.0.0', port=5050, debug=True)