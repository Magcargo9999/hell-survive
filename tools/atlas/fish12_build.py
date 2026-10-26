"""마계 물고기 진화 도트 (v9.49): 1진화 마계 미꾸라지(fish1.png) · 최종 공허의 마해룡(fish2.png) → fish1.webp/json · fish2.webp/json
실행: python3 tools/atlas/fish12_build.py <미꾸라지 시트> <마해룡 시트> <출력 폴더>
자르기 · 배경 제거 · 마스크만 (재색칠 · 배율 없음). 두 시트 모두 몸은 오른쪽을 본다.
- 몸 줄: fish_build.py 와 같은 frames() (테두리와 이어진 배경만 지움 · 칸막이 선 제거 · 떨어진 조각(번호 글자) 버림)
- 절대 수압 원 · 포식자의 파도: 이펙트라 배경과의 차이로 부드러운 알파. 수압 원 가운데의 용(본체 그림과 겹침)은 원형 마스크로 가린다"""
import os, sys, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
D = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(D, 'an_build.py'), encoding='utf8').read().split('\ninfo = {}')[0])   # load · mode_bg · unblend · body_alpha · keep_main · fx_alpha
src = open(os.path.join(D, 'fish_build.py'), encoding='utf8').read()
exec(src[src.index('def longest'):src.index("A = load(")])   # longest · lines · refine · frames · piece (info 전역)
exec(src[src.index('def pack'):src.index("pack(list(info)")])

def blank(S, box):
    x0, y0, x1, y1 = box; S[y0:y1, x0:x1] = mode_bg(S[y1:y1 + 30, x0:x1])
f1, f2, out = sys.argv[1:4]
os.makedirs(out, exist_ok=True)

# ---- 1진화 마계 미꾸라지 (fish0 시트와 같은 판) ----
A = load(f1)
blank(A, (536, 205, 745, 252)); blank(A, (536, 375, 880, 418)); blank(A, (484, 556, 712, 601)); blank(A, (395, 755, 600, 800)); blank(A, (855, 755, 1055, 800))
frames('i1', A, 250, 356, [540, 688, 842, 980, 1120, 1270, 1432], win=10, gap=20)
frames('w1', A, 418, 540, [550, 742, 852, 985, 1092, 1222, 1340, 1432], win=10, gap=22)
frames('a1', A, 598, 742, [485, 645, 800, 952, 1108, 1268, 1432], win=8, gap=26)
frames('h1', A, 800, 912, [400, 507, 622, 726, 832], win=6, gap=20)
frames('d1', A, 800, 914, [855, 960, 1057, 1156, 1254, 1346, 1432], win=6, gap=30)
pack(['i1', 'w1', 'a1', 'h1', 'd1'], os.path.join(out, 'fish1'))
info.clear()

# ---- 최종 공허의 마해룡 ----
# 이 시트는 몸이 띠 높이를 거의 다 채워서, 세로 칸막이 판정이 몸통 세로줄을 지워 버린다 → 가로 줄만 지운다
def lines(band, BG):
    m = np.abs(band - BG).max(-1) > 18; L = np.zeros(m.shape, bool)
    for y in np.where(longest(m) > 380)[0]: L[max(0, y - 1):y + 2] = True
    return L
B = load(f2)
blank(B, (12, 495, 285, 520)); blank(B, (618, 495, 765, 520)); blank(B, (12, 622, 380, 653)); blank(B, (540, 622, 700, 653)); blank(B, (905, 622, 1060, 653))   # 칸 제목 상자
frames('i2', B, 517, 597, [18, 108, 205, 305, 405, 505, 605], win=8, gap=14)
frames('w2', B, 517, 597, [625, 721, 811, 909, 1003, 1098, 1196, 1312, 1425], win=6, gap=14)
frames('a2', B, 652, 734, [18, 101, 182, 265, 351, 436, 525], win=6, gap=14)
frames('h2', B, 652, 734, [543, 633, 722, 808, 893], win=6, gap=16)
frames('d2', B, 652, 736, [912, 1004, 1084, 1166, 1252, 1346, 1425], win=6, gap=40)

def fxp(name, S, box, lo=14, hi=70, hole=0, cx=None, cy=None, cut=()):   # 이펙트 한 장 (hole: 가운데 원형 마스크 반지름)
    x0, y0, x1, y1 = box; c = S[y0:y1, x0:x1].copy(); BG = np.array([7, 9, 24.0])
    a = fx_alpha(c, BG, lo, hi)
    for u0, v0, u1, v1 in cut: a[max(0, v0 - y0):max(0, v1 - y0), max(0, u0 - x0):max(0, u1 - x0)] = 0   # 설명 글자 · 제목 상자 · 칸막이 (원본 좌표)
    a = keep_main(a, 40)
    lab, n = ndi.label(a > 0.04, structure=np.ones((3, 3)))   # 칸막이 · 밑줄 같은 가늘고 긴 선 조각은 버린다
    for i, sl in enumerate(ndi.find_objects(lab), 1):
        hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if (hh <= 5 and ww >= 25) or (ww <= 5 and hh >= 25): a[sl][lab[sl] == i] = 0
    if hole:
        yy, xx = np.mgrid[0:c.shape[0], 0:c.shape[1]]; a[(xx - cx) ** 2 + (yy - cy) ** 2 < hole ** 2] = 0
    rgba = unblend(c, a, BG); ys, xs = np.where(rgba[..., 3] > 6)
    cr = rgba[ys.min():ys.max() + 1, xs.min():xs.max() + 1]; h, w = cr.shape[:2]
    info.setdefault(name, []).append((cr, (cx - xs.min()) if cx is not None else w / 2, (cy - ys.min()) if cy is not None else h / 2))
# 절대 수압: 원 중심 (365, 917) 근처 — 왼쪽 설명 글자는 원 밖이라 상자에서 뺀다
fxp('press', B, (192, 758, 545, 1078), lo=18, hi=80, hole=62, cx=178, cy=157, cut=[(0, 740, 245, 800), (541, 740, 560, 1090), (192, 758, 300, 776), (192, 1071, 560, 1090)])
# 포식자의 파도 (큰 그림, 용 + 창끝 파도)
fxp('wave', B, (968, 838, 1428, 975), lo=16, hi=75, cut=[(960, 830, 1200, 864)])
pack(['i2', 'w2', 'a2', 'h2', 'd2', 'press', 'wave'], os.path.join(out, 'fish2'), W=1400)
