"""v10.30 업경의 심판수 반업수 아틀라스 — 사용자가 준 인게임 도트 시트(마젠타 배경)를 줄·칸으로 자르고 배경만 지운다 (도트는 그대로)
python3 tools/atlas/bny_build.py <시트.png> <출력 폴더(src/assets)>  →  bny/bny.webp + bny.json
줄: idle 6 · move 8 · atk 6 · judge 6(강공격·심판장, 결정 기둥이 붙어 있음) · hit 4 · death 6.  시트는 왼쪽을 봄."""
import sys, json, os
import numpy as np
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
A = np.asarray(Image.open(src).convert('RGB')).astype(int)
r, g, b = A[..., 0], A[..., 1], A[..., 2]
bg = (np.minimum(r, b) - g > 110)   # 마젠타 배경 (가장자리 번짐 포함)
fg = ~bg
ROWS = [('idle', 16, 185), ('move', 211, 357), ('atk', 381, 526), ('judge', 547, 705), ('hit', 724, 875), ('death', 901, 1054)]
def segs(y0, y1):
    col = fg[y0:y1].sum(0) > 0; s = []; x = 0; W = len(col)
    while x < W:
        if not col[x]: x += 1; continue
        x0 = x
        while x < W and col[x]: x += 1
        s.append([x0, x])
    m = []
    for a, c in s:   # 작은 조각(결정 끝 · 번짐)은 옆 칸에 붙인다
        if m and (c - a < 30 or a - m[-1][1] < 6): m[-1][1] = c
        else: m.append([a, c])
    return m
frames = {}; tiles = []
for name, y0, y1 in ROWS:
    L = segs(y0, y1); base = None; frames[name] = []
    for i, (a, c) in enumerate(L):
        sub = fg[y0:y1, a:c]; ys = np.where(sub.any(1))[0]; fy0, fy1 = y0 + ys[0], y0 + ys[-1] + 1
        crop = A[fy0:fy1, a:c]; al = np.where(fg[fy0:fy1, a:c], 255, 0)
        if base is None: base = fy1   # 줄 첫 칸의 발끝 = 이 줄의 바닥선
        top = al[:int((fy1 - fy0) * 0.5)] > 0; ax = float(np.mean(np.where(top)[1])) if top.any() else (c - a) / 2
        tiles.append((name, Image.fromarray(np.dstack([crop, al]).astype(np.uint8), 'RGBA'), ax, base - fy0))
    print(name, len(L))
# 한 장에 줄 단위로 붙인다
W = 0; H = 0; x = 0; y = 0; rowH = 0; cur = None; pos = []
for name, im, ax, ay in tiles:
    if name != cur: x = 0; y += rowH + (2 if cur else 0); rowH = 0; cur = name
    pos.append((name, x, y, im, ax, ay)); x += im.width + 2; rowH = max(rowH, im.height); W = max(W, x)
H = y + rowH
sheet = Image.new('RGBA', (W, H), (0, 0, 0, 0)); J = {}
for name, x, y, im, ax, ay in pos:
    sheet.paste(im, (x, y)); J.setdefault(name, []).append([x, y, im.width, im.height, round(ax, 1), int(ay)])
# 죄상 노출 파편 = 심판장 4번째 칸 왼쪽 결정 기둥 (고리 위까지, 열 단위로 가장 빈 곳에서 자름)
x, y, w, h, ax, ay = J['judge'][3]; a = np.asarray(sheet)[y:y + h, x:x + w, 3] > 0; a = a[:int(ay) - 14]
cs = a.sum(0); cut = 10 + int(np.argmin(cs[10:40])); rows = np.where(a[:, :cut].any(1))[0]
J['shard'] = [[x, y + int(rows[0]), cut, int(rows[-1] - rows[0] + 1), cut / 2, int(rows[-1] - rows[0] + 1)]]
os.makedirs(os.path.join(out, 'bny'), exist_ok=True)
sheet.save(os.path.join(out, 'bny', 'bny.webp'), lossless=True)
json.dump(J, open(os.path.join(out, 'bny', 'bny.json'), 'w'), separators=(',', ':'))
print(sheet.size, {k: len(v) for k, v in J.items()})
