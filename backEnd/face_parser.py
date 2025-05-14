import torch
import facer
import numpy as np
import matplotlib.pyplot as plt

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
        'r': float(round(mean_rgb[0], 1)),
        'g': float(round(mean_rgb[1], 1)),
        'b': float(round(mean_rgb[2], 1)),
        'h': float(round(mean_h, 1)),
        's': float(round(mean_s, 1)),
        'v': float(round(mean_v, 1))
    }
