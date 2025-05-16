# backEnd/facesmoothing_integration.py

import os
import sys

# AutomaticFaceSmoothing 모듈 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'AutomaticFaceSmoothing')))

from facesmoothing import smoothing

def apply_face_smoothing(input_path: str, d=9, sigma_color=75, sigma_space=75, extension=".jpg") -> str:
    """
    얼굴 피부 부드럽게 처리하고, 새 파일로 저장
    :param input_path: 원본 이미지 경로d
    :return: 보정된 이미지 경로
    """
    output_path = "static/clipped_smoothing.jpg"

    from shutil import copyfile
    copyfile(input_path, output_path)

    smoothing.smoothing(output_path, d, sigma_color, sigma_space, extension)

    return output_path


#  단독 실행 시 테스트 코드
if __name__ == "__main__":
    print(" [TEST] 얼굴 보정 모듈 테스트 중...")

    # 정적 테스트 이미지 경로 (절대경로 아님)
    test_image = "static/captured_clipping.jpg"  # 상대경로나 직접입력한 정적 경로

    if not os.path.exists(test_image):
        print(f" 테스트 이미지가 없습니다: {test_image}")
    else:
        result_path = apply_face_smoothing(test_image)
        print(f" 얼굴 보정 완료: {result_path}")
