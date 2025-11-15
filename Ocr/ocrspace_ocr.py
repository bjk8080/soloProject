import cv2
from PIL import Image
import numpy as np
import requests
import os

def preprocess_image(img_path):
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 3)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    
    scale = 2
    thresh = cv2.resize(thresh, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    
    return thresh

def ocr_space_api_preprocessed(img_path, api_key, language="kor"):

    processed = preprocess_image(img_path)
    processed_path = "temp_processed.png"
    cv2.imwrite(processed_path, processed)

    url = "https://api.ocr.space/parse/image"

    with open(processed_path, "rb") as f:
        resp = requests.post(
            url,
            files={"filename": f},
            data={
                "apikey": api_key,            
                "language": language,
                "OCREngine": 2,              
                "scale": True,                 
                "detectOrientation": True
            },
            timeout=30
        )

    try:
        result = resp.json()
    except:
        print("Json이 아님")
        os.remove(processed_path)
        return ""

    os.remove(processed_path) 

    if result.get("IsErroredOnProcessing"):
        print("OCR 처리 에러:", result.get("ErrorMessage") or result.get("ErrorDetails"))
        return ""

    parsed = result.get("ParsedResults")
    if not parsed:
        print("OCR 결과 없음:", result)
        return ""

    return parsed[0].get("ParsedText", "").strip()


if __name__ == "__main__":
    img_path = "input/testpicture.jpeg"  
    api_key = "본인의 api 키"      

    text = ocr_space_api_preprocessed(img_path, api_key)
    print("OCR.Space 결과:\n", text)

    with open("output/ocrspace.txt", "w", encoding="utf-8") as f:
        f.write(text)