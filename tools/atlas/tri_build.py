"""v10.34 ∞ 챌린지 전용 마왕 '무한의 삼위일체' 시트 7장(마젠타 배경) → src/assets/tri/tri.webp + tri.json
시트: build/tri/{idle,summon,dash,move,phase,death,fx}.png. 자르기 · 마젠타 배경 제거 · 0.5배 축소만 (색·도트 수정 없음).
json = {그룹: [[x,y,w,h,ax,ay], …]} — 몸 그룹은 (ax,ay) = 칸 가운데 · 몸 바닥, 이펙트 그룹은 그림 가운데.
몸 시트는 오른쪽을 본다(돌진 줄의 바람 줄기가 왼쪽 뒤로 남음)."""
import numpy as np, json, os
from PIL import Image
from scipy import ndimage as ndi
IN = 'build/tri/'; OUT = 'src/assets/tri/'; os.makedirs(OUT, exist_ok=True); SC = 0.5
def mask(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    bg = (r > 200) & (b > 200) & (g < 110); lab, n = ndi.label(bg)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(edge)) | ((r > 225) & (b > 225) & (g < 70))
    bg |= ndi.binary_dilation(bg, iterations=1) & (r > 170) & (b > 150) & (g < 150)
    fg = ~bg; l2, n2 = ndi.label(fg); sz = ndi.sum(fg, l2, range(1, n2 + 1))
    big = max(sz) if len(sz) else 0
    return np.isin(l2, [i + 1 for i, v in enumerate(sz) if v >= max(25, big * 0.002)]), l2, sz
def cut(S, x0, y0, x1, y1, body):
    a = S[y0:y1, x0:x1]; fg, lab, sz = mask(a)
    ys, xs = np.where(fg); bx0, bx1, by0, by1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    if body:   # 기준점: 칸 가운데 x · 가장 큰 덩어리(몸)의 바닥
        L = int(np.argmax(sz)) + 1; yy = np.where(lab == L)[0]; ax = (x1 - x0) / 2 - bx0; ay = yy.max() - by0
    else: ax = (bx1 - bx0) / 2; ay = (by1 - by0) / 2
    sub = a[by0:by1, bx0:bx1].astype(np.uint8); m = fg[by0:by1, bx0:bx1]
    im = Image.fromarray(np.dstack([sub, (m * 255).astype(np.uint8)]), 'RGBA')
    im = im.resize((max(1, round(im.width * SC)), max(1, round(im.height * SC))), Image.BOX)
    return im, ax * SC, ay * SC
def grid(n, rows, cols):
    S = np.array(Image.open(IN + n + '.png').convert('RGB')).astype(int); W = S.shape[1]; out = []
    for (y0, y1) in rows:
        for c in range(cols): out.append(cut(S, int(c * W / cols), y0, int((c + 1) * W / cols), y1, True))
    return out
G = {}
G['idle'] = grid('idle', [(152, 552), (598, 1000)], 4)
G['move'] = grid('move', [(152, 554), (596, 1000)], 4)
G['phase'] = grid('phase', [(150, 556), (586, 1044)], 4)
G['summon'] = grid('summon', [(138, 558), (570, 1050)], 3)
G['dash'] = grid('dash', [(148, 556), (600, 1036)], 3)
G['death'] = grid('death', [(140, 566), (600, 1022)], 3)
F = np.array(Image.open(IN + 'fx.png').convert('RGB')).astype(int)
FX = {'slash': (127, 283, [(55, 252), (290, 492), (512, 710), (722, 935), (948, 1172), (1182, 1414)]),
      'erupt': (284, 416, [(40, 196), (216, 372), (386, 548), (560, 738), (749, 944), (949, 1174), (1176, 1424)]),
      'spike': (418, 588, [(40, 168), (198, 344), (366, 527), (550, 744), (766, 951), (979, 1174), (1212, 1422)]),
      'rune': (588, 766, [(40, 168), (194, 358), (381, 570), (594, 822), (846, 1099), (1127, 1420)]),
      'bomb': (766, 895, [(49, 138), (193, 297), (338, 477), (498, 669), (671, 895), (901, 1151), (1176, 1396)]),
      'vortex': (893, 1080, [(40, 189), (215, 407), (414, 634), (651, 883), (889, 1137), (1138, 1418)])}
for k, (y0, y1, xs) in FX.items(): G[k] = [cut(F, a, y0, b, y1, False) for a, b in xs]
cells = [(k, im, ax, ay) for k, L in G.items() for (im, ax, ay) in L]
W = 2048; x = y = sh = 0; pos = []
for (_, im, _, _) in cells:
    w, h = im.size
    if x + w > W: x = 0; y += sh + 2; sh = 0
    pos.append((x, y)); x += w + 2; sh = max(sh, h)
at = Image.new('RGBA', (W, y + sh), (0, 0, 0, 0)); meta = {}
for (k, im, ax, ay), (px, py) in zip(cells, pos): at.alpha_composite(im, (px, py)); meta.setdefault(k, []).append([px, py, im.width, im.height, round(ax), round(ay)])
at.save(OUT + 'tri.webp', lossless=True, method=6); json.dump(meta, open(OUT + 'tri.json', 'w'), separators=(',', ':'))
pv = Image.new('RGBA', at.size, (40, 90, 70, 255)); pv.alpha_composite(at); pv.save('build/tri/tri_prev.png')
print(at.size, {k: len(v) for k, v in meta.items()})
