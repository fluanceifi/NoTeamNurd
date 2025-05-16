from rembg import remove, new_session
from PIL import Image
import io
import colorsys




def remove_background(input_path: str) -> bytes:
    with open(input_path, 'rb') as i:
            image_bytes = i.read()
            session = new_session("u2net_human_seg")
            return remove(image_bytes, session=session) #remb처리 후 바이너리 반환

def fill_transparent_background(image_bytes: bytes, color_rgb=(255, 255, 255)) -> Image.Image:
    # rembg로 배경 제거된 이미지에 원하는 배경색을 채운다.
    rgba = Image.open(io.BytesIO(image_bytes)).convert('RGBA')

    # color_rgb는 튜플이므로 불변성을 가지며,
    # 여기에 (255,)를 더해 RGBA 형식의 튜플을 만들어
    # 완전 불투명한 배경색을 지정한다.
    background = Image.new("RGBA", rgba.size, color_rgb + (255,))

    #두 RGBA 이미지를 알파 채널을 고려하여 겹쳐 그리는 함수이다.
    composited = Image.alpha_composite(background, rgba)

    return composited.convert("RGB")



def hsv_to_rgb_int(h: float, s: float, v: float) -> tuple[int, int, int]:
    """
    0~1 범위의 HSV → 0~255 범위의 RGB 정수값 변환
    """
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(r * 255), int(g * 255), int(b * 255)

if __name__ == "__main__":
    input_path = f'static/captured.jpg'
    output_path = f'static/captured_clipping.jpg'

    bg_removed = remove_background(input_path)
    filled = fill_transparent_background(bg_removed, color_rgb=(255, 255, 255)) #일단 흰색 (나중에 변수로 받아서 퍼스널컬러에 맞게 변환)
    filled.save(output_path, 'JPEG')