import cv2
import numpy as np
from skimage.morphology import skeletonize
from skimage.measure import label, regionprops

def _to_skeleton(binary_img):
    # 0/1 이진화 후 skeletonize
    bin01 = (binary_img > 0).astype(np.uint8)
    skel = skeletonize(bin01).astype(np.uint8) * 255
    return skel

def _largest_hand_region(mask):
    # 가장 큰 연결성분(손 영역)만 남기기 (노이즈 억제)
    lbl = label(mask > 0)
    if lbl.max() == 0:
        return mask
    props = regionprops(lbl)
    largest = max(props, key=lambda p: p.area)
    keep = (lbl == largest.label).astype(np.uint8) * 255
    return keep

def _polyline_from_component(component_mask, step=3):
    """
    컴포넌트의 픽셀 좌표를 간단히 다운샘플하여 폴리라인 문자열로 변환
    예: "x1,y1 x2,y2 ..."
    """
    ys, xs = np.where(component_mask > 0)
    if len(xs) < 2:
        return ""
    pts = np.stack([xs, ys], axis=1)
    # 좌표 수가 많으면 간격 샘플링
    pts = pts[::step]
    return " ".join([f"{int(x)},{int(y)}" for x, y in pts])

def extract_palm_lines(preprocessed_img):
    """
    1) 스켈레톤화
    2) 가장 큰 손 영역 근처만 유지
    3) 연결성분 별로 폴리라인 후보 생성
    4) 상위 몇 개(길이 기준)를 라인으로 채택
    """
    # 스켈레톤
    skel = _to_skeleton(preprocessed_img)

    # 손 영역 근사 (스켈레톤 dilate → 손 영역 근처)
    kernel = np.ones((5,5), np.uint8)
    hand_region = cv2.dilate(skel, kernel, iterations=2)
    hand_region = _largest_hand_region(hand_region)

    # 스켈레톤과 hand_region 교차
    skel = cv2.bitwise_and(skel, hand_region)

    # 연결성분 분석
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(skel, connectivity=8)
    comps = []
    for lab in range(1, num_labels):
        area = stats[lab, cv2.CC_STAT_AREA]
        if area < 80:  # 너무 짧은 선 제거
            continue
        comp_mask = (labels == lab).astype(np.uint8) * 255
        length = area  # 스켈레톤이라 픽셀 수 ~ 길이 근사
        poly = _polyline_from_component(comp_mask, step=4)
        if poly:
            comps.append((length, poly, comp_mask))

    # 길이 순으로 정렬 후 상위 3~4개를 주요 손금으로 가정
    comps.sort(key=lambda x: x[0], reverse=True)
    top = comps[:4]

    # 단순 매핑(길이 기준으로 임시 라벨링)
    line_names = ["life", "head", "heart", "fate"]
    lines = {}
    for i, item in enumerate(top):
        _, poly, _ = item
        lines[line_names[i]] = poly

    # 시각화용 컨투어(흰 바탕에 선)
    vis = np.zeros_like(preprocessed_img)
    for _, _, mask in top:
        vis = cv2.bitwise_or(vis, mask)

    return vis, lines
