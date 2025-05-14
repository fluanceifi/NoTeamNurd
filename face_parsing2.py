# -*- coding: utf-8 -*-
"""
Face parsing 코드 - PyCharm 버전
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import cv2
import os
import torch
import facer

# facer 설치 (최초 1회만 실행)
# pip install git+https://github.com/FacePerceiver/facer.git@main

# 이미지 경로 지정 (여기에 실제 이미지 경로를 입력하세요)
IMAGE_PATH = "./static/capture_1743338766.jpg"  # 실제 이미지 경로로, 이 경로는 수정 필요

# 1. 이미지 로드 및 face parsing
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Using device: {device}")

# 파일 존재 확인
if not os.path.exists(IMAGE_PATH):
    raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {IMAGE_PATH}")

image = facer.hwc2bchw(facer.read_hwc(IMAGE_PATH)).to(device)

face_detector = facer.face_detector('retinaface/mobilenet', device=device)
with torch.inference_mode():
    faces = face_detector(image)

face_parser = facer.face_parser('farl/lapa/448', device=device)
with torch.inference_mode():
    faces = face_parser(image, faces)

# 2. 세그멘테이션 결과
seg_logits = faces['seg']['logits']
seg_probs = seg_logits.softmax(dim=1)
parsed_classes = seg_probs.argmax(dim=1)

# 3. 추출하고 싶은 부위 리스트 (좌우 통합 포함)
merged_labels = {
    'face_skin': [1],
    'eyebrows': [2, 3],
    'eyes': [4, 5],
    'nose': [6],
    'lips': [7, 9],
    'inner_mouth': [8],
    'hair': [10]
}

# 4. 부위별 추출
extracted_parts = {}

for part_name, class_indices in merged_labels.items():
    mask = torch.zeros_like(parsed_classes, dtype=torch.bool)
    for idx in class_indices:
        mask |= (parsed_classes == idx)
    part_image = image * mask.unsqueeze(1).float()  # [B, C, H, W]
    extracted_parts[part_name] = part_image

plt.figure(figsize=(16, 10))
for i, (part_name, part_img) in enumerate(extracted_parts.items()):
    plt.subplot(2, 4, i + 1)
    facer.show_bchw(part_img)
    plt.title(part_name)
plt.tight_layout()
plt.show()

## 여기까지 부위 추출 관련 코드 - 그 다음부터는 색 추출

print(image.shape)

# 원본이미지 [1, 3, H, W] → NumPy [H, W, 3] - 원본이미지를 NumPy에서 쓰기 위해서 변환하는과정.
image_np = image[0].permute(1, 2, 0).cpu().numpy()  # shape: (H, W, 3)

plt.figure(figsize=(8, 8))
plt.imshow(image_np)
plt.title("Original Image")
plt.show()

# 1. 피부 부위 마스크 생성 (클래스 번호 1 = face_skin) - True / False 로 구분된 이미지 - 피부부위 마스크를 만들기 위해서
skin_mask_tensor = (parsed_classes == 1)
skin_mask = skin_mask_tensor.squeeze().cpu().numpy().astype(bool)  # shape: (H, W)

plt.figure(figsize=(8, 8))
plt.imshow(skin_mask)
plt.title("Skin Mask")
plt.show()

skin_pixels = image_np[skin_mask]

# 마스크에서 피부라고 인식한 이미지에 해당하는 픽셀의 값의 평균을 구한다.
if skin_pixels.shape[0] == 0:
    print("❗️마스크에 해당하는 픽셀이 없습니다.")
else:
    mean_rgb = np.mean(skin_pixels, axis=0)
    print(f"📊 평균 RGB 값: R={mean_rgb[0]:.1f}, G={mean_rgb[1]:.1f}, B={mean_rgb[2]:.1f}")

# HSV + RGB구하는 코드
if skin_pixels.shape[0] == 0:
    print("❗️마스크에 해당하는 픽셀이 없습니다.")
else:
    # RGB 평균
    mean_rgb = np.mean(skin_pixels, axis=0)
    print(f"📊 평균 RGB 값: R={mean_rgb[0]:.1f}, G={mean_rgb[1]:.1f}, B={mean_rgb[2]:.1f}")

    # RGB → HSV 수식 변환용: 0~1로 정규화
    rgb = skin_pixels.astype(np.float32) / 255.0
    r, g, b = rgb[:, 0], rgb[:, 1], rgb[:, 2]

    cmax = np.max(rgb, axis=1)  # V
    cmin = np.min(rgb, axis=1)
    delta = cmax - cmin

    # H 계산
    h = np.zeros_like(cmax)

    # 조건별로 H 계산
    mask = delta != 0
    r_eq = (cmax == r) & mask
    g_eq = (cmax == g) & mask
    b_eq = (cmax == b) & mask

    h[r_eq] = (60 * ((g[r_eq] - b[r_eq]) / delta[r_eq])) % 360
    h[g_eq] = (60 * ((b[g_eq] - r[g_eq]) / delta[g_eq]) + 120) % 360
    h[b_eq] = (60 * ((r[b_eq] - g[b_eq]) / delta[b_eq]) + 240) % 360

    # S 계산
    s = np.zeros_like(cmax)
    s[cmax != 0] = delta[cmax != 0] / cmax[cmax != 0]

    # V = cmax
    v = cmax

    # 평균 HSV
    mean_h = np.mean(h)
    mean_s = np.mean(s) * 100
    mean_v = np.mean(v) * 100

    print(f"📊 평균 HSV 값: H={mean_h:.1f}, S={mean_s:.1f}, V={mean_v:.1f}")

    # HSV 값을 시각화
    hsv_color = np.array([[[mean_h/360, mean_s/100, mean_v/100]]], dtype=np.float32)
    rgb_color = cv2.cvtColor(hsv_color, cv2.COLOR_HSV2RGB)

    # 추출된 색상 표시
    plt.figure(figsize=(4, 4))
    plt.imshow(np.ones((100, 100, 3)) * rgb_color[0])
    plt.title(f"평균 피부색\nRGB: ({mean_rgb[0]:.1f}, {mean_rgb[1]:.1f}, {mean_rgb[2]:.1f})\nHSV: ({mean_h:.1f}, {mean_s:.1f}, {mean_v:.1f})")
    plt.axis('off')
    plt.show()