"""v9.85 검 도깨비 마왕 아틀라스 — 사용자가 준 시트 한 장(왼쪽 인게임 도트 · 오른쪽 이펙트)을 자르고 배경만 지운다 (도트는 그대로)
python3 tools/atlas/dok_build.py <시트.png> <출력 폴더(src/assets)>
몸 → dok/dok.webp + dok.json  ·  이펙트 → dokfx/dokfx.webp + dokfx.json"""
import sys, json, os
import numpy as np
from PIL import Image
from collections import deque

src, out = sys.argv[1], sys.argv[2]
A = np.asarray(Image.open(src).convert('RGB')).astype(int)
MX = A.max(axis=2)

def lines_off(m):   # 판 테두리선(행·열 대부분이 칠해진 줄) 지우기
    m = m.copy(); h, w = m.shape
    for y in range(h):
        if m[y].mean() > 0.55: m[y] = False
    for x in range(w):
        if m[:, x].mean() > 0.55: m[:, x] = False
    return m

def segs(m, gap=3, minw=14):   # 세로 빈 줄로 칸 나누기
    col = m.sum(axis=0) > 0; out_ = []; x = 0; w = len(col)
    while x < w:
        if not col[x]: x += 1; continue
        x0 = x; g = 0
        while x < w and g < gap:
            g = g + 1 if not col[x] else 0; x += 1
        x1 = x - g
        if x1 - x0 >= minw: out_.append((x0, x1))
    return out_

LABELS = [(18, 70, 160, 102), (18, 212, 156, 245), (18, 358, 262, 393), (18, 496, 266, 530), (18, 636, 176, 667), (258, 636, 394, 667), (548, 636, 676, 667), (18, 758, 156, 790)]
def char_cut(x0, y0, x1, y1, thr=34, n=None, cuts=None):
    reg = A[y0:y1, x0:x1].copy(); mx = reg.max(axis=2).copy()
    for a, b, c, d in LABELS:   # 줄 이름표 자리는 배경으로
        ya, yb, xa, xb = max(b, y0) - y0, min(d, y1) - y0, max(a, x0) - x0, min(c, x1) - x0
        if ya < yb and xa < xb: mx[ya:yb, xa:xb] = 0; reg[ya:yb, xa:xb] = 0
    fg = lines_off(mx > thr)
    col = fg.sum(axis=0)
    if cuts: ss = [(c0 - x0, c1 - x0) for c0, c1 in cuts]
    else:   # 칸을 고르게 나누되 경계는 근처에서 가장 빈 세로줄로
        xs = np.where(col > 0)[0]; L, R = xs[0], xs[-1] + 1; bnd = [L]
        for i in range(1, n):
            c = L + (R - L) * i / n; lo, hi = int(c - 22), int(c + 22); bnd.append(lo + int(np.argmin(col[lo:hi])))
        bnd.append(R); ss = list(zip(bnd[:-1], bnd[1:]))
    res = []
    for a, b in ss:
        sub = fg[:, a:b]; ys = np.where(sub.any(axis=1))[0]; xs0 = np.where(sub.any(axis=0))[0]; ya, yb = ys[0], ys[-1] + 1; a, b = a + xs0[0], a + xs0[-1] + 1
        crop = reg[ya:yb, a:b]; cm = mx[ya:yb, a:b]; h, w = cm.shape
        bgl = cm <= thr; vis = np.zeros_like(bgl); q = deque()
        for yy in range(h):
            for xx in (0, w - 1):
                if bgl[yy, xx] and not vis[yy, xx]: vis[yy, xx] = 1; q.append((yy, xx))
        for xx in range(w):
            for yy in (0, h - 1):
                if bgl[yy, xx] and not vis[yy, xx]: vis[yy, xx] = 1; q.append((yy, xx))
        while q:   # 칸 가장자리와 이어진 어두운 배경만 투명
            yy, xx = q.popleft()
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = yy + dy, xx + dx
                if 0 <= ny < h and 0 <= nx < w and bgl[ny, nx] and not vis[ny, nx]: vis[ny, nx] = 1; q.append((ny, nx))
        alpha = np.where(vis, 0, 255)
        # 작은 부스러기(테두리 찌꺼기) 제거: 열 단위로 거의 빈 가장자리 정리는 생략 — 도트는 그대로
        rgba = np.dstack([crop, alpha]).astype(np.uint8)
        mid = alpha[int(h * 0.15):int(h * 0.55)] > 0   # 기준 x = 머리·몸통(위쪽 15~55%)의 가운데 — 칼끝·다리에 흔들리지 않게
        ax = float(np.median(np.where(mid)[1])) if mid.any() else w / 2
        res.append((Image.fromarray(rgba, 'RGBA'), ax))
    return res

FXLAB = [(903, 70, 1128, 101), (1338, 70, 1572, 101), (903, 200, 1072, 227), (1323, 200, 1507, 227), (903, 309, 1062, 337), (1338, 309, 1542, 337),
         (903, 434, 1077, 464), (1338, 434, 1512, 464), (903, 552, 1097, 580), (1288, 552, 1542, 580), (903, 662, 1072, 692), (1310, 662, 1547, 692), (903, 772, 1072, 800), (1326, 772, 1507, 800)]
def fx_cut(x0, y0, x1, y1, cuts=None, n=None, t0=22, t1=70):
    reg = A[y0:y1, x0:x1].copy(); mx = reg.max(axis=2).copy()
    for a, b, c, d in FXLAB:
        ya, yb, xa, xb = max(b, y0) - y0, min(d, y1) - y0, max(a, x0) - x0, min(c, x1) - x0
        if ya < yb and xa < xb: mx[ya:yb, xa:xb] = 0
    fg = lines_off(mx > t0 + 10)
    if cuts: ss = [(c0 - x0, c1 - x0) for c0, c1 in cuts]
    elif n: ss = segs(fg, 4, 10)
    else: ss = [(0, x1 - x0)]
    if n:
        while len(ss) > n:
            gi = min(range(len(ss) - 1), key=lambda i: ss[i + 1][0] - ss[i][1]); ss[gi:gi + 2] = [(ss[gi][0], ss[gi + 1][1])]
    res = []
    for a, b in ss:
        sub = fg[:, a:b]; ys = np.where(sub.any(axis=1))[0]; xs = np.where(sub.any(axis=0))[0]
        if not ys.size: continue
        ya, yb, xa, xb = ys[0], ys[-1] + 1, a + xs[0], a + xs[-1] + 1
        crop = reg[ya:yb, xa:xb]; cm = mx[ya:yb, xa:xb]
        alpha = np.clip((cm - t0) / (t1 - t0), 0, 1) * 255 * (fg[ya:yb, xa:xb] | (cm > t0))   # 어두운 배경 → 투명 (밝기만큼 반투명)
        rgba = np.dstack([crop, alpha]).astype(np.uint8)
        res.append(Image.fromarray(rgba, 'RGBA'))
    return res

def pack(groups, path, anchors=None):
    pad = 2; maxw = 2048; x = y = rowh = 0; rects = {}; place = []
    for k, ims in groups.items():
        rects[k] = []
        for i, im in enumerate(ims):
            w, h = im.size
            if x + w > maxw: x = 0; y += rowh + pad; rowh = 0
            place.append((im, x, y)); r = [x, y, w, h]
            if anchors is not None: r += [round(anchors[k][i], 1), h - 1]
            rects[k].append(r); x += w + pad; rowh = max(rowh, h)
    W, H = maxw, y + rowh
    sheet = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for im, xx, yy in place: sheet.paste(im, (xx, yy))
    used = max(r[0] + r[2] for v in rects.values() for r in v)
    sheet = sheet.crop((0, 0, used, H))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sheet.save(path + '.webp', lossless=True); sheet.save(path + '_preview.png')
    json.dump(rects, open(path + '.json', 'w'), separators=(',', ':'))
    return rects

# ---- 몸 (왼쪽 판, 오른쪽을 봄) ----
ROWS = {'idle': (18, 70, 874, 207, 7), 'walk': (18, 212, 874, 352, 7), 'atk': (18, 358, 874, 494, 6), 'combo': (18, 496, 874, 632, 7),
        'guard': (20, 636, 252, 754, 3), 'hit': (260, 636, 542, 754, 3), 'stun': (550, 636, 872, 754, 3), 'death': (18, 758, 874, 876, 6)}
CUTS = {'death': [(30, 128), (130, 228), (230, 336), (338, 456), (458, 650), (650, 872)]}
body, anc = {}, {}
for k, (x0, y0, x1, y1, n) in ROWS.items():
    r = char_cut(x0, y0, x1, y1, n=n, cuts=CUTS.get(k))
    body[k] = [im for im, _ in r]; anc[k] = [a for _, a in r]
rb = pack(body, os.path.join(out, 'dok/dok'), anc)
print({k: len(v) for k, v in rb.items()})
# ---- 이펙트 (오른쪽 판) ----
FX = {'slash': (906, 98, 1328, 192, [(908, 985), (985, 1052), (1052, 1138), (1138, 1232), (1232, 1326)]), 'wave': (1140, 226, 1320, 302), 'dash': (1326, 205, 1760, 302),
      'rain': (906, 309, 1334, 428, [(1236, 1290), (1290, 1334)]), 'blade': (1338, 309, 1760, 432, None, 6),
      'spin': (906, 466, 1334, 550, [(912, 1140), (1140, 1334)]), 'big': (1338, 440, 1760, 550),
      'circ': (906, 582, 1280, 654, [(908, 1028), (1028, 1150), (1150, 1280)]), 'judge': (1288, 566, 1760, 654, [(1292, 1415), (1415, 1535), (1535, 1640), (1640, 1760)]),
      'drop': (906, 662, 1312, 766, [(908, 1030), (1030, 1150), (1150, 1312)]), 'chain': (1312, 678, 1760, 763, [(1322, 1506), (1527, 1578), (1604, 1658)]),
      'burst': (906, 798, 1320, 874, [(916, 1010), (1010, 1100), (1100, 1186), (1186, 1320)]), 'dfx': (1328, 790, 1760, 876)}
fx = {}
for k, v in FX.items():
    x0, y0, x1, y1 = v[:4]; cuts = v[4] if len(v) > 4 else None; n = v[5] if len(v) > 5 else None
    fx[k] = fx_cut(x0, y0, x1, y1, cuts=cuts, n=n)
rf = pack(fx, os.path.join(out, 'dokfx/dokfx'))
print({k: len(v) for k, v in rf.items()})
