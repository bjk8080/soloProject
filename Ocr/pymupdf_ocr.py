import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import io
import cv2
import numpy as np

# ✅ 이미지 전처리 함수
def preprocess_image_pil(pil_img):
    img = np.array(pil_img)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 3)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    scale = 1.5
    thresh = cv2.resize(thresh, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)

    return thresh

def extract_text_from_pdf(pdf_path):
   doc = fitz.open(pdf_path)
   full_text = ""

   for page_num in range(len(doc)):
       page = doc.load_page(page_num)
       text = page.get_text()
       full_text += text

       # 이미지 추출
       image_list = page.get_images()
       for img_index, img in enumerate(image_list):
           xref = img[0]
           base_image = doc.extract_image(xref)
           image_bytes = base_image["image"]
           img_pil = Image.open(io.BytesIO(image_bytes))

           processed = preprocess_image_pil(img_pil)
           pil_processed = Image.fromarray(processed)
           img_text = pytesseract.image_to_string(pil_processed, lang='kor')
           full_text += "\n[이미지 내 텍스트]\n" + img_text + "\n"

   return full_text

text = extract_text_from_pdf("input/Presentation.pdf")
print(text)

with open("output/pymupdf_tesseract.txt", "w", encoding="utf-8") as f:
    f.write(text)
