"""v10.40 철식 강철이 아틀라스 — 사용자 시트 3장을 자르고 배경만 지운다 (도트는 그대로)
python3 tools/atlas/stl_build.py <컨셉 시트(이족 인게임 칸)> <흑철룡 시트(마젠타)> <철 덩어리(마젠타)> <출력 폴더(src/assets)>
 → stl/stl.webp + stl.json
  이족(1·2페이즈, 정면·왼쪽을 봄): idle6 · move8 · atk6(철의 발톱) · bite6(철식의 물어뜯기) · pow5(강화) · hit4 · death6
    컨셉 시트 칸은 어두운 회색 배경 — 칸 가장자리와 이어진 무채색 회색만 투명 (스프라이트 테두리는 더 어둡거나 색이 있어 막힌다)
  흑철룡(3페이즈, 왼쪽을 봄): d_idle6 · d_move8 · d_atk6(브레스) · d_dash6 · d_roar4 · d_death6
  철 덩어리 chunk 1칸 (1/5로 줄임)"""
import sys, json, os
import numpy as np
from PIL import Image
from collections import deque
from scipy import ndimage

con, drg, chk, out = sys.argv[1:5]

def flood_bg(reg, isbg):
    h, w = isbg.shape; vis = np.zeros((h, w), bool); q = deque()
    for y in range(h):
        for x in (0, w - 1):
            if isbg[y, x] and not vis[y, x]: vis[y, x] = 1; q.append((y, x))
    for x in range(w):
        for y in (0, h - 1):
            if isbg[y, x] and not vis[y, x]: vis[y, x] = 1; q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and isbg[ny, nx] and not vis[ny, nx]: vis[ny, nx] = 1; q.append((ny, nx))
    return vis

tiles = []   # (group, rgba Image)
# --- 이족 (컨셉 시트 칸) ---
C = np.asarray(Image.open(con).convert('RGB')).astype(int)
ROWS = [
    ('idle', 508, 585, [(18, 122), (123, 229), (230, 336), (337, 443), (445, 551), (553, 660)]),
    ('move', 508, 585, [(684, 773), (774, 862), (864, 952), (954, 1042), (1044, 1134), (1136, 1227), (1228, 1321), (1323, 1431)]),
    ('atk', 639, 715, [(21, 135), (136, 249), (251, 365), (367, 481), (482, 597), (598, 716)]),
    ('bite', 639, 715, [(742, 862), (863, 977), (978, 1091), (1093, 1197), (1198, 1311), (1312, 1430)]),
    ('pow', 772, 853, [(21, 134), (135, 246), (247, 357), (358, 472), (473, 593)]),
    ('hit', 772, 853, [(616, 694), (696, 769), (770, 837), (839, 903)]),
    ('death', 772, 853, [(925, 1001), (1003, 1079), (1081, 1159), (1160, 1240), (1241, 1320), (1321, 1429)]),
]
for name, y0, y1, cells in ROWS:
    for a, b in cells:
        reg = C[y0:y1, a + 1:b - 1]; mx = reg.max(2); mn = reg.min(2)
        isbg = (mx - mn <= 9) & (mx >= 11) & (mx <= 62)
        bg = flood_bg(reg, isbg)
        al = np.where(bg, 0, 255).astype(np.uint8)
        al[mx < 6] = np.where(bg[mx < 6], 0, al[mx < 6])
        lab, nlab = ndimage.label(al > 0)   # 칸 배경 그라데이션에서 남은 외톨이 점(8px 미만)만 지운다
        if nlab: sz = ndimage.sum(al > 0, lab, range(1, nlab + 1)); al[np.isin(lab, np.where(sz < 8)[0] + 1)] = 0
        tiles.append((name, np.dstack([reg, al]).astype(np.uint8)))
# --- 흑철룡 (마젠타) ---
D = np.asarray(Image.open(drg).convert('RGB')).astype(int)
dbg = (np.minimum(D[..., 0], D[..., 2]) - D[..., 1] > 110); dfg = ~dbg
rows = dfg.sum(1) > 0; bands = []; y = 0
while y < len(rows):
    if not rows[y]: y += 1; continue
    a = y
    while y < len(rows) and rows[y]: y += 1
    if y - a > 30: bands.append((a, y))
DN = ['d_idle', 'd_move', 'd_atk', 'd_dash', 'd_roar', 'd_death']
DCNT = {'d_idle': 6, 'd_move': 8, 'd_atk': 6, 'd_dash': 6, 'd_roar': 4, 'd_death': 6}
for (y0, y1), name in zip(bands, DN):
    col = dfg[y0:y1].sum(0) > 0; s = []; x = 0
    while x < len(col):
        if not col[x]: x += 1; continue
        a = x
        while x < len(col) and col[x]: x += 1
        s.append([a, x])
    m = []; i = 0
    while i < len(s):   # 작은 조각(불꽃·파편)은 바로 뒤 칸에 붙인다 (뒤가 멀면 앞 칸에)
        a, b = s[i]
        if b - a < 40:
            if i + 1 < len(s) and s[i + 1][0] - b < 40: s[i + 1][0] = a
            elif m: m[-1][1] = b
            i += 1; continue
        m.append([a, b]); i += 1
    need = DCNT[name]; colsum = dfg[y0:y1].sum(0)
    while len(m) < need:   # 붙어 있는 두 칸은 가운데 가장 빈 세로줄에서 나눈다
        k = max(range(len(m)), key=lambda j: m[j][1] - m[j][0]); a, b = m[k]; lo, hi = a + (b - a) // 3, b - (b - a) // 3
        c = lo + int(np.argmin(colsum[lo:hi])); m[k:k + 1] = [[a, c], [c, b]]
    for a, b in m:
        tiles.append((name, np.dstack([D[y0:y1, a:b], np.where(dfg[y0:y1, a:b], 255, 0)]).astype(np.uint8)))
# --- 철 덩어리 ---
K = np.asarray(Image.open(chk).convert('RGB')).astype(int)
kfg = ~(np.minimum(K[..., 0], K[..., 2]) - K[..., 1] > 110)
ys, xs = np.where(kfg); K2 = Image.fromarray(np.dstack([K, np.where(kfg, 255, 0)]).astype(np.uint8), 'RGBA').crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
K2 = K2.resize((K2.width // 5, K2.height // 5), Image.NEAREST)
tiles.append(('chunk', np.asarray(K2)))

# 칸마다 알파 경계로 다듬고, 기준점(ax = 위쪽 절반 무게중심 · ay = 아래 끝)을 잡아 한 장에 붙인다
packed = []
for name, t in tiles:
    al = t[..., 3] > 0; ys, xs = np.where(al)
    if not len(ys): continue
    t = t[ys.min():ys.max() + 1, xs.min():xs.max() + 1]; h, w = t.shape[:2]; top = t[:max(1, h // 2), :, 3] > 0
    ax = float(np.mean(np.where(top)[1])) if top.any() else w / 2
    packed.append((name, Image.fromarray(t, 'RGBA'), round(ax, 1), h))
W = 0; x = 0; y = 0; rowH = 0; cur = None; pos = []
for name, im, ax, ay in packed:
    grp = name.split('_')[0] if name.startswith('d_') else 'b'
    if name != cur and (x + im.width > 1500 or cur is None or name.startswith('d_') != (cur or '').startswith('d_') or name in ('chunk',)):
        x = 0; y += rowH + (2 if cur else 0); rowH = 0
    cur = name
    pos.append((name, x, y, im, ax, ay)); x += im.width + 2; rowH = max(rowH, im.height); W = max(W, x)
H = y + rowH
sheet = Image.new('RGBA', (W, H), (0, 0, 0, 0)); J = {}
for name, x, y, im, ax, ay in pos:
    sheet.paste(im, (x, y)); J.setdefault(name, []).append([x, y, im.width, im.height, ax, ay])
os.makedirs(os.path.join(out, 'stl'), exist_ok=True)
sheet.save(os.path.join(out, 'stl', 'stl.webp'), lossless=True)
json.dump(J, open(os.path.join(out, 'stl', 'stl.json'), 'w'), separators=(',', ':'))
print(sheet.size, {k: len(v) for k, v in J.items()})
