# 퍼스널컬러 기반 증명사진 웹 어플리케이션
---
## 시연영상
![Image](https://github.com/user-attachments/assets/0e9c0f7c-9db6-486c-a5fa-de430d5513f9)

---
## 기술스택
### front-end
![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
![TypeScript](https://img.shields.io/badge/typescript-%23007ACC.svg?style=for-the-badge&logo=typescript&logoColor=white)
![Next JS](https://img.shields.io/badge/Next-black?style=for-the-badge&logo=next.js&logoColor=white)

### back-end
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-%23EE4C2C.svg?style=for-the-badge&logo=PyTorch&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-%23ffffff.svg?style=for-the-badge&logo=Matplotlib&logoColor=black)
![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white)
![OpenCV](https://img.shields.io/badge/opencv-%23white.svg?style=for-the-badge&logo=opencv&logoColor=white)
![SciPy](https://img.shields.io/badge/SciPy-%230C55A5.svg?style=for-the-badge&logo=scipy&logoColor=%white)

---
## 외부 API
### 백그라운드 제거 
https://github.com/danielgatis/rembg  
### 얼굴감지
https://github.com/FacePerceiver/facer
### 옷 적용
https://github.com/yisol/IDM-VTON

---
## 데이터 파이프라인
1. 이미지 업로드 및 규격화
사용자 이미지를 수신하고 OpenCV의 CascadeClassifier를 이용해 얼굴을 탐지한 후, 3x4 증명사진 비율로 이미지를 자동 크롭합니다.
```
# app.py
@app.route('/upload', methods=['POST'])
def upload_image():
    # ... 파일 저장 로직 ...
    id_photo_path = create_id_photo(save_path) # 얼굴 인식 및 자동 크롭 실행
    # ...
```

2. AI 분석 및 추천 이미지 생성
규격화된 이미지에서 배경을 제거하고, facer로 피부 톤을 분석하여 어울리는 배경색을 추천합니다. 그 후 자연스러운 보정 효과를 적용해 3개의 후보 이미지를 생성합니다.
```
# main.py
def generate_recommended_images(image_path: str) -> list:
    # 1. 배경 제거
    foreground = remove_background_rembg(image_path)
    
    # 2. 얼굴 분석으로 퍼스널 컬러 진단
    hsv_data = analyze_face(image_path)
    palette = get_recommended_backgrounds(hsv_data)

    # 3. 추천 배경 적용 및 이미지 보정
    return apply_recommended_backgrounds(foreground, image_path, palette)
```
get_recommended_background는 이런 형태로 존재하여 피부 톤에 맞는 색이 적용됩니다.
```
global latest_color_category

    h, s, v = hsv_data['h'], hsv_data['s'] / 100, hsv_data['v'] / 100
    print(f"🔥 분석된 HSV 값: H={h:.1f}, S={s:.2f}, V={v:.2f}")

    # 개선된 톤 테이블 - 더 넓은 범위로 수정
    tone_table = [
        # (톤 이름, 계절 카테고리, H 범위, S 범위, V 범위)

        # 🌸 봄 (따뜻하고 밝음) - H: 0-90도 (따뜻한 색조)
        ('봄 라이트', '봄', (0, 90), (0.05, 0.4), (0.7, 1.0)),  # 밝고 연한 따뜻한 톤
        ('봄 브라이트', '봄', (0, 80), (0.3, 0.8), (0.75, 1.0)),  # 밝고 선명한 따뜻한 톤
        ('봄 웜', '봄', (0, 70), (0.2, 0.6), (0.5, 0.9)),  # 따뜻한 중간 톤

        # 🌊 여름 (차갑고 부드러움) - H: 180-300도 (차가운 색조)
        ('여름 라이트', '여름', (180, 300), (0.05, 0.4), (0.65, 1.0)),  # 밝고 연한 차가운 톤
        ('여름 뮤트', '여름', (160, 280), (0.1, 0.45), (0.4, 0.8)),  # 부드러운 차가운 톤
        ('여름 쿨', '여름', (170, 260), (0.15, 0.5), (0.55, 0.85)),  # 차가운 중간 톤

        # 🍂 가을 (따뜻하고 깊이감 있음) - H: 10-60도, 낮은 명도
        ('가을 뮤트', '가을', (10, 80), (0.15, 0.5), (0.3, 0.7)),  # 부드러운 따뜻한 어두운 톤
        ('가을 웜', '가을', (0, 60), (0.4, 0.9), (0.3, 0.75)),  # 진한 따뜻한 톤
        ('가을 다크', '가을', (5, 50), (0.3, 0.8), (0.15, 0.55)),  # 어두운 따뜻한 톤

        # ❄️ 겨울 (차갑고 또렷함) - H: 240-360도, 높은 대비
        ('겨울 브라이트', '겨울', (200, 360), (0.4, 1.0), (0.7, 1.0)),  # 밝고 선명한 차가운 톤
        ('겨울 딥', '겨울', (220, 340), (0.3, 0.8), (0.2, 0.6)),  # 어두운 차가운 톤
        ('겨울 쿨', '겨울', (180, 320), (0.25, 0.9), (0.45, 0.9)),  # 차가운 중간 톤

        # 🌟 뉴트럴 (중성적) - 낮은 채도의 모든 색조
        ('뉴트럴 라이트', '뉴트럴', (0, 360), (0.0, 0.15), (0.65, 1.0)),  # 매우 연한 중성 톤
        ('뉴트럴 미디엄', '뉴트럴', (0, 360), (0.0, 0.2), (0.4, 0.7)),  # 중간 중성 톤
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

    print(f"🎯 추론 결과: {latest_color_category} (카테고리: {category})")
    return tone_palette[category]

```

3. 가상 의상 피팅
사용자가 선택한 이미지에 IDM-VTON 모델을 사용하여 가상으로 옷을 합성합니다. gradio_client를 통해 외부 API와 통신합니다.
```
# main.py
def apply_outfit_synthesis(person_image_path: str, outfit_type: str) -> str:
    # ...
    # IDM-VTON API 클라이언트 초기화
    client = Client("yisol/IDM-VTON")

    # 원격 API로 이미지와 의상 정보를 보내 결과 예측
    result = client.predict(
        garm_img=file(cloth_path),      # 의상 이미지
        dict={"background": file(person_image_path)}, # 원본 인물 이미지
        api_name="/tryon"
    )
    # ...
```

4. 💾 최종 결과 전송
사용자가 모든 옵션(배경, 의상)을 선택하면, 미리 생성해둔 최종 이미지 파일 경로를 바탕으로 사용자에게 이미지를 전송합니다.
```
# app.py
@app.route('/final-image', methods=['GET'])
def get_final_image():
    if not final_image_path or not os.path.exists(final_image_path):
        return jsonify({'success': False, 'message': '최종 이미지가 없습니다'}), 400

    # 최종 선택된 이미지의 base64 인코딩 문자열 반환
    return jsonify({
        'success': True,
        'image': image_to_base64(final_image_path)
    })
```
