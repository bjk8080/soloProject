import os
import re
import cv2
import json
import logging
import requests
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

# =====================[ SETTINGS ]=====================
OCR_API_KEY = os.getenv("OCR_SPACE_KEY", "K82626647288957")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
PROCESSED_FOLDER = os.path.join(BASE_DIR, "processed")
RECORD_FILE = os.path.join(BASE_DIR, "records.json")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["JSON_AS_ASCII"] = False

CORS(app, resources={r"/*": {"origins": "*"}})

# Logging
log_path = os.path.join(BASE_DIR, "app.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(log_path), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


# =====================[ IMAGE PREPROCESS ]=====================
def preprocess_image(src, dst):
    img = cv2.imread(src)

    # ---- 1. 그레이스케일 ----
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # ---- 2. 노이즈 제거 ----
    gray = cv2.bilateralFilter(gray, 5, 150, 150)

    # ---- 3. 대비 증가(명암 강조) ----
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(5, 5))
    gray = clahe.apply(gray)

    # ---- 4. 선명도 강화 ----
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    sharp = cv2.filter2D(gray, -1, kernel)

    # ---- 5. adaptive threshold ----
    th1 = cv2.adaptiveThreshold(
        sharp, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        25, 10
    )

    # ---- 6. 확대 업샘플링 ----
    th1 = cv2.resize(th1, None, fx=3, fy=3, interpolation=cv2.INTER_LINEAR)

    # ---- 첫 번째 버전 저장 ----
    cv2.imwrite(dst, th1)


# =====================[ OCR SPACE API ]=====================
def ocr_space(img_path, lang="kor"):
    url = "https://api.ocr.space/parse/image"

    try:
        with open(img_path, "rb") as f:
            resp = requests.post(
                url,
                files={"filename": f},
                data={"apikey": OCR_API_KEY, "language": lang, "OCREngine": 2},
                timeout=20
            )

        result = resp.json()
        parsed = result.get("ParsedResults", [])
        return parsed[0].get("ParsedText", "") if parsed else ""

    except Exception as e:
        logging.error(f"OCR API 오류: {str(e)}")
        return ""


# =====================[ NUTRITION PARSER ]=====================
NUTRIENT_PATTERNS = {
    "칼로리(kcal)": ["칼로리", "열량", "kcal", "kc"],
    "나트륨(mg)": ["나트륨", "sodium", "소듐", "나트"],
    "탄수화물(g)": ["탄수", "탄수화물", "carb"],
    "당류(g)": ["당류", "당", "sugar"],
    "지방(g)": ["지방", "fat"],
    "트랜스지방(g)": ["트랜스", "trans"],
    "포화지방(g)": ["포화", "saturated"],
    "콜레스테롤(mg)": ["콜레스", "cholesterol"],
    "단백질(g)": ["단백질", "protein", "prot"]
}

VAL_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(mg|g|kcal|%)", re.IGNORECASE)


def normalize_text(s):
    return (
        s.replace(" ", "")
        .replace("％", "%")
        .replace("㎎", "mg")
        .replace("그램", "g")
        .replace("kca", "kcal")
        .replace("kc", "kcal")
        .strip()
        .lower()
    )


def parse_nutrition(text):
    lines = [normalize_text(l) for l in text.splitlines() if l.strip()]
    data = {k: None for k in NUTRIENT_PATTERNS.keys()}

    for idx, line in enumerate(lines):
        for nutrient, keys in NUTRIENT_PATTERNS.items():
            if any(k in line for k in keys):

                targets = [line]
                if idx + 1 < len(lines):
                    targets.append(lines[idx + 1])

                for t in targets:
                    matches = VAL_RE.findall(t)
                    for v, u in matches:
                        if u.lower() in ["g", "mg", "kcal"]:
                            data[nutrient] = float(v)
                            break
    return data


# =====================[ SCORE + TIER ]=====================
def calculate_score(parsed):
    protein = parsed.get("단백질(g)", 0)
    sugar = parsed.get("당류(g)", 0)
    fat = parsed.get("지방(g)", 0)
    sat_fat = parsed.get("포화지방(g)", 0)
    calories = parsed.get("칼로리(kcal)", 0)
    sodium = parsed.get("나트륨(mg)", 0)
    cholesterol = parsed.get("콜레스테롤(mg)", 0)
    trans = parsed.get("트랜스지방(g)", 0)

    protein_score = min(protein, 20)
    sugar_score = max(20 - sugar, 0)
    fat_score = max(10 - fat * 0.5, 0)
    sat_fat_score = max(10 - sat_fat, 0)
    calorie_score = max(10 - ((calories - 100) / 40), 0) if calories > 100 else 10
    sodium_score = max(10 - (sodium / 200), 0)
    cholesterol_score = max(5 - (cholesterol / 60), 0)
    trans_score = 5 if trans == 0 else 0

    total = (
        protein_score + sugar_score + fat_score + sat_fat_score +
        calorie_score + sodium_score + cholesterol_score + trans_score
    )

    return int(total)


def get_tier(score):
    if score >= 85:
        return "A"
    elif score >= 65:
        return "B"
    else:
        return "C"


# =====================[ 기록 저장 ]=====================
def save_record(record):
    try:
        if not os.path.exists(RECORD_FILE):
            with open(RECORD_FILE, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4, ensure_ascii=False)

        with open(RECORD_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        data.append(record)

        with open(RECORD_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Record Save Error: {e}")


# =====================[ ROUTES ]=====================
@app.route("/health")
def health():
    return jsonify({"ok": True})


@app.route("/api/upload", methods=["POST"])
def upload():
    f = request.files.get("file")
    if not f:
        return jsonify({"ok": False, "error": "No file"}), 400

    filename = secure_filename(f.filename)
    f.save(os.path.join(UPLOAD_FOLDER, filename))

    return jsonify({"ok": True, "filename": filename})


@app.route("/api/analyze")
def analyze():
    filename = request.args.get("filename")
    src = os.path.join(UPLOAD_FOLDER, filename)
    processed = os.path.join(PROCESSED_FOLDER, filename + "_p.png")

    preprocess_image(src, processed)

    text = ocr_space(processed)
    parsed = parse_nutrition(text)

    # 하나라도 None이면 실패 처리
    if any(v is None for v in parsed.values()):
        return jsonify({
            "ok": False,
            "error": "영양성분 인식이 불완전합니다. 이미지를 다시 업로드해주세요.",
            "parsed": parsed
        }), 400

    score = calculate_score(parsed)
    tier = get_tier(score)

    # 기록 저장
    record = {
        "filename": filename,
        "parsed": parsed,
        "score": score,
        "tier": tier,
        "text": text,
        "timestamp": datetime.now().isoformat()
    }
    save_record(record)

    return jsonify({
        "ok": True,
        "filename": filename,
        "parsed": parsed,
        "text": text,
        "score": score,
        "tier": tier
    })


@app.route("/api/processed")
def get_processed():
    filename = request.args.get("filename")
    path = os.path.join(PROCESSED_FOLDER, filename + "_p.png")
    return send_file(path)


# =====================[ RUN ]=====================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
