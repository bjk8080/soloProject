import os
import cv2
import numpy as np
import pytesseract
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image, ImageDraw, ImageFont
import re
import math

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
RESULT_FOLDER = os.path.join(BASE_DIR, "results")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)


def analyze_moon(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("이미지를 불러오지 못했습니다.")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # ✅ 달 세그멘테이션 (이진화)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise ValueError("달 윤곽을 찾지 못했습니다.")
    moon_contour = max(contours, key=cv2.contourArea)

    # ✅ 밝기 (참고용)
    mask = np.zeros_like(gray)
    cv2.drawContours(mask, [moon_contour], -1, 255, -1)
    moon_brightness = cv2.mean(gray, mask=mask)[0]
    bright_ratio = round((moon_brightness / 255) * 100, 2)

    # ✅ 좌우 비율 계산
    x, y, w, h = cv2.boundingRect(moon_contour)
    moon_crop = mask[y:y+h, x:x+w]
    total_area = np.count_nonzero(moon_crop)
    left_area = np.count_nonzero(moon_crop[:, :w//2])
    right_area = np.count_nonzero(moon_crop[:, w//2:])
    left_ratio = left_area / total_area
    right_ratio = right_area / total_area

    # ✅ 방향 판별
    if right_ratio > left_ratio:
        direction = "오른쪽이 밝음 → 초승/상현"
        side = "right"
    else:
        direction = "왼쪽이 밝음 → 하현/그믐"
        side = "left"

    # ✅ 형태 분석 (채워진 비율)
    (cx, cy), radius = cv2.minEnclosingCircle(moon_contour)
    circle_area = math.pi * (radius ** 2)
    moon_area = cv2.contourArea(moon_contour)
    fill_ratio = round(moon_area / circle_area, 2)

    # ✅ 둥근 정도
    x, y, w_box, h_box = cv2.boundingRect(moon_contour)
    aspect_ratio = w_box / h_box if h_box != 0 else 1
    roundness = 1 - abs(1 - aspect_ratio)
    roundness = max(0, min(roundness, 1))

    # ✅ 최적 조합 공식
    shape_ratio = round(fill_ratio * 0.7 + roundness * 0.3, 2)

    # ✅ 위상 분류
    if shape_ratio < 0.1:
        phase = "암달"
    elif shape_ratio < 0.3:
        phase = "초승달" if side == "right" else "그믐달"
    elif shape_ratio < 0.7:
        phase = "상현달" if side == "right" else "하현달"
    elif shape_ratio < 0.95:
        phase = "상현과 보름 사이" if side == "right" else "보름과 하현 사이"
    else:
        phase = "보름달"

    # ✅ 이미지에 텍스트 표시
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    font_size = max(24, int(img.shape[1] * 0.045))
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/nanum/NanumGothic.ttf", font_size)
    except:
        font = ImageFont.load_default()
    draw.text((25, 25), f"{phase} ({shape_ratio * 100:.1f}%)", font=font, fill=(255, 255, 255))

    # ✅ 결과 이미지 저장
    result_filename = f"result_{os.path.basename(image_path)}"
    result_path = os.path.join(RESULT_FOLDER, result_filename)
    pil_img.save(result_path)

    # ✅ OCR
    try:
        ocr_raw = pytesseract.image_to_string(pil_img, lang="kor+eng")
        ocr_text = re.sub(r"[^가-힣\s]", "", ocr_raw).strip()
    except:
        ocr_text = ""

    return bright_ratio, shape_ratio, direction, phase, ocr_text, result_filename


@app.route("/analyze", methods=["POST"])
def analyze():
    if "file" not in request.files:
        return jsonify({"error": "파일이 없습니다."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "파일 이름이 비어있습니다."}), 400

    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(save_path)

    try:
        bright_ratio, shape_ratio, direction, phase, ocr_text, result_filename = analyze_moon(save_path)
        return jsonify({
            "bright_ratio": bright_ratio,
            "shape_ratio": shape_ratio,
            "direction": direction,
            "phase": phase,
            "ocr_text": ocr_text,
            "result_image": f"results/{result_filename}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/results/<path:filename>")
def serve_result_image(filename):
    return send_from_directory(RESULT_FOLDER, filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
