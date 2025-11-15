from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import cv2
import numpy as np
import os
import math

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "results"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# ==========================================
# 손금(긴 주요 선 여러 개) 검출
# ==========================================
def extract_major_lines(img_path):
    img = cv2.imread(img_path)
    orig = img.copy()

    # 1️⃣ YCbCr 변환 + CLAHE 대비 강화
    ycbcr = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    Y, Cr, Cb = cv2.split(ycbcr)
    clahe = cv2.createCLAHE(clipLimit=3.5, tileGridSize=(8,8))
    y_eq = clahe.apply(Y)

    # 2️⃣ 블러 + Black-hat (어두운 손금 강조)
    blur = cv2.GaussianBlur(y_eq, (7, 7), 0)
    kernel_bh = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    blackhat = cv2.morphologyEx(blur, cv2.MORPH_BLACKHAT, kernel_bh)

    # 3️⃣ Adaptive Threshold (손금 반전)
    thresh = cv2.adaptiveThreshold(
        blackhat, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
        41, 7
    )

    # 4️⃣ Morphological Closing (끊긴 선 연결)
    kernel_close = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel_close, iterations=7)

    # 5️⃣ Canny 엣지 검출
    edges = cv2.Canny(morph, 40, 120)

    # 6️⃣ 확률적 허프 변환 (직선 검출)
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi/180,
        threshold=80,
        minLineLength=150,
        maxLineGap=50
    )

    mask = np.zeros_like(Y)

    # 7️⃣ 검출된 선 모두 그리기 (조건 만족 시)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = math.degrees(math.atan2(y2 - y1, x2 - x1))

            # 세로 + 약간 기울어진 선 (생명선, 두뇌선, 감정선 등)
            if 20 < abs(angle) < 80:
                if y1 > img.shape[0] * 0.3 and y2 > img.shape[0] * 0.3:  # 손목 이상
                    cv2.line(mask, (x1, y1), (x2, y2), 255, 2)

    # 8️⃣ 스무딩 + 컬러 오버레이
    mask = cv2.GaussianBlur(mask, (5, 5), 0)
    color_mask = cv2.applyColorMap(mask, cv2.COLORMAP_HOT)
    overlay = cv2.addWeighted(orig, 0.85, color_mask, 0.8, 0)

    return overlay


# ==========================================
# Flask API
# ==========================================
@app.route("/analyze", methods=["POST"])
def analyze():
    if "image" not in request.files:
        return jsonify({"error": "이미지 파일이 필요합니다."}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "파일명이 비어 있습니다."}), 400

    img_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(img_path)

    result_img = extract_major_lines(img_path)
    result_path = os.path.join(RESULT_FOLDER, f"result_{file.filename}")
    cv2.imwrite(result_path, result_img)

    return jsonify({
        "message": "손금 주요 선 검출 완료",
        "result_image": f"/result/{os.path.basename(result_path)}"
    })


@app.route("/result/<filename>")
def get_result(filename):
    path = os.path.join(RESULT_FOLDER, filename)
    if os.path.exists(path):
        return send_file(path, mimetype="image/png")
    return jsonify({"error": "파일을 찾을 수 없습니다."}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
