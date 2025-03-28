import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import cv2
import torch
import facer
from tkinter import filedialog

# 파일 업로드
image_path = filedialog.askopenfilename(title="Select an image")
if not image_path:
    raise ValueError("No file selected!")

device = 'cuda' if torch.cuda.is_available() else 'cpu'

# 파일 경로
image = facer.hwc2bchw(facer.read_hwc(image_path)).to(device=device)

face_detector = facer.face_detector('retinaface/mobilenet', device=device)
with torch.inference_mode():
    faces = face_detector(image)

face_parser = facer.face_parser('farl/lapa/448', device=device) # optional "farl/celebm/448"

with torch.inference_mode():
    faces = face_parser(image, faces)

seg_logits = faces['seg']['logits']
seg_probs = seg_logits.softmax(dim=1)  # nfaces x nclasses x h x w
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

skin_mask_tensor = (parsed_classes == 1)
skin_mask = skin_mask_tensor.squeeze().cpu().numpy().astype(bool)

print(skin_mask_tensor.shape)
print(skin_mask.shape)

image_tensor = facer.bchw2hwc(image.cpu())
print(image_tensor.shape)
image_np = image_tensor[0].numpy()
print(image_np.shape)

image_tensor = facer.bchw2hwc(image.cpu())
print(image_tensor.shape)

print(image.shape)

image_tensor = facer.bchw2hwc(image.cpu())   # ← 오타 없음!
print(image_tensor.shape)                    # → torch.Size([1, 506, 524, 3]) ← OK
image_np = image_tensor[0].numpy()
print(image_np.shape)

# 원본 텐서: [1, 3, H, W]
image = image.cpu()  # GPU → CPU 이동
image_np = image[0].permute(1, 2, 0).numpy()  # → [H, W, 3]
image_np = (image_np * 255).astype(np.uint8)  # → uint8로 변환
print("image_np shape:", image_np.shape)


# 1. 피부 부위 마스크 생성 (클래스 번호 1 = face_skin)
skin_mask_tensor = (parsed_classes == 1)
skin_mask = skin_mask_tensor.squeeze().cpu().numpy().astype(bool)  # shape: (H, W)

# mask_3ch: (H, W, 1) → (H, W, 3)
mask_3ch = np.repeat(skin_mask[:, :, np.newaxis], 3, axis=2)  # Boolean mask

# 마스크 적용: 피부 부분은 원본, 나머지는 검정
masked_image = np.where(mask_3ch, image_np, 0)


#n_classes = seg_probs.size(1)
#vis_seg_probs = seg_probs.argmax(dim=1).float()/n_classes*255
#vis_img = vis_seg_probs.sum(0, keepdim=True)
#facer.show_bhw(vis_img)
#facer.show_bchw(facer.draw_bchw(image, faces))

#seg_probs = seg_probs.cpu()
#tensor = seg_probs.permute(0, 2, 3, 1)
#tensor = tensor.squeeze().numpy()
#face_skin = tensor[:, :, 1]
#plt.imshow(face_skin)

#third_channel = tensor[:, :, 6]
#plt.imshow(third_channel)


#nose_class = 6

# 코 영역 마스크 생성
#nose_mask = seg_probs.argmax(dim=1) == nose_class

# 코만 추출하기
#nose_image = image * nose_mask.unsqueeze(1).float()

# 결과 시각화
#plt.figure(figsize=(6, 6))
#facer.show_bchw(nose_image)
#plt.title('Nose Area')
#plt.show()