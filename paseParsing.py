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
n_classes = seg_probs.size(1)
vis_seg_probs = seg_probs.argmax(dim=1).float()/n_classes*255
vis_img = vis_seg_probs.sum(0, keepdim=True)
facer.show_bhw(vis_img)
facer.show_bchw(facer.draw_bchw(image, faces))

seg_probs = seg_probs.cpu()
tensor = seg_probs.permute(0, 2, 3, 1)
tensor = tensor.squeeze().numpy()
face_skin = tensor[:, :, 1]
plt.imshow(face_skin)

third_channel = tensor[:, :, 6]
plt.imshow(third_channel)


nose_class = 6

# 코 영역 마스크 생성
nose_mask = seg_probs.argmax(dim=1) == nose_class

# 코만 추출하기
nose_image = image * nose_mask.unsqueeze(1).float()

# 결과 시각화
plt.figure(figsize=(6, 6))
facer.show_bchw(nose_image)
plt.title('Nose Area')
plt.show()