"""해저좀비(썩어버린 해군 제독 판 미니 보스) 시트 → 아틀라스 (자르기·배경 제거(마스크)만, 색 수정 없음)
사용: python3 tools/atlas/zom_build.py <시트.png> → src/assets/zom/zom.{webp,json}
프레임 [x, y, 너비, 높이, 기준x(몸통 가운데), 기준y(발)] · 시트는 오른쪽을 본다(게임에서 face<0이면 뒤집음)
줄: idle 4 · walk 5 · atk 5(물보라 포함) · hit 3 · death 6(유령 포함) · fx 13(물보라·초록 웅덩이·유령 5·물결·잔물결) · port(큰 일러스트, 도감)"""
import sys, json, os
import numpy as np
from PIL import Image
from scipy import ndimage as nd
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'src/assets/zom'); os.makedirs(OUT, exist_ok=True); os.makedirs(os.path.join(ROOT, 'build/zom'), exist_ok=True)
A = np.array(Image.open(sys.argv[1]).convert('RGBA')); AL = A[:, :, 3] > 40
# 줄: (y0, y1, 경계들, 칸별 y0 보정 {칸번호: y0}, 경계 다듬기 여부)
ROWS = {
  'idle':  (50, 228, [515, 700, 892, 1086, 1270], {}, True),
  'walk':  (233, 421, [509, 697, 882, 1045, 1206, 1440], {}, True),
  'atk':   (424, 646, [509, 692, 906, 1088, 1290, 1445], {}, True),
  'hit':   (648, 826, [509, 700, 900, 1118], {}, True),
  'death': (826, 978, [20, 238, 459, 714, 946, 1174, 1445], {0: 796, 5: 796}, True),
}
FX = [(43, 199), (211, 312), (323, 445), (450, 536), (554, 697), (725, 772), (779, 805), (822, 866), (894, 943), (957, 982), (996, 1147), (1168, 1242), (1261, 1390)]
def refine(y0, y1, b):
    occ = AL[y0:y1].sum(axis=0); b = list(b)
    for i in range(1, len(b) - 1):
        lo, hi = b[i] - 22, b[i] + 22; seg = occ[lo:hi]; xs = np.where(seg == seg.min())[0]; b[i] = lo + int(xs[len(xs) // 2])
    return b
def cut(x0, x1, y0, y1, pad_keep=True):
    m = AL[y0:y1, x0:x1].copy()
    lab, n = nd.label(nd.binary_dilation(m, iterations=2)); lab = lab * m
    if n == 0: return None
    sz = nd.sum(m, lab, range(1, n + 1)); mx = sz.max(); ok = []
    for j, sl in enumerate(nd.find_objects(lab)):
        if sl is None: continue
        w = sl[1].stop - sl[1].start; h = sl[0].stop - sl[0].start
        edge = sl[1].start == 0 or sl[1].stop == m.shape[1]
        if sz[j] >= 6 and not (edge and sz[j] < 0.1 * mx) and not (sz[j] < 0.004 * mx): ok.append(j + 1)
    keep = np.isin(lab, ok)
    ys, xs = np.where(keep)
    if not len(xs): return None
    X0, X1, Y0, Y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    t = np.zeros((Y1 - Y0, X1 - X0, 4), np.uint8)
    t[:, :, :3] = A[y0 + Y0:y0 + Y1, x0 + X0:x0 + X1, :3]; t[:, :, 3] = keep[Y0:Y1, X0:X1] * A[y0 + Y0:y0 + Y1, x0 + X0:x0 + X1, 3]
    return t, keep, X0, X1, Y0, Y1, xs, ys
tiles = []
for k, (y0, y1, bnd, ydef, rf) in ROWS.items():
    if rf: bnd = refine(y0, y1, bnd)
    for i in range(len(bnd) - 1):
        r = cut(bnd[i], bnd[i + 1], ydef.get(i, y0), y1)
        if not r: continue
        t, keep, X0, X1, Y0, Y1, xs, ys = r
        # 기준: 발 = 몸 아래(물보라까지 포함한 맨 아래), x = 몸통 중간 높이 가로 평균
        mid = (ys >= Y0 + 0.3 * (Y1 - Y0)) & (ys <= Y0 + 0.75 * (Y1 - Y0)); ax = float(xs[mid].mean()) - X0
        tiles.append((k, Image.fromarray(t), int(round(ax)), t.shape[0]))
for x0, x1 in FX:
    r = cut(x0, x1, 978, 1084)
    if not r: continue
    t = r[0]; tiles.append(('fx', Image.fromarray(t), t.shape[1] // 2, t.shape[0]))
# 큰 일러스트(도감용)
r = cut(0, 516, 0, 700)
if r: t = r[0]; tiles.append(('port', Image.fromarray(t), t.shape[1] // 2, t.shape[0]))
W = 1400; x = y = rh = 0; place = []; F = {}
for k, t, ax, ay in tiles:
    if x + t.width > W: x = 0; y += rh + 2; rh = 0
    place.append((k, t, x, y, ax, ay)); x += t.width + 2; rh = max(rh, t.height)
out = Image.new('RGBA', (W, y + rh), (0, 0, 0, 0))
for k, t, x, y, ax, ay in place: out.paste(t, (x, y)); F.setdefault(k, []).append([int(v) for v in (x, y, t.width, t.height, ax, ay)])
out.save(os.path.join(OUT, 'zom.webp'), lossless=True); json.dump(F, open(os.path.join(OUT, 'zom.json'), 'w'))
print(out.size, {k: len(v) for k, v in F.items()})
bg = Image.new('RGBA', out.size, (60, 60, 80, 255)); bg.alpha_composite(out); bg.save(os.path.join(ROOT, 'build/zom/atlas_prev.png'))
