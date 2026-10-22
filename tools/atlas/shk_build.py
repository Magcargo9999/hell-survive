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
LBL_X = {'idle': 640, 'walk': 640, 'atk': 645, 'spit': 645, 'hit': 645, 'death': 640, 'cast': 735, 'spore': 735, 'sum': 700, 'erupt': 700, 'fx': 200}
frames, tiles = {}, []
for k, (y0, y1, lb, cells) in ROWS.items():
    frames[k] = []
    for (x0, x1) in cells:
        rgb = RGB[y0:y1, x0:x1]; m = rgb.max(axis=2) > 20
        if lb and x0 < LBL_X.get(k, 0):   # 라벨 상자: 아래 테두리(붉은 가로선)까지 지운다
            lx0 = 14 if k == 'fx' else 482; R = RGB[y0 - 4:y0 + 44, lx0:LBL_X[k]]
            line = ((R[:, :, 0] > 120) & (R[:, :, 1] < 50) & (R[:, :, 2] > 35) & (R[:, :, 2] < 110)).sum(axis=1)
            rows = [i for i, c in enumerate(line) if c >= 40]; bot = (y0 - 4 + max(rows)) if rows else lb
            m[:max(0, bot - y0 + 2), :LBL_X[k] - x0] = False
        if k == 'fx': m[:max(0, lb - y0 + 2), :] = m[:max(0, lb - y0 + 2), :] if x0 > 200 else False
        m[:, :2] = m[:, -2:] = False; m[:2, :] = m[-2:, :] = False                       # 패널 테두리
        m[:3, :] = False                                                                  # 패널 윗 테두리
        lab, n = nd.label(m)
        for sl_i, sl in enumerate(nd.find_objects(lab)):                                  # 가늘고 긴 선(테두리 조각) 제거
            h_, w_ = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
            if (h_ <= 4 and w_ >= 14) or (w_ <= 4 and h_ >= 14): m[lab == sl_i + 1] = False
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
