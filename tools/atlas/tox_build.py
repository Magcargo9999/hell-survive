"""이독버섯 마왕 시트 → 아틀라스 (자르기·배경 제거만, 색 수정 없음)
사용: python3 tools/atlas/tox_build.py <시트.png> → src/assets/tox/tox.{webp,json}
프레임 [x, y, 너비, 높이, 기준x(발 가운데), 기준y(발)] · 원본은 정면/왼쪽 (게임에서 정수 2배 nearest로 그린다)"""
import sys, json, os
import numpy as np
from PIL import Image
from scipy import ndimage as nd
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'src/assets/tox'); os.makedirs(OUT, exist_ok=True)
A = np.array(Image.open(sys.argv[1]).convert('RGBA')); RGB = A[:, :, :3].astype(int); M = RGB.max(axis=2)
THR = 30
# 줄 이름: (위, 아래, [(x0, x1), …], 기준 'foot' = 발 가운데 | 'c' = 그림 가운데)
ROWS = {
  'idle':  (382, 470, [(114, 231), (231, 337), (337, 447), (447, 541), (541, 656), (656, 760), (760, 880)], 'foot'),
  'walk':  (484, 580, [(112, 225), (225, 330), (330, 430), (430, 530), (530, 635), (635, 740), (740, 886)], 'foot'),
  'atk':   (590, 690, [(112, 218), (219, 302), (302, 442), (418, 507)], 'foot'),
  'cast':  (700, 788, [(118, 268), (285, 390), (390, 492), (492, 603), (603, 752), (752, 882)], 'foot'),
  'melt':  (800, 889, [(115, 268), (275, 375), (375, 478), (478, 595), (595, 700), (700, 792), (792, 885)], 'foot'),
  'ball':  (596, 632, [(512, 575)], 'c'),
  'splash': (598, 690, [(592, 702), (702, 802), (802, 885)], 'foot'),
  'pool':  (420, 474, [(1150, 1255), (1262, 1398), (1398, 1532)], 'c'),
  'pbig':  (505, 548, [(1030, 1085)], 'c'),
  'swamp': (785, 868, [(1092, 1312)], 'c'),
  'rise':  (752, 866, [(1335, 1518)], 'foot'),
  'mini':  (928, 1009, [(25, 95), (100, 162), (170, 250), (250, 332), (355, 415), (418, 505), (505, 598), (598, 712), (715, 812), (812, 918)], 'foot'),
  'core':  (930, 1012, [(960, 1045), (1055, 1150), (1175, 1270), (1285, 1405), (1405, 1505)], 'c'),
}
VALLEY = {'idle', 'walk', 'atk', 'cast', 'melt', 'mini'}
def refine(y0, y1, cells):   # 칸 경계를 윗몸 그림이 가장 비어 있는 세로줄로 (바닥 점액 줄은 빼고)
    occ = (M[y0:y1 - 16] > 45).sum(axis=0); c = [list(v) for v in cells]
    for i in range(len(c) - 1):
        lo, hi = c[i][1] - 20, c[i][1] + 20; seg = occ[lo:hi]; xs = np.where(seg == seg.min())[0]; v = lo + int(xs[len(xs) // 2]); c[i][1] = c[i + 1][0] = v
    return [tuple(v) for v in c]
tiles = []
for k, (y0, y1, cells, mode) in ROWS.items():
    if k in VALLEY: cells = refine(y0, y1, cells)
    for i, (x0, x1) in enumerate(cells):
        m = M[y0:y1, x0:x1] > THR
        lab, n = nd.label(nd.binary_dilation(m, iterations=1)); lab = lab * m
        sz = nd.sum(m, lab, range(1, n + 1)); mx = sz.max(); ok = []
        for j, sl in enumerate(nd.find_objects(lab)):
            if sl is None: continue
            edge = sl[1].start == 0 or sl[1].stop == m.shape[1]
            thin = ((sl[1].stop - sl[1].start) <= 4 and (sl[0].stop - sl[0].start) >= 20) or ((sl[0].stop - sl[0].start) <= 3 and (sl[1].stop - sl[1].start) >= 40)
            if sz[j] >= 6 and not thin and not (edge and sz[j] < 0.15 * mx): ok.append(j + 1)
        keep = np.isin(lab, ok)
        keep = nd.binary_closing(np.pad(keep, 3), structure=np.ones((3, 3)))[3:-3, 3:-3] | keep
        if k not in ('splash',): keep = nd.binary_fill_holes(keep)
        rw = keep.sum(axis=1); ys0 = np.where(rw > 0)[0]
        if mode == 'foot' and len(ys0):   # 패널 바닥 선(아주 넓고 얇은 맨 아래 줄) 지우기
            yb = ys0.max()
            while yb > 10 and rw[yb] > 1.6 * max(rw[yb - 6], 1) and rw[yb] > 40: keep[yb] = False; rw[yb] = 0; yb = np.where(rw > 0)[0].max()
        ys, xs = np.where(keep); X0, X1, Y0, Y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        if mode == 'foot': bot = ys > Y1 - 12; ax = float(xs[bot].mean()) - X0; ay = Y1 - Y0
        else: ax = (X1 - X0) / 2; ay = (Y1 - Y0) / 2
        t = np.zeros((Y1 - Y0, X1 - X0, 4), np.uint8); t[:, :, :3] = A[y0 + Y0:y0 + Y1, x0 + X0:x0 + X1, :3]; t[:, :, 3] = keep[Y0:Y1, X0:X1] * 255
        tiles.append((k, Image.fromarray(t), int(round(ax)), int(round(ay))))
W = 1024; x = y = rh = 0; place = []; F = {}
for k, t, ax, ay in tiles:
    if x + t.width > W: x = 0; y += rh + 2; rh = 0
    place.append((k, t, x, y, ax, ay)); x += t.width + 2; rh = max(rh, t.height)
out = Image.new('RGBA', (W, y + rh), (0, 0, 0, 0))
for k, t, x, y, ax, ay in place: out.paste(t, (x, y)); F.setdefault(k, []).append([int(v) for v in (x, y, t.width, t.height, ax, ay)])
out.save(os.path.join(OUT, 'tox.webp'), lossless=True); json.dump(F, open(os.path.join(OUT, 'tox.json'), 'w'))
print(out.size, {k: len(v) for k, v in F.items()})
