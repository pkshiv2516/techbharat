import pytesseract
from PIL import Image
import cv2
import numpy as np
from ..config import settings
import os

TESSERACT_EXE = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXE

# 2) The tessdata directory (this is where *.traineddata lives)
# TESSDATA_DIR = r"C:\Program Files\Tesseract-OCR\tessdata"

# 3) (Optional but recommended) Environment variable:
#    IMPORTANT: TESSDATA_PREFIX should point to the *parent* that contains "tessdata",
#    i.e. "C:\Program Files\Tesseract-OCR\", NOT the tessdata folder itself.
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"

if settings.tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd




def read_ingredients(image_bytes: bytes) -> str:
    arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    pil = Image.fromarray(th)
    txt = pytesseract.image_to_string(
        pil,
        lang="eng",
        config=rf'--psm 6'  # all backslashes; quoted path
    )

    return txt