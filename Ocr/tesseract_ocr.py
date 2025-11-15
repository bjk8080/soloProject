import cv2
from PIL import Image
import pytesseract
import numpy as np

def preprocess_image(img_path):
    # 이미지 읽기 (OpenCV는 BGR)
    img = cv2.imread(img_path)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 3)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    scale = 1.5
    thresh = cv2.resize(thresh, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)

    return thresh

def ocr_with_tesseract(img_path):
    processed = preprocess_image(img_path)
    pil_img = Image.fromarray(processed)
    text = pytesseract.image_to_string(pil_img, lang='kor', config='--psm 6')

    return text

if __name__ == "__main__":
    result = ocr_with_tesseract("input/testpicture.jpeg")
    print(result)

    with open("output/tesseract.txt", "w", encoding="utf-8") as f:
        f.write(result)