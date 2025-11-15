import numpy as np
from scipy.ndimage import gaussian_filter1d

def _polyline_to_xy(polyline_str):
    # "x,y x,y ..." -> (N,2) numpy
    if not polyline_str:
        return np.zeros((0,2), dtype=np.float32)
    pts = []
    for tok in polyline_str.strip().split():
        x, y = tok.split(',')
        pts.append((float(x), float(y)))
    return np.array(pts, dtype=np.float32)

def measure_length(polyline_str):
    pts = _polyline_to_xy(polyline_str)
    if len(pts) < 2:
        return 0.0
    diffs = np.diff(pts, axis=0)
    seg_len = np.sqrt((diffs**2).sum(axis=1))
    return float(seg_len.sum())

def measure_curvature(polyline_str, sigma=2.0):
    """
    간이 곡률: x(t), y(t) 1~2차 미분 근사로 평균 절대 곡률 반환
    """
    pts = _polyline_to_xy(polyline_str)
    if len(pts) < 5:
        return 0.0
    x = gaussian_filter1d(pts[:,0], sigma=sigma, mode='nearest')
    y = gaussian_filter1d(pts[:,1], sigma=sigma, mode='nearest')
    dx = np.gradient(x); dy = np.gradient(y)
    ddx = np.gradient(dx); ddy = np.gradient(dy)
    # 곡률 k = |x'y'' - y'x''| / ( (x'^2 + y'^2)^(3/2) )
    num = np.abs(dx*ddy - dy*ddx)
    den = (dx*dx + dy*dy)**1.5 + 1e-8
    k = num / den
    return float(np.mean(np.abs(k)))

def generate_fortune_from_features(features):
    """
    길이/곡률로 간단 감성 문장 생성
    features = {
      'life': {'length':..., 'curvature':...}, ...
    }
    """
    msgs = []
    if 'life' in features:
        if features['life']['length'] > 400: msgs.append("생명선이 길고 선명합니다. 체력과 회복력이 좋네요.")
        else: msgs.append("생명선이 비교적 짧습니다. 휴식과 생활 리듬 관리가 중요해요.")
    if 'heart' in features:
        if features['heart']['curvature'] > 0.01: msgs.append("감정선의 곡률이 커서 감성 표현이 풍부한 편이에요.")
        else: msgs.append("감정선이 완만하여 감정보다 이성을 중시하는 경향이 있어요.")
    if 'head' in features:
        if features['head']['length'] > 350: msgs.append("두뇌선이 길어 집중력이 좋은 타입이에요.")
        else: msgs.append("두뇌선이 짧아 결단이 빠른 편일 수 있어요.")
    if 'fate' in features:
        msgs.append("운명선이 또렷해 목표 지향성이 보입니다.")
    return " ".join(msgs) if msgs else "손금 특징이 은은합니다. 다른 각도/밝기로 다시 시도해보세요."
