"""사슬의 폭군 · 돌쇠 스킨 시트 → 아틀라스 + 일러스트 (자르기·배경 제거만, 색 수정 없음)
사용: python3 tools/atlas/twskin_build.py <시트.png> → src/assets/skin/twS.{webp,json} + twS_art.webp
키: idle walk lash(기본 공격) combo(사슬 휘두르기) hit death — 원본은 오른쪽을 본다
기준점: 칸마다 흔들리지 않게 '연보라 머리카락' 위치 + 고정 보정(머리카락 → 몸 가운데), 발 높이는 줄마다 고정"""
import sys, json, os
import numpy as np
from PIL import Image
from scipy import ndimage as nd
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'src/assets/skin'); os.makedirs(OUT, exist_ok=True)
src = sys.argv[1]; THR = 24
A = np.array(Image.open(src).convert('RGBA')); RGB = A[:, :, :3].astype(int); M = RGB.max(axis=2)
R, G, B = RGB[:, :, 0], RGB[:, :, 1], RGB[:, :, 2]
HAIR = (B > 150) & (R > 140) & (G > 120) & (np.abs(R - B) < 60) & (G > 0.7 * R)   # 연보라 머리카락
def eq(a, b, n): return [int(a + (b - a) * i / n) for i in range(n + 1)]
def mids(c): return [148] + [(c[i] + c[i + 1]) // 2 for i in range(len(c) - 1)] + [1430]   # 머리 가운데 사이를 칸 경계로
ROWS = {
  'idle':   (378, 474, mids([195, 298, 404, 523, 630, 740, 858, 955, 1074, 1196, 1322])),
  'walk':   (490, 584, mids([205, 317, 416, 522, 623, 721, 842, 961, 1074, 1186, 1279])),
  'lash':   (596, 706, [150, 262, 372, 482, 590, 700, 905, 1250, 1428]),
  'combo':  (722, 832, [150, 262, 458, 580, 705, 890, 1140, 1430]),
  'hit':    (842, 944, eq(148, 1428, 10)),
  'death':  (958, 1056, [150, 265, 445, 640, 835, 1190, 1430]),
}
VAL = 14; raw = {}
for k, (y0, y1, edges) in ROWS.items():
    occ = (M[y0:y1] > THR + 10).sum(axis=0); e = list(edges)
    for i in range(1, len(e) - 1):
        lo, hi = e[i] - VAL, e[i] + VAL; seg = occ[lo:hi]; xs = np.where(seg == seg.min())[0]; e[i] = lo + int(xs[len(xs) // 2])
    L = []
    for i in range(len(e) - 1):
        x0, x1 = e[i], e[i + 1]; m = M[y0:y1, x0:x1] > THR
        lab, n = nd.label(m); sz = nd.sum(m, lab, range(1, n + 1)); mx = sz.max(); ok = []
        for j, sl in enumerate(nd.find_objects(lab)):
            edge = sl[1].start == 0 or sl[1].stop == m.shape[1]
            thin = (sl[1].stop - sl[1].start) <= 4 and (sl[0].stop - sl[0].start) >= 20
            if sz[j] >= 20 and not thin and not (edge and sz[j] < 0.2 * mx): ok.append(j + 1)
        keep = np.isin(lab, ok)
        keep = nd.binary_closing(np.pad(keep, 3), structure=np.ones((3, 3)))[3:-3, 3:-3] | keep
        keep = nd.binary_fill_holes(keep) if k not in ('combo',) else keep
        th = nd.binary_dilation(nd.binary_opening(keep, structure=np.ones((3, 3))), iterations=1)
        keep &= ~((nd.binary_opening(keep, structure=np.ones((1, 16))) | nd.binary_opening(keep, structure=np.ones((16, 1)))) & ~th & (M[y0:y1, x0:x1] < 90))
        ys, xs = np.where(keep)
        X0, X1, Y0, Y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        h = HAIR[y0:y1, x0:x1] & keep; hy, hx = np.where(h)
        hair = float(hx.mean()) if len(hx) > 30 else None
        L.append(dict(x0=x0, y0=y0, X0=X0, X1=X1, Y0=Y0, Y1=Y1, hair=hair, keep=keep, cx=(X0 + X1) / 2, bot=Y1))
    raw[k] = L
# 머리카락 → 몸 가운데 보정: 대기·이동 프레임에서 (프레임 가운데 - 머리카락) 중앙값
K = float(np.median([f['cx'] - f['hair'] for r in ('idle', 'walk') for f in raw[r] if f['hair'] is not None]))
print('hair->body', round(K, 1))
tiles = []; frames = {}
for k, L in raw.items():
    foot = float(np.median([f['bot'] for f in L if f['hair'] is not None]))   # 줄마다 고정한 발 높이(칸 안 y)
    for f in L:
        t = np.zeros((f['Y1'] - f['Y0'], f['X1'] - f['X0'], 4), np.uint8)
        t[:, :, :3] = A[f['y0'] + f['Y0']:f['y0'] + f['Y1'], f['x0'] + f['X0']:f['x0'] + f['X1'], :3]; t[:, :, 3] = f['keep'][f['Y0']:f['Y1'], f['X0']:f['X1']] * 255
        ax = (f['hair'] + K if f['hair'] is not None else f['cx']) - f['X0']
        ay = foot - f['Y0'] if f['hair'] is not None and k != 'death' else f['bot'] - f['Y0']
        if k == 'death': ay = f['bot'] - f['Y0']
        tiles.append((k, Image.fromarray(t), int(round(ax)), int(round(ay))))
W = 1400; x = y = rh = 0; place = []
for k, t, ax, ay in tiles:
    if x + t.width > W: x = 0; y += rh + 2; rh = 0
    place.append((k, t, x, y, ax, ay)); x += t.width + 2; rh = max(rh, t.height)
out = Image.new('RGBA', (W, y + rh), (0, 0, 0, 0))
for k, t, x, y, ax, ay in place:
    out.paste(t, (x, y)); frames.setdefault(k, []).append([int(v) for v in (x, y, t.width, t.height, ax, ay)])
out.save(os.path.join(OUT, 'twS.webp'), lossless=True); json.dump(frames, open(os.path.join(OUT, 'twS.json'), 'w'))
Image.open(src).convert('RGB').crop((0, 0, 670, 362)).save(os.path.join(OUT, 'twS_art.webp'), quality=90)
print(out.size, {k: len(v) for k, v in frames.items()})
