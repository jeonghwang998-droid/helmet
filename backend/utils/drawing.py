"""
OpenCV 프레임에 한글 텍스트를 출력하는 유틸.
cv2.putText는 한글을 □□□로 표시하므로 PIL을 경유한다.
"""
import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image

_FONT_PATH = "C:/Windows/Fonts/malgun.ttf"
_font_cache: dict[int, ImageFont.FreeTypeFont] = {}


def _font(size: int) -> ImageFont.FreeTypeFont:
    if size not in _font_cache:
        _font_cache[size] = ImageFont.truetype(_FONT_PATH, size)
    return _font_cache[size]


def put_text_kr(
    frame: np.ndarray,
    text: str,
    pos: tuple[int, int],
    size: int = 28,
    color: tuple[int, int, int] = (255, 255, 255),
) -> np.ndarray:
    """
    한글/영문 텍스트를 frame에 그려 반환한다.

    Args:
        frame : BGR numpy 배열
        text  : 출력할 문자열
        pos   : (x, y) 좌상단 좌표
        size  : 폰트 크기 (px)
        color : BGR 색상 튜플
    """
    img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    rgb_color = (color[2], color[1], color[0])  # BGR → RGB
    draw.text(pos, text, font=_font(size), fill=rgb_color)
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
