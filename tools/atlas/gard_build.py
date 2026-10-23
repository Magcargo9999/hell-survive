"""v8.30 지하 16~20층 '악마 식물원' 세트: 바닥 타일 35칸 · 소품 · 보스맵.
시트(build/gard/): field_sheet.png(마계 식인 식물원 필드 타일셋 1448×1086) · boss_sheet.png(악마 식물원 보스맵 타일셋 1536×1024)
자르기 · 배경(흰색) 제거 · 배율만 — 재색칠 없음.
출력(src/assets/gard/): gfloor.webp(바닥 35칸 42px 띠) · gprops.webp/json(소품 사각형) · gmap.webp(예시 보스맵 932×970)"""
import numpy as np, json
from PIL import Image
from scipy import ndimage as ndi
IN = 'build/gard/'; OUT = 'src/assets/gard/'
F = np.array(Image.open(IN + 'field_sheet.png').convert('RGB')).astype(float)
# ---- 바닥 타일: 9열 × 4줄 (마지막 문양 칸 제외), 테두리 2px 안쪽을 42px로 ----
CX = [(18, 62), (64, 108), (109, 152), (155, 200), (203, 249), (251, 297), (299, 345), (347, 393), (396, 440)]
CY = [(142, 188), (190, 235), (238, 283), (285, 331)]
T = []
for r, (y0, y1) in enumerate(CY):
    for c, (x0, x1) in enumerate(CX):
        if r == 3 and c == 8: continue
        t = F[y0 + 2:y1 - 2, x0 + 2:x1 - 2].astype(np.uint8); T.append(np.array(Image.fromarray(t).resize((42, 42), Image.BOX)))
Image.fromarray(np.hstack(T)).save(OUT + 'gfloor.webp', lossless=True, method=6); print('tiles', len(T))
# ---- 소품: 흰 배경 위 덩어리 (번호는 build/gard/det2.py 미리보기 기준) ----
BOX = json.load(open(IN + 'boxes2.json'))
KEEP = list(range(0, 38)) + [39, 40, 41, 42, 43, 44, 45, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56] + [57, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75] + [76, 77, 87, 88, 89, 91]
WH = np.array([255., 255, 255])
def cut(b):
    _, x0, y0, x1, y1 = b; p = 3; c = F[y0 - p:y1 + p, x0 - p:x1 + p]
    d = np.abs(c - WH).max(-1); lo, hi = 22, 60
    a = np.clip((d - lo) / (hi - lo), 0, 1); core = d > hi; a = np.where(ndi.binary_dilation(core, iterations=1) & (d > lo), np.maximum(a, 0.85), a)
    a[:p] = 0; a[-p:] = 0; a[:, :p] = 0; a[:, -p:] = 0
    lab, n = ndi.label(a > 0.3, structure=np.ones((3, 3)))
    if n:
        sz = ndi.sum(a > 0.3, lab, range(1, n + 1)); keep = np.where(sz >= sz.max() * 0.08)[0] + 1; a[~np.isin(lab, keep)] = 0
    A = a[..., None]
    with np.errstate(divide='ignore', invalid='ignore'): u = np.where(A > 0.999, c, (c - WH * (1 - A)) / np.maximum(A, 1e-3))
    r = np.dstack([np.clip(u, 0, 255).astype(np.uint8), (a * 255).astype(np.uint8)])
    ys, xs = np.where(r[..., 3] > 8); return r[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
info = [cut(BOX[i]) for i in KEEP]
W = 1024; x = y = sh = 0; pos = []
for c in info:
    h, w = c.shape[:2]
    if x + w > W: x = 0; y += sh + 2; sh = 0
    pos.append((x, y)); x += w + 2; sh = max(sh, h)
at = np.zeros((y + sh, W, 4), np.uint8); rects = []
for c, (x, y) in zip(info, pos): h, w = c.shape[:2]; at[y:y + h, x:x + w] = c; rects.append([x, y, w, h])
Image.fromarray(at).save(OUT + 'gprops.webp', lossless=True, method=6); json.dump(rects, open(OUT + 'gprops.json', 'w'), separators=(',', ':'))
print('props', len(rects), at.shape)
# ---- 보스맵 (예시 보스맵 부분, 제목 띠 아래) ----
Image.open(IN + 'boss_sheet.png').convert('RGB').crop((8, 46, 940, 1016)).save(OUT + 'gmap.webp', quality=90, method=6)
