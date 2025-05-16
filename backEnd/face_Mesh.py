import cv2 as cv
import mediapipe as mp
from PIL import Image
#MediaPipe 초기화
mp_mesh=mp.solutions.face_mesh
mp_drawing=mp.solutions.drawing_utils
mp_styles=mp.solutions.drawing_styles

#정지 이미지 읽기
input_path = f'static/captured_clipping.jpg'
image = cv.imread(input_path)

#RGB 변환  why?-> openCV는 BRG순서로 읽지만 MediaPipe는 RGB순서로 읽는다.
image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

#FaceMesh 객체 생성 why? -> 모델을 한번만 로딩하고 계속 재사용해서 매번 로딩되어 성능이 저하되는 일을 없앤다.
#얼굴1개, 눈과 입의 랜드마크 더 정교하게, 얼굴 검출 신뢰도 0.5이상 일 땐 성공, 0.5이하 일 땐 실패
with mp_mesh.FaceMesh(
    static_image_mode=True, #정지 영상일 땐 꼭 True
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)as mesh:

    res = mesh.process(image)

    if res.multi_face_landmarks:
        h, w, _ = image.shape
        face_landmarks = res.multi_face_landmarks[0]
        #웃음 판단 지표
        # 🎯 입꼬리 위치 추출
        landmarks = face_landmarks.landmark
        left_corner = landmarks[61]
        right_corner = landmarks[291]
        upper_lip = landmarks[13]
        lower_lip = landmarks[14]

        lx, ly = int(left_corner.x * w), int (left_corner.y * h)
        rx, ry = int(right_corner.x * w), int (right_corner.y * h)
        ux, uy = int(upper_lip.x * w), int (upper_lip.y * h)
        dx, dy = int(lower_lip.x * w), int (lower_lip.y * h)

        mouth_height = dy - uy
        avg_corner_y = (ly + ry) / 2 #입꼬리의 중간값
        center_y = (uy + dy) / 2    #입술에서 중간값

        is_smiling = (avg_corner_y < center_y - 3) and (mouth_height > 5)
        result_text = "Smiling" if is_smiling else "Not Smiling "


        mp_drawing.draw_landmarks(
            image=image,
            landmark_list=face_landmarks,
            connections=mp_mesh.FACEMESH_TESSELATION,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp_styles.get_default_face_mesh_tesselation_style()
        )
        mp_drawing.draw_landmarks(
            image=image,
            landmark_list=face_landmarks,
            connections=mp_mesh.FACEMESH_CONTOURS,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp_styles.get_default_face_mesh_contours_style()
        )
        mp_drawing.draw_landmarks(
            image=image,
            landmark_list=face_landmarks,
            connections=mp_mesh.FACEMESH_IRISES,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp_styles.get_default_face_mesh_iris_connections_style()
        )

        # 결과 텍스트 출력
        cv.putText(image, result_text, (30, 50), cv.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)


#MediaPipe에서 처리한 사진은 RGB순이니깐 이미지를 저장할 땐 원래 BGR순으로 바꿔야 얼굴색이 재대로 나온다.
image = cv.cvtColor(image, cv.COLOR_RGB2BGR)

#이미지 저장
output_path = f'static/clipped_FaceMesh.jpg'
cv.imwrite(output_path, image)

#이미지 확인용
cv.imshow('Face Mesh', image)
cv.waitKey(0)
cv.destroyAllWindows()


# 동적영상 일 때
#cap=cv.VideoCapture(0)

#while True:
    #ret, frame = cap.read()
    # if not ret:
    #     print("프레임 획득에 실패하여 루프를 나갑니다.")
    #     break

#     res = mesh.process(cv.cvtColor(frame,cv.COLOR_BGR2RGB))
#
#     if res.multi_face_landmarks:
#         for landmarks in res.multi_face_landmarks:
#             mp_drawing.draw_landmarks(
#                 image=frame,
#                 landmark_list=landmarks,
#                 connections=mp_mesh.FACEMESH_TESSELATION,
#                 landmark_drawing_spec=None,
#                 connection_drawing_spec=mp_styles.get_default_face_mesh_tesselation_style()
#             )
#             mp_drawing.draw_landmarks(
#                 image=frame,
#                 landmark_list=landmarks,
#                 connections=mp_mesh.FACEMESH_CONTOURS,
#                 landmark_drawing_spec=None,
#                 connection_drawing_spec=mp_styles.get_default_face_mesh_contours_style()
#             )
#             mp_drawing.draw_landmarks(
#                 image=frame,
#                 landmark_list=landmarks,
#                 connections=mp_mesh.FACEMESH_IRISES,
#                 landmark_drawing_spec=None,
#                 connection_drawing_spec=mp_styles.get_default_face_mesh_iris_connections_style()
#             )
#
#     cv.imshow('MediaPipe Face Mesh',cv.flip(frame,1))
#     if cv.waitKey(5) == ord('q'):
#         break
#
# cap.release()
# cv.destroyAllWindows()