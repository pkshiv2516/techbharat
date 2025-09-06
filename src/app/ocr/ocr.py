import pytesseract
from PIL import Image
import cv2
import numpy as np
from ..config import settings


if settings.tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd




def read_ingredients(image_bytes: bytes) -> str:
    arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    pil = Image.fromarray(th)
    txt = pytesseract.image_to_string(pil, config='--psm 6')
    return txt