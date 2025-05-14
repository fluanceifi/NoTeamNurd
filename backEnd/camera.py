import cv2
import time


class Camera:
    def __init__(self):
        self.camera = cv2.VideoCapture(0)  # 카메라 연결

    def get_frames(self):  # 클래스 메서드 제거
        while True:
            success, frame = self.camera.read()  # self.camera 사용
            cv2.waitKey(11)  # 11ms 대기

            if not success:
                yield b'fail :('  # 바이트 타입으로 반환
                continue
            else:
                ret, buffer = cv2.imencode('.jpg', frame)  # 프레임을 JPEG로 변환
                frame = buffer.tobytes()

                # 프레임을 HTTP 응답으로 변환
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def capture(self):
        success, frame = self.camera.read()
        if success:
            filename = f'static/captured.jpg'
            cv2.imwrite(filename, frame)
            return filename
        return None


# 전역 카메라 인스턴스 생성
camera = Camera()
