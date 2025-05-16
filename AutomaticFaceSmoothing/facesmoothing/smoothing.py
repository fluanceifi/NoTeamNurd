import cv2
import os

def smoothing(imagePath: str, d: int = 9, 
              sigmaColor: float = 75, sigmaSpace: float = 75, 
              extension: str = '.png'):
    """Smoothing faces on an image from file path using bilateral filter in BGR domain
    Faces are detected using grey scaled image with classifier from openCV

    Args:
        imagePath (string): Path of an image file.
        d (int): Diameter of each pixel neighborhood that is used during filtering
        sigmaColor (float): Filter sigma in the color space, used in bilateral filter
        sigmaSpace (float): Filter sigma in the coordinate space, used in bilateral filter
        extension (string): A wanted extension for output image
    """
    img = cv2.imread(imagePath)
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_classifier = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    face = face_classifier.detectMultiScale(
        gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
    )
    face_img = []
    for (x, y, w, h) in face:
        face_img.append(img[y:y + h, x:x + w])
    for i, (x, y, w, h) in enumerate(face):
        filtered_img = cv2.bilateralFilter(face_img[i], d, sigmaColor, sigmaSpace)
        img[y:y+h, x:x+w] = filtered_img

    new_path = os.path.splitext(imagePath)[0] + '_smoothing' + extension
    cv2.imwrite(new_path, img)

if __name__ == '__main__':
    imagePath = input('input image file: ')
    smoothing(imagePath)
