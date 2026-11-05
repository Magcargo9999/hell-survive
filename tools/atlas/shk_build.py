"""거대 버섯마귀(보스) 시트 → 아틀라스. 자르기·배경 제거만 (색 수정 없음).
사용: python3 tools/atlas/shk_build.py <시트.png>  → src/assets/shk/shk.webp + shk.json
각 프레임 [x,y,w,h,ax,ay] : ax = 몸통(가장 큰 덩어리) 가운데, ay = 몸통 아래 끝 (발 위치)"""
import sys, json, os
import numpy as np
from PIL import Image
from scipy import ndimage as nd
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'build/shk/sheet.png')
im = Image.open(src).convert('RGBA'); A = np.array(im)
RGB = A[:, :, :3].astype(int)
# 행(위·아래 y) · 라벨 상자 아래 끝(이 위는 지움) · 칸들(x 범위)
ROWS = {
 'idle':  (14, 130, 36, [(525, 655), (704, 822), (890, 1014), (1085, 1219)]),
 'walk':  (142, 248, 167, [(512, 614), (620, 719), (736, 833), (844, 942), (952, 1049), (1059, 1166), (1168, 1267), (1280, 1378), (1397, 1488)]),
 'atk':   (258, 370, 284, [(505, 645), (665, 795), (798, 928), (930, 1060), (1278, 1408)]),
 'spit':  (258, 370, 284, [(1062, 1272), (1410, 1514)]),
 'hit':   (380, 476, 403, [(600, 720), (742, 873), (882, 1026), (1031, 1161)]),
 'death': (491, 592, 506, [(508, 682), (690, 852), (855, 962), (965, 1095), (1098, 1290), (1292, 1514)]),
 'cast':  (603, 728, 620, [(486, 690)]),
 'spore': (603, 728, 620, [(690, 830), (830, 975), (975, 1157), (1160, 1325), (1327, 1514)]),
 'sum':   (742, 850, 757, [(489, 690), (690, 862)]),
 'erupt': (742, 850, 757, [(862, 1000), (1000, 1152), (1152, 1302), (1302, 1514)]),
 'fx':    (862, 998, 887, [(30, 135), (402, 582), (585, 748), (1078, 1510)]),
}
BOX = {r: v for r, v in {'idle': (484, 12, 628, 43), 'walk': (484, 137, 626, 169), 'atk': (485, 255, 627, 286), 'spit': (485, 255, 627, 286), 'hit': (485, 376, 626, 407), 'death': (484, 484, 628, 516),
       'cast': (485, 599, 706, 630), 'spore': (485, 599, 706, 630), 'sum': (484, 737, 667, 768), 'erupt': (484, 737, 667, 768), 'fx': (18, 856, 188, 887)}.items()}   # 줄 제목 상자 (x0, y0, x1, y1)
LBL_X = {'idle': 640, 'walk': 640, 'atk': 645, 'spit': 645, 'hit': 645, 'death': 640, 'cast': 735, 'spore': 735, 'sum': 700, 'erupt': 700, 'fx': 200}
# v10.28: 빽빽한 줄(포자·소환·분출)은 칸 경계를 ±28px 안에서 그림이 가장 적은 세로줄로 옮긴다 (이펙트가 네모로 잘리지 않게)
FG = RGB.max(axis=2) > 20
def valley(y0, y1, cells):
    xs = [c[0] for c in cells] + [cells[-1][1]]
    for i in range(1, len(xs) - 1):
        if cells[i - 1][1] != cells[i][0]: continue
        lo, hi = xs[i] - 28, xs[i] + 28; col = FG[y0:y1, lo:hi].sum(axis=0); xs[i] = lo + int(np.argmin(col))
    return [(xs[i], xs[i + 1]) for i in range(len(cells))]
for r1, r2 in (('cast', 'spore'), ('sum', 'erupt')):
    y0, y1, lb, _ = ROWS[r1]; allc = ROWS[r1][3] + ROWS[r2][3]; adj = valley(y0, y1, allc)
    n1 = len(ROWS[r1][3]); ROWS[r1] = (y0, y1, lb, adj[:n1]); ROWS[r2] = (y0, y1, lb, adj[n1:])
frames, tiles = {}, []
for k, (y0, y1, lb, cells) in ROWS.items():
    frames[k] = []
    for (x0, x1) in cells:
        rgb = RGB[y0:y1, x0:x1]; m = rgb.max(axis=2) > 20
        bx = BOX.get(k)
        if bx and x0 < bx[2] + 8 and bx[3] + 3 > y0:   # v10.28: 줄 제목 상자 — 상자 사각형 안의 테두리선·어두운 바탕·사각형 안에 갇힌 덩어리(글자)만 지운다 (예전엔 칸 왼쪽 윗부분을 통째로 지워 버섯 머리가 잘렸다)
            rx0, ry0, rx1, ry1 = max(0, bx[0] - 2 - x0), max(0, bx[1] - 2 - y0), min(x1 - x0, bx[2] + 8 - x0), min(y1 - y0, bx[3] + 3 - y0)
            if rx1 > rx0 and ry1 > ry0:
                box = np.zeros_like(m); box[ry0:ry1, rx0:rx1] = True
                sub = rgb.astype(int); crim = (sub[:, :, 0] > 140) & (sub[:, :, 1] < 90) & (sub[:, :, 0] > sub[:, :, 2] * 1.6)
                line = nd.binary_opening(crim & box, structure=np.ones((1, 7))) | nd.binary_opening(crim & box, structure=np.ones((7, 1)))
                dark = box & (sub.max(axis=2) < 48)
                m &= ~(nd.binary_dilation(line, iterations=1) & box) & ~dark
                lab0, n0 = nd.label(m)
                for i0 in range(1, n0 + 1):
                    comp = lab0 == i0
                    if not (comp & ~box).any(): m[comp] = False
                near = np.zeros_like(m); near[max(0, ry0 - 2):min(m.shape[0], ry1 + 8), max(0, rx0 - 2):min(m.shape[1], rx1 + 8)] = True
                lab0, n0 = nd.label(m); szs = nd.sum(m, lab0, range(1, n0 + 1))
                for i0 in range(1, n0 + 1):   # 상자 모서리(둥근 끝) 부스러기
                    if szs[i0 - 1] < 60 and (lab0[near] == i0).any(): m[lab0 == i0] = False
        if k == 'fx': m[:max(0, lb - y0 + 2), :] = m[:max(0, lb - y0 + 2), :] if x0 > 200 else False
        m[:, :2] = m[:, -2:] = False; m[:2, :] = m[-2:, :] = False                       # 패널 테두리
        m[:3, :] = False                                                                  # 패널 윗 테두리
        lab, n = nd.label(m)
        for sl_i, sl in enumerate(nd.find_objects(lab)):                                  # 가늘고 긴 선(테두리 조각) 제거
            h_, w_ = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
            if (h_ <= 4 and w_ >= 14) or (w_ <= 4 and h_ >= 14) or (w_ <= 3 and h_ >= 7 and sl[0].start < 24): m[lab == sl_i + 1] = False   # v10.28 띠 위쪽의 짧은 세로 눈금도
        if k in ('idle', 'walk', 'atk', 'hit', 'death', 'cast'):   # v10.28b: 몸 동작 칸 가장자리에 걸린 옆 칸 조각(작은 덩어리) 제거
            lab, n = nd.label(m); sz0 = nd.sum(m, lab, range(1, n + 1))
            for i0, sl in enumerate(nd.find_objects(lab)):
                if (sz0[i0] < 150 or sl[1].stop - sl[1].start <= 16) and sz0[i0] < 0.2 * sz0.max() and (sl[1].start <= 3 or sl[1].stop >= m.shape[1] - 3): m[lab == i0 + 1] = False
        lab, n = nd.label(m); sz = nd.sum(m, lab, range(1, n + 1))
        keep = np.isin(lab, [i + 1 for i, s in enumerate(sz) if s >= 5]); keep = nd.binary_fill_holes(keep)
        big = (lab == (int(np.argmax(sz)) + 1)) if n else keep
        ys, xs = np.where(keep); by, bx = np.where(big)
        X0, X1, Y0, Y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        t = np.zeros((Y1 - Y0, X1 - X0, 4), np.uint8); t[:, :, :3] = A[y0 + Y0:y0 + Y1, x0 + X0:x0 + X1, :3]
        t[:, :, 3] = keep[Y0:Y1, X0:X1] * 255
        ax = int(round((bx.min() + bx.max()) / 2)) - X0; ay = int(by.max()) + 1 - Y0
        tiles.append((k, len(frames[k]), Image.fromarray(t), ax, ay)); frames[k].append(None)
# 가로로 줄지어 담기
W = 1024; x = y = rowh = 0; place = []
for k, i, t, ax, ay in tiles:
    if x + t.width > W: x = 0; y += rowh + 2; rowh = 0
    place.append((k, i, t, x, y, ax, ay)); x += t.width + 2; rowh = max(rowh, t.height)
out = Image.new('RGBA', (W, y + rowh), (0, 0, 0, 0))
for k, i, t, x, y, ax, ay in place:
    out.paste(t, (x, y)); frames[k][i] = [int(v) for v in (x, y, t.width, t.height, ax, ay)]
os.makedirs(os.path.join(ROOT, 'src/assets/shk'), exist_ok=True)
out.save(os.path.join(ROOT, 'src/assets/shk/shk.webp'), lossless=True)
json.dump(frames, open(os.path.join(ROOT, 'src/assets/shk/shk.json'), 'w'))
print(out.size, {k: len(v) for k, v in frames.items()})
