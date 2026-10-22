"""v7.10 지하 11~15층 '어인섬' 세트: 바닥 타일 10칸 · 소품 16종 · 어인/게 악마(잡몹 10종) · 보스맵.
시트(실행 폴더): map_sheet.png(신규 맵 타일셋) · fish_sheet.png(물고기 악마) · crab_sheet.png(게 악마) · bmap_sheet.png(보스맵 타일셋+예시 보스맵)
자르기 · 배경 제거 · 배율(소품·잡몹 0.6~0.72배 축소)만 — 재색칠 없음.
출력(src/assets/sea/): sfloor.webp(바닥 10칸 42px 띠) · sprops.webp/json · smob.webp(124×124 칸 · 10종 × 4프레임) · smap.webp(예시 보스맵 612×779)"""
import numpy as np, json, sys
sys.path.insert(0, 'tools/atlas')
from PIL import Image
from scipy import ndimage as ndi
OUT = 'src/assets/sea/'; IN = 'build/sea/'
def rgb(f): return np.array(Image.open(IN + f).convert('RGB')).astype(float)
def clean(a, minsz=6):
    m = a > 0; lab, n = ndi.label(m, structure=np.ones((3, 3)))
    if n: sz = ndi.sum(m, lab, range(1, n + 1)); a[np.isin(lab, np.where(sz < minsz)[0] + 1)] = 0
    return a
def alpha(c, BG, lo, hi):
    d = np.abs(c - BG).max(-1); core = d > hi; near = ndi.binary_dilation(core, iterations=1)
    return clean(np.where(d <= lo, 0.0, np.where(core | near, 1.0, (d - lo) / (hi - lo))))
def unblend(c, a, BG):
    A = np.clip(a, 0, 1)[..., None]
    with np.errstate(divide='ignore', invalid='ignore'): u = np.where(A > 0.999, c, (c - BG * (1 - A)) / np.maximum(A, 1e-3))
    return np.dstack([np.clip(u, 0, 255).astype(np.uint8), (np.clip(a, 0, 1) * 255).astype(np.uint8)])
def trim(r):
    ys, xs = np.where(r[..., 3] > 8); return r[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
def resize(r, k): return np.array(Image.fromarray(r).resize((max(1, round(r.shape[1] * k)), max(1, round(r.shape[0] * k))), Image.LANCZOS))
# ---- 바닥 타일 10칸 (지형 줄, 테두리 4px 안쪽을 42px로 줄임) ----
M = rgb('map_sheet.png')
TX = [(21, 91), (97, 166), (173, 243), (248, 319), (324, 392), (400, 472), (481, 559), (568, 643), (651, 725), (734, 815)]
T = []
for x0, x1 in TX:
    t = M[195:261, x0 + 3:x1 - 3]; T.append(np.array(Image.fromarray(t.astype(np.uint8)).resize((42, 42), Image.BOX)))
Image.fromarray(np.hstack(T)).save(OUT + 'sfloor.webp', lossless=True, method=6)
# ---- 소품 16종 (센 배경 제거 · 0.6배) ----
BG = np.array([2, 12, 25.])
PROPS = [(20, 518, 110, 592), (110, 518, 212, 592), (215, 518, 302, 592), (305, 508, 378, 592), (385, 515, 478, 592), (480, 525, 590, 592), (590, 520, 722, 592), (722, 510, 822, 594),
         (18, 620, 100, 725), (108, 618, 258, 728), (256, 618, 332, 728), (334, 622, 378, 728), (383, 622, 442, 728), (452, 622, 532, 728), (540, 618, 722, 730), (722, 618, 822, 730)]
info = []
for x0, y0, x1, y1 in PROPS:
    pad = 4; c = M[y0 - pad:y1 + pad, x0 - pad:x1 + pad]; a = alpha(c, BG, 16, 40)
    a[:pad] = 0; a[-pad:] = 0; a[:, :pad] = 0; a[:, -pad:] = 0
    lab, n = ndi.label(a > 0.3, structure=np.ones((3, 3)))
    if n:
        sz = ndi.sum(a > 0.3, lab, range(1, n + 1)); keep = np.where(sz >= max(30, sz.max() * 0.04))[0] + 1
        a[~np.isin(lab, keep)] = 0
    info.append(resize(trim(unblend(c, a, BG)), 0.6))
W = 1024; x = y = sh = 0; pos = []
for c in info:
    h, w = c.shape[:2]
    if x + w > W: x = 0; y += sh + 2; sh = 0
    pos.append((x, y)); x += w + 2; sh = max(sh, h)
at = np.zeros((y + sh, W, 4), np.uint8); rects = []
for c, (x, y) in zip(info, pos): h, w = c.shape[:2]; at[y:y + h, x:x + w] = c; rects.append([x, y, w, h])
Image.fromarray(at).save(OUT + 'sprops.webp', lossless=True, method=6); json.dump(rects, open(OUT + 'sprops.json', 'w'), separators=(',', ':'))
print('props', len(rects), at.shape, [(r[2], r[3]) for r in rects])
# ---- 잡몹: 작은 5종(1프레임) + 보통 5종(걷기 4프레임 · 0.72배) → 124×124 칸 ----
CW, CH = 124, 124
F = np.array(Image.open(IN + 'fish_sheet.png').convert('RGBA'))
def fish(box):
    x0, y0, x1, y1 = box; c = F[y0 - 3:y1 + 3, x0 - 3:x1 + 3].copy(); c[..., 3] = np.where(c[..., 3] > 128, 255, 0)
    lab, n = ndi.label(c[..., 3] > 0, structure=np.ones((3, 3))); sz = ndi.sum(c[..., 3] > 0, lab, range(1, n + 1)); c[lab != np.argmax(sz) + 1] = 0
    return trim(c)
C = rgb('crab_sheet.png')
def crab(box):
    x0, y0, x1, y1 = box; c = C[y0 - 4:y1 + 4, x0 - 4:x1 + 4]; BGc = np.array([252., 252, 252]); a = alpha(c, BGc, 55, 85)
    lab, n = ndi.label(a > 0.3, structure=np.ones((3, 3))); sz = ndi.sum(a > 0.3, lab, range(1, n + 1)); a[lab != np.argmax(sz) + 1] = 0
    a = np.maximum(a, ndi.binary_fill_holes(a > 0.3).astype(float))   # 흰 이빨·눈이 배경색과 같아 구멍이 났다 → 메움
    return trim(unblend(c, a, BGc))
SM = [(297, 185, 392, 271), (307, 412, 414, 521), (297, 683, 401, 790), (314, 918, 426, 1010)]
MID = [[(440, 116, 573, 260), (596, 124, 733, 263), (749, 128, 896, 263), (911, 115, 1058, 263)],
       [(440, 355, 590, 517), (598, 363, 744, 517), (754, 363, 907, 521), (922, 362, 1071, 522)],
       [(441, 614, 599, 789), (602, 623, 744, 789), (759, 617, 915, 791), (922, 623, 1069, 789)],
       [(440, 883, 599, 1015), (607, 893, 749, 1015), (754, 886, 907, 1015), (913, 889, 1085, 1015)]]
CSM = (329, 107, 456, 220); CMID = [(498, 90, 654, 225), (666, 90, 803, 230), (814, 86, 965, 230), (978, 88, 1128, 225)]
species = [[fish(b)] * 4 for b in SM] + [[resize(crab(CSM), 0.75)] * 4] + [[resize(fish(b), 0.66) for b in row] for row in MID] + [[resize(crab(b), 0.66) for b in CMID]]
sheet = np.zeros((CH * 4, CW * len(species), 4), np.uint8); nh = []
for i, fr in enumerate(species):
    for k, c in enumerate(fr):
        h, w = c.shape[:2]; assert h <= CH - 2 and w <= CW, (i, k, h, w)
        ox = i * CW + (CW - w) // 2; oy = k * CH + CH - 2 - h; sheet[oy:oy + h, ox:ox + w] = c
    nh.append(max(c.shape[0] for c in fr))
Image.fromarray(sheet).save(OUT + 'smob.webp', lossless=True, method=6); print('mob nh', nh, [[c.shape[:2] for c in fr][:1] for fr in species])
# ---- 보스맵 (예시 보스맵 부분) ----
Image.open(IN + 'bmap_sheet.png').convert('RGB').crop((820, 285, 1432, 1064)).save(OUT + 'smap.webp', lossless=True, method=6)
