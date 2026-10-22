"""저주받은 해골 궁수 최종 진화형 시트 → 아틀라스 (자르기·배경 제거만, 색 수정 없음)
사용: python3 tools/atlas/skelf_build.py <시트.png>
 → src/assets/skin/skelF.{webp,json} (프레임 [x,y,w,h,기준x(몸통),기준y(발)] · idle walk attack hit death skill)
 + skelF_arrow.webp (칠흑의 대궁 화살 · 시트 스킬 줄의 큰 화살)"""
import sys, json, os
import numpy as np
from PIL import Image
from scipy import ndimage as nd
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'src/assets/skin'); os.makedirs(OUT, exist_ok=True)
src = sys.argv[1]; THR = 24
A = np.array(Image.open(src).convert('RGBA')); RGB = A[:, :, :3].astype(int); M = RGB.max(axis=2)
# 줄: (위, 아래, 칸 경계 x들, 기준 방식 'foot'|'box')
ROWS = {
  'idle':   (48, 166, [595 + 108 * i for i in range(7)], 'foot'),
  'walk':   (214, 314, [592 + 100 * i for i in range(9)], 'foot'),
  'attack': (360, 488, [598 + 108 * i for i in range(6)] + [1268], 'foot'),
  'hit':    (538, 634, [590, 775, 930, 1075, 1285], 'box'),
  'death':  (688, 782, [590, 700, 840, 950, 1105, 1225, 1300], 'box'),
  'skill':  (832, 972, [592, 700, 812, 928, 1046], 'foot'),
}
VAL = 22
tiles = []; frames = {}
for k, (y0, y1, edges, mode) in ROWS.items():
    occ = (M[y0:y1] > THR + 10).sum(axis=0); e = list(edges)
    for i in range(1, len(e) - 1):   # 칸 경계를 가장 빈 세로줄로
        lo, hi = e[i] - VAL, e[i] + VAL; seg = occ[lo:hi]; xs = np.where(seg == seg.min())[0]; e[i] = lo + int(xs[len(xs) // 2])
    raw = []
    for i in range(len(e) - 1):
        x0, x1 = e[i], e[i + 1]
        m = M[y0:y1, x0:x1] > THR
        lab, n = nd.label(nd.binary_closing(np.pad(m, 3), structure=np.ones((3, 3)))[3:-3, 3:-3] | m)
        sz = nd.sum(m, lab, range(1, n + 1)); mx = sz.max(); ok = []
        for j, sl in enumerate(nd.find_objects(lab)):
            edge = sl[1].start == 0 or sl[1].stop == m.shape[1]
            if sz[j] >= 25 and not (edge and sz[j] < 0.25 * mx) and not ((sl[1].stop - sl[1].start) <= 4 and (sl[0].stop - sl[0].start) >= 20): ok.append(j + 1)
        keep = np.isin(lab, ok) & (nd.binary_dilation(m, iterations=1))
        keep = nd.binary_fill_holes(keep)
        th = nd.binary_dilation(nd.binary_opening(keep, structure=np.ones((3, 3))), iterations=1)   # 바닥 선·패널 조각 지우기
        keep &= ~((nd.binary_opening(keep, structure=np.ones((1, 14))) | nd.binary_opening(keep, structure=np.ones((14, 1)))) & ~th)
        if mode == 'foot':   # 바닥 선(발보다 훨씬 넓은 맨 아래 가로줄) 지우기
            rw = keep.sum(axis=1); yb = np.where(rw > 0)[0].max()
            while yb > 8 and rw[yb] > 1.5 * max(rw[yb - 7], 1): keep[yb] = False; rw[yb] = 0; yb = np.where(rw > 0)[0].max()
        if k == 'attack' and i == 0:   # 왼쪽 큰 그림의 화살촉 조각
            l3, n3 = nd.label(keep)
            for q in range(1, n3 + 1):
                cx = np.where(l3 == q)[1].mean()
                if cx < 22: keep[l3 == q] = False
        lab2, n2 = nd.label(keep); sz2 = nd.sum(keep, lab2, range(1, n2 + 1)); big = lab2 == (int(np.argmax(sz2)) + 1)
        ys, xs = np.where(keep); by, bx = np.where(big)
        X0, X1, Y0, Y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        if mode == 'foot':
            bot = by > by.max() - 14; fx = float(bx[bot].mean())   # 발 근처 가운데
        else: fx = (bx.min() + bx.max()) / 2
        raw.append((x0, y0, X0, Y0, X1, Y1, fx, keep))
    if mode == 'foot':   # 칸마다 흔들리지 않게: 칸 시작 기준 발 위치의 중앙값으로 고정
        off = float(np.median([r[6] - 0 for r in raw]))
    for i, (x0, yy, X0, Y0, X1, Y1, fx, keep) in enumerate(raw):
        t = np.zeros((Y1 - Y0, X1 - X0, 4), np.uint8); t[:, :, :3] = A[y0 + Y0:y0 + Y1, x0 + X0:x0 + X1, :3]; t[:, :, 3] = keep[Y0:Y1, X0:X1] * 255
        axv = (fx if mode == 'box' else off) - X0
        tiles.append((k, i, Image.fromarray(t), int(round(axv)), int(Y1 - Y0)))
        frames.setdefault(k, []).append(None)
W = 1024; x = y = rh = 0; place = []
for k, i, t, ax, ay in tiles:
    if x + t.width > W: x = 0; y += rh + 2; rh = 0
    place.append((k, i, t, x, y, ax, ay)); x += t.width + 2; rh = max(rh, t.height)
out = Image.new('RGBA', (W, y + rh), (0, 0, 0, 0))
for k, i, t, x, y, ax, ay in place: out.paste(t, (x, y)); frames[k][i] = [int(v) for v in (x, y, t.width, t.height, ax, ay)]
out.save(os.path.join(OUT, 'skelF.webp'), lossless=True); json.dump(frames, open(os.path.join(OUT, 'skelF.json'), 'w'))
print(out.size, {k: len(v) for k, v in frames.items()})
# 화살(스킬 줄 큰 화살) · 충돌 이펙트: 검은 배경 그대로 잘라 게임에서 'lighter'로 그린다 (검정 = 투명)
def cut(x0, x1, y0, y1, name, mask):
    t = np.zeros((y1 - y0, x1 - x0, 4), np.uint8); t[:, :, :3] = A[y0:y1, x0:x1, :3]
    mm = M[y0:y1, x0:x1] > THR
    if mask: mm = nd.binary_fill_holes(nd.binary_closing(mm, structure=np.ones((3, 3)), iterations=2)) & nd.binary_dilation(mm, iterations=2)
    t[:, :, 3] = mm * 255 if mask else 255
    Image.fromarray(t).save(os.path.join(OUT, name + '.webp'), lossless=True); print(name, t.shape)
cut(1040, 1300, 836, 982, 'skelF_arrow', False)

