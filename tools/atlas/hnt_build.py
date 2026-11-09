"""v10.38 지하 40층 최종 마왕 '암전의 사냥꾼' 시트 9장(마젠타 배경) → src/assets/hnt/hnt.webp + hnt.json
쓰는 법: 받은 시트를 build/hnt/{walk,slash,throw,dash,hit,death,fx,lamp,trap}.png 로 두고 python3 tools/atlas/hnt_build.py
자르기 · 마젠타 배경 제거 · 축소만 (색·도트 수정 없음). 시트마다 그린 크기가 달라 서 있는 첫 칸 높이를 walk 첫 칸에 맞춘다.
json = {그룹: [[x,y,w,h,ax,ay], …]} — 몸 그룹은 (ax,ay) = 칸 가운데 · 발 바닥, 이펙트·소품 그룹은 그림 가운데(소품 lamp·trap은 바닥 가운데).
방향: walk·death(그리고 idle = walk 첫 칸)는 왼쪽을 보고, slash·throw·dash·hit는 오른쪽을 본다 (템플릿 HNT_LEFT)."""
import numpy as np, json, os
from PIL import Image
from scipy import ndimage as ndi
IN = 'build/hnt/'; OUT = 'src/assets/hnt/'; os.makedirs(OUT, exist_ok=True)
BASE = 0.5            # walk 시트 기준 저장 배율 (게임에서 ×HNT.K nearest)
REF = 234             # walk 첫 칸(서 있는 모습) 높이
def load(n): return np.array(Image.open(IN + n + '.png').convert('RGB')).astype(int)
def bgmask(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    bg = (r > 200) & (b > 200) & (g < 110); lab, n = ndi.label(bg)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(edge)) | ((r > 225) & (b > 225) & (g < 70))
    bg |= ndi.binary_dilation(bg, iterations=1) & (r > 170) & (b > 150) & (g < 150)
    return bg
def fgmask(a):
    fg = ~bgmask(a); l2, n2 = ndi.label(fg)
    if not n2: return fg, l2, [0]
    sz = ndi.sum(fg, l2, range(1, n2 + 1)); big = max(sz)
    return np.isin(l2, [i + 1 for i, v in enumerate(sz) if v >= max(20, big * 0.002)]), l2, sz
def runs(v, gap, minw):
    R = []; s = None
    for i, x in enumerate(v):
        if x and s is None: s = i
        if not x and s is not None: R.append([s, i]); s = None
    if s is not None: R.append([s, len(v)])
    M = []
    for q in R:
        if M and q[0] - M[-1][1] < gap: M[-1][1] = q[1]
        else: M.append(q)
    return [q for q in M if q[1] - q[0] >= minw]
def cut(a, x0, y0, x1, y1, sc, anchor):
    s = a[y0:y1, x0:x1]; fg, lab, sz = fgmask(s)
    ys, xs = np.where(fg); bx0, bx1, by0, by1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    if anchor == 'body':   # 칸 가운데 x(몸 덩어리 가운데) · 가장 큰 덩어리(몸)의 바닥
        L = int(np.argmax(sz)) + 1; yy, xx = np.where(lab == L); ay = yy.max() - by0
        y0b, y1b = yy.min(), yy.max(); sel = (yy > y0b + 0.6 * (y1b - y0b)) & (yy < y0b + 0.92 * (y1b - y0b))   # 아랫몸(망토·다리)의 가운데 — 위로 든 낫·뻗은 사슬에 끌려가지 않게
        ax = float(np.median(xx[sel])) - bx0
    elif anchor == 'foot': ax = (bx1 - bx0) / 2; ay = by1 - by0
    else: ax = (bx1 - bx0) / 2; ay = (by1 - by0) / 2   # 'c' · 'glow'
    sub = s[by0:by1, bx0:bx1].astype(np.uint8); m = fg[by0:by1, bx0:bx1]
    im = Image.fromarray(np.dstack([sub, (m * 255).astype(np.uint8)]), 'RGBA')
    if anchor == 'glow':   # 붉은 눈: 빛 번짐이 마젠타와 섞여 있어 배경색을 빼내 투명도로 (색은 그대로 되돌림 — 배경 제거)
        f = sub.astype(float) / 255; al = np.clip(np.maximum(1 - f[..., 2], f[..., 1]), 0, 1); al[~m] = 0
        M = np.array([1.0, 0.0, 1.0]); c = np.clip((f - (1 - al[..., None]) * M) / np.maximum(al[..., None], 1e-3), 0, 1)
        im = Image.fromarray(np.dstack([(c * 255).astype(np.uint8), (al * 255).astype(np.uint8)]), 'RGBA')
    im = im.resize((max(1, round(im.width * sc)), max(1, round(im.height * sc))), Image.BOX)
    return im, ax * sc, ay * sc
def body(n, n_exp, h0):
    a = load(n); fg = ndi.binary_opening(~bgmask(a), iterations=1)
    C = runs(fg.any(0), 10, 12); R = runs(fg.any(1), 30, 20)
    assert len(C) == n_exp, (n, C)
    y0, y1 = R[0][0] - 4, R[-1][1] + 4; sc = BASE * REF / h0
    out = []
    for i, (x0, x1) in enumerate(C):
        lo = (C[i - 1][1] + x0) // 2 if i else 0; hi = (x1 + C[i + 1][0]) // 2 if i + 1 < len(C) else a.shape[1]
        out.append(cut(a, lo, y0, hi, y1, sc, 'body'))
    return out
def rowcells(a, y0, y1, sc, anchor, gap=14, minw=10):
    fg = ndi.binary_opening(~bgmask(a[y0:y1]), iterations=1); C = runs(fg.any(0), gap, minw)
    return [cut(a, max(0, x0 - 3), y0, min(a.shape[1], x1 + 3), y1, sc, anchor) for x0, x1 in C]
G = {}
G['walk'] = body('walk', 8, 234)
G['idle'] = [G['walk'][0]]
G['slash'] = body('slash', 6, 261)
G['throw'] = body('throw', 6, 194)
G['dash'] = body('dash', 4, 310)
G['hit'] = body('hit', 3, 389)
G['death'] = body('death', 6, 293)
F = load('fx')
G['scy'] = rowcells(F, 60, 340, 0.5, 'c', gap=30)          # 회전하는 사슬 낫 4
G['chain'] = rowcells(F, 370, 565, 0.5, 'c', gap=16)       # 사슬 조각 8 (0~2 직선 · 3 사슬 머리 · 4~7 휜 사슬)
G['trail'] = [cut(F, x0, 610, x1, 840, 0.5, 'c') for x0, x1 in [(30, 180), (186, 375), (375, 600), (622, 930), (960, 1150), (1185, 1418)]]   # 베기 궤적 6 (2·3번째가 세로로 겹쳐 경계를 직접 지정)
G['eye'] = rowcells(F, 905, 990, 1.0, 'glow', gap=14)         # 붉은 눈 7
L = load('lamp')
G['lampB'] = rowcells(L, 30, 552, 0.42, 'foot', gap=40)     # 큰 등불 2 (0 꺼짐 · 1 켜짐)
hb = G['lampB'][0][0].height
sm = rowcells(L, 630, 1030, 1.0, 'foot', gap=20)            # 작은 등불 6 (일렁임) → 큰 등불 높이에 맞춤
G['lamp'] = []
for im, ax, ay in sm:
    k = hb / im.height; G['lamp'].append((im.resize((round(im.width * k), hb), Image.BOX), ax * k, ay * k))
T = load('trap')
G['trap'] = rowcells(T, 270, 730, 0.2, 'foot', gap=40)       # 올가미 함정 2 (0 열림 · 1 닫힘)
for k, v in G.items(): print(k, len(v), [im.size for im, _, _ in v][:3])
assert len(G['scy']) == 4 and len(G['chain']) == 8 and len(G['trail']) == 6 and len(G['eye']) == 7 and len(G['lampB']) == 2 and len(G['lamp']) == 6 and len(G['trap']) == 2
cells = [(k, im, ax, ay) for k, Lc in G.items() for (im, ax, ay) in Lc]
Wd = 2048; x = y = sh = 0; pos = []
for (_, im, _, _) in cells:
    w, h = im.size
    if x + w > Wd: x = 0; y += sh + 2; sh = 0
    pos.append((x, y)); x += w + 2; sh = max(sh, h)
at = Image.new('RGBA', (Wd, y + sh), (0, 0, 0, 0)); meta = {}
for (k, im, ax, ay), (px, py) in zip(cells, pos): at.alpha_composite(im, (px, py)); meta.setdefault(k, []).append([px, py, im.width, im.height, round(ax), round(ay)])
at.save(OUT + 'hnt.webp', lossless=True, method=6); json.dump(meta, open(OUT + 'hnt.json', 'w'), separators=(',', ':'))
pv = Image.new('RGBA', at.size, (30, 26, 40, 255)); pv.alpha_composite(at); pv.save('build/hnt/hnt_prev.png')
print(at.size, os.path.getsize(OUT + 'hnt.webp'))
