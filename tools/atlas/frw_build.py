"""서리혈랑(지하 25층 · 릴세르카 판 미니 보스) 컨셉 시트 → 아틀라스 (자르기·배경 제거만, 색 수정 없음)
사용: python3 tools/atlas/frw_build.py <시트.png> → src/assets/frw/frw.{webp,json}
어두운 남색 배경은 밝기 문턱으로 지우고, 패널 테두리·바닥 가는 선(가로/세로로 길고 얇은 덩어리)과 줄 이름표(대기·IDLE 등) 칸은 뺀다.
프레임 [x, y, w, h, 기준x(발 가운데), 기준y(바닥)] · 시트는 오른쪽을 본다
그룹: idle 3 · move 4 · atk 3 · sk 4(서리 절단 · 혈빙 가시 · 빙혈 폭풍 · 영혼의 겨울) · hit 4 · death 4"""
import sys, os, json
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as nd
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = Image.open(sys.argv[1]).convert('RGBA'); A = np.array(S); L = A[..., :3].max(axis=2).astype(int)
LABELS = [(15, 515, 80, 563), (635, 515, 690, 563), (15, 660, 110, 703), (600, 660, 660, 703), (15, 897, 80, 943), (615, 897, 680, 943), (640, 855, 1420, 885)]
for x0, y0, x1, y1 in LABELS: L[y0:y1, x0:x1] = 0
def valley(y0, y1, c, w=16):
    seg = (L[y0:y1, c - w:c + w] > 40).sum(axis=0); xs = np.where(seg == seg.min())[0]; return c - w + int(xs[len(xs) // 2])
def cut(x0, y0, x1, y1, thr=34):
    reg = A[y0:y1, x0:x1].copy(); lum = L[y0:y1, x0:x1]; fg = lum >= thr
    lab, n = nd.label(fg, structure=np.ones((3, 3)))
    for i, sl in enumerate(nd.find_objects(lab), 1):
        hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start; a = (lab[sl] == i).sum()
        if (hh <= 5 and ww >= 40) or (ww <= 5 and hh >= 40) or a < 10: fg[sl] &= ~(lab[sl] == i)
    cl = nd.binary_closing(fg, structure=np.ones((3, 3)), iterations=2)
    lab, n = nd.label(cl, structure=np.ones((3, 3)))
    if n == 0: return None, None
    sz = nd.sum(np.ones_like(lum), lab, range(1, n + 1)); mx = sz.max()
    keep = [i + 1 for i, s in enumerate(sz) if s >= max(30, mx * 0.008)]
    m = np.isin(lab, keep)   # 구멍 메우기는 하지 않는다(소용돌이·검기 안쪽 배경이 막히지 않게)
    reg[..., 3] = np.where(m & (lum >= 24), 255, 0)
    im = Image.fromarray(reg); return im, im.getchannel('A').getbbox()
ROWS = {   # (y0, y1, x0, x1, 경계 대략)
 'idle':  (520, 645, 25, 618, [222, 415]),
 'move':  (520, 645, 650, 1435, [835, 1030, 1228]),
 'atk':   (668, 858, 8, 588, [208, 410]),
 'sk':    (668, 858, 598, 1442, [793, 978, 1218]),
 'hit':   (900, 1058, 8, 590, [150, 282, 432]),
 'death': (900, 1060, 612, 1442, [810, 990, 1155]),
}
frames = {}
for k, (y0, y1, x0, x1, cs) in ROWS.items():
    xs = [x0] + [valley(y0, y1, c) for c in cs] + [x1]; Lf = []
    for i in range(len(xs) - 1):
        im, bb = cut(xs[i], y0, xs[i + 1], y1)
        if bb is None: continue
        a = np.array(im.getchannel('A')); ys, xx = np.where(a > 0); yb = ys.max(); sel = xx[ys > yb - max(8, int((yb - ys.min()) * 0.15))]
        ax = float(np.median(sel)) - bb[0]; im = im.crop(bb); Lf.append((im, int(round(ax)), im.height))
    frames[k] = Lf
meta = {}; W = 1500; x = y = rh = 0; place = []
for k, Lf in frames.items():
    for im, ax, ay in Lf:
        if x + im.width > W: x = 0; y += rh + 2; rh = 0
        place.append((k, im, x, y, ax, ay)); meta.setdefault(k, []).append([x, y, im.width, im.height, ax, ay]); x += im.width + 2; rh = max(rh, im.height)
at = Image.new('RGBA', (W, y + rh), (0, 0, 0, 0))
for k, im, x, y, ax, ay in place: at.alpha_composite(im, (x, y))
out = os.path.join(ROOT, 'src/assets/frw'); os.makedirs(out, exist_ok=True); os.makedirs(os.path.join(ROOT, 'build/fw2'), exist_ok=True)
at.save(os.path.join(out, 'frw.webp'), lossless=True); json.dump(meta, open(os.path.join(out, 'frw.json'), 'w'))
b2 = Image.new('RGBA', at.size, (60, 110, 70, 255)); b2.alpha_composite(at); b2.save(os.path.join(ROOT, 'build/fw2/atlas_prev.png'))
print(at.size, {k: len(v) for k, v in meta.items()})
