# -*- coding: utf-8 -*-
"""face_parsing.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/12451YRgNKa6AgIfxn0yz3htbkdsynKzB
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import cv2

pip install git+https://github.com/FacePerceiver/facer.git@main

from google.colab import files

# 파일 업로드
uploaded = files.upload()

import torch
import facer
import numpy as np
import matplotlib.pyplot as plt

# 1. 이미지 로드 및 face parsing
device = 'cuda' if torch.cuda.is_available() else 'cpu'
image = facer.hwc2bchw(facer.read_hwc('/content/woojin.png')).to(device)

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
image_np = image[0].permute(1, 2, 0).cpu().numpy()  # shape: (506, 524, 3)

plt.imshow(image_np)

import numpy as np
import cv2

# 1. 피부 부위 마스크 생성 (클래스 번호 1 = face_skin) - True / False 로 구분된 이미지 - 피부부위 마스크를 만들기 위해서
skin_mask_tensor = (parsed_classes == 1)
skin_mask = skin_mask_tensor.squeeze().cpu().numpy().astype(bool)  # shape: (H, W)
plt.imshow(skin_mask)

skin_pixels = image_np[skin_mask]


# 마스크에서 피부라고 인식한 이미지에 해당하는 픽셀의 값의 평균을 구한다.
if skin_pixels.shape[0] == 0:
    print("❗️마스크에 해당하는 픽셀이 없습니다.")
else:
    mean_rgb = np.mean(skin_pixels, axis=0)
    print(f"📊 평균 RGB 값: R={mean_rgb[0]:.1f}, G={mean_rgb[1]:.1f}, B={mean_rgb[2]:.1f}")


# HSV + RGB구하는 코드

skin_pixels = image_np[skin_mask]  # shape: (N, 3)

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