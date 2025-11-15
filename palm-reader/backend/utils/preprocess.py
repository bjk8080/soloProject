import cv2
import numpy as np

def _illumination_correction(gray):
    # 조명 보정: 가우시안 블러를 배경으로 보고 제거
    background = cv2.GaussianBlur(gray, (41, 41), 0)
    norm = cv2.divide(gray, background, scale=255)
    return norm

def preprocess_image(image_path: str):
    """
    1) 컬러 → YCbCr/HSV 혼합 보정
    2) 노이즈 제거 + 대비 향상
    3) 적응형 이진화(Adaptive Threshold)로 손금 대비 극대화
    4) Morphology로 얇은 선 보존
    """
    bgr = cv2.imread(image_path)
    if bgr is None:
        raise ValueError("이미지 로드 실패")

    # 고해상도 권장(최소 한 변 900~1200px). 낮으면 업샘플 약간
    h, w = bgr.shape[:2]
    if max(h, w) < 900:
        scale = 900 / max(h, w)
        bgr = cv2.resize(bgr, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_CUBIC)

    # Y 채널(휘도) 기준으로 대비 향상
    ycrcb = cv2.cvtColor(bgr, cv2.COLOR_BGR2YCrCb)
    y, cr, cb = cv2.split(ycrcb)
    y = cv2.equalizeHist(y)
    y = _illumination_correction(y)
    ycrcb = cv2.merge([y, cr, cb])
    bgr = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)

    # HSV로 피부톤 구간 약하게 마스킹(손금 대비 ↑)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    # 피부 대략 범위 (넓게 잡음)
    lower = np.array([0, 10, 40])
    upper = np.array([35, 200, 255])
    skin = cv2.inRange(hsv, lower, upper)
    skin = cv2.GaussianBlur(skin, (7, 7), 0)

    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # 적응형 이진화로 미세 선 강조
    bin_img = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        25, 7
    )

    # 피부 마스크와 AND → 배경 잡선 억제
    bin_img = cv2.bitwise_and(bin_img, skin)

    # Morphology: 가는 선 살리고 끊김 메우기
    kernel = np.ones((3, 3), np.uint8)
    thin = cv2.morphologyEx(bin_img, cv2.MORPH_OPEN, kernel, iterations=1)
    close = cv2.morphologyEx(thin, cv2.MORPH_CLOSE, kernel, iterations=1)

    return close
