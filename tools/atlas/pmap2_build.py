"""v10.59 10지옥 '판데모니움' 보스맵 다시 만들기 — 예시 보스맵(7. EXAMPLE BOSS MAP) 구조를 받은 조각으로 원래 크기 그대로 조합 (예시 그림을 늘리지 않는다)
쓰는 법: build/pan/boss.png(보스맵 조각 시트) · build/pan/tiles.png 를 두고 python3 tools/atlas/pmap2_build.py
→ src/assets/pan/pmap.webp (게임에서 ×2 nearest) + build/pan/pmap2.json (걷는 곳 다각형 등, 템플릿 IMAP_PAN에 붙여 넣음)
자르기 · 마젠타 배경 제거 · 이어 붙이기 · 좌우 뒤집기 · 모양대로 오려 내기(바닥 타일)만 — 색·도트 수정 없음.
구성 (예시 그대로): 가운데 팔각 광장(룬 마법진) · 8방향 길 — 위 계단 → 옥좌 단상 · 아래 계단 → 아래 단상(화로 둘) → 출구 계단과 악마 아치
 · 좌우 아치 다리 → 옆 단상 · 대각 4방향 다리 → 모서리 단상(화로·깃발) · 바깥은 심연(흰 빛줄기)과 떠 있는 절벽 · 위쪽 고딕 성벽·첨탑 · 사슬"""
import numpy as np, os, json, math
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
import cv2
S = Image.open('build/pan/boss.png').convert('RGB'); A = np.array(S).astype(int); OUT = 'src/assets/pan/'
def bgmask(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return ((r - g > 60) & (b - g > 60)) | ((r > 180) & (b > 180) & (g < 120))
def piece(box, big=False):
    x0, y0, x1, y1 = box; s = A[y0:y1, x0:x1]; fg = ~bgmask(s); fg = ndi.binary_opening(fg, iterations=1); L, n = ndi.label(fg)
    if n:
        sz = ndi.sum(fg, L, range(1, n + 1))
        fg = (L == int(np.argmax(sz)) + 1) if big else np.isin(L, [i + 1 for i, v in enumerate(sz) if v >= 25])
    for _ in range(2):
        r, g, b = s[..., 0], s[..., 1], s[..., 2]; edge = fg & ~ndi.binary_erosion(fg); fg = fg & ~(edge & (r - g > 22) & (b - g > 22))
    ys, xs = np.where(fg); bx0, bx1, by0, by1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    return Image.fromarray(np.dstack([s[by0:by1, bx0:bx1].astype(np.uint8), (fg[by0:by1, bx0:bx1] * 255).astype(np.uint8)]), 'RGBA')
FC = [(10, 66), (69, 125), (128, 186), (189, 246), (249, 302)]; FR = [(41, 104), (107, 165), (169, 227), (230, 294)]; TS = 56
def tile(r, c, ins=2): (x0, x1), (y0, y1) = FC[c], FR[r]; return S.crop((x0 + ins, y0 + ins, x1 - ins, y1 - ins)).resize((TS, TS), Image.BOX).convert('RGBA')
P = {
  'cliffA': [317, 38, 368, 110], 'cliffB': [369, 37, 428, 111], 'cliffC': [430, 37, 535, 109], 'cliffD': [536, 37, 611, 111],
  'rockA': [705, 36, 758, 100], 'rockB': [757, 37, 806, 108], 'rockC': [810, 37, 850, 108],
  'wallA': [317, 110, 466, 221], 'wallB': [472, 112, 620, 221], 'wallC': [625, 118, 707, 221], 'wallD': [318, 229, 478, 297], 'stairs': [481, 228, 550, 297],
  'gateW': [555, 229, 615, 297], 'arches': [626, 228, 742, 297], 'colm': [818, 177, 852, 257], 'rail': [745, 235, 850, 297],
  'q0': [8, 346, 107, 449], 'q1': [113, 346, 212, 449], 'q2': [8, 454, 107, 555], 'q3': [113, 454, 212, 555], 'sigil': [212, 343, 350, 528],
  'arch': [364, 340, 541, 488], 'shrL': [545, 340, 601, 450], 'throne': [569, 340, 800, 523], 'shrR': [774, 340, 850, 472],
  'pillar': [202, 517, 267, 670], 'plat': [346, 490, 440, 562], 'platS': [274, 528, 344, 580], 'post': [440, 488, 478, 558],
  'chain': [488, 518, 557, 617], 'banP': [560, 523, 641, 667], 'spire': [760, 481, 847, 670], 'bridL': [15, 544, 107, 613], 'bridR': [115, 544, 206, 613],
  'bridge': [8, 606, 212, 676], 'brzA': [275, 587, 331, 670], 'brzB': [344, 566, 404, 670], 'brzC': [416, 562, 486, 670], 'altar': [499, 610, 605, 667], 'cage': [640, 560, 695, 667],
  'fenceA': [16, 719, 86, 783], 'fenceB': [97, 720, 147, 779], 'fenceC': [155, 721, 246, 776], 'fenceD': [249, 718, 311, 776],
  'ban1': [473, 712, 528, 808], 'ban2': [533, 712, 616, 782], 'skulls': [74, 783, 142, 881], 'ruin': [184, 784, 274, 882], 'obel': [682, 778, 762, 890], 'ribs': [763, 803, 851, 876],
}
G = {k: piece(v, big=k in ('throne', 'arch', 'spire', 'pillar', 'sigil')) for k, v in P.items()}
abyss = S.crop((12, 943, 61, 994)).convert('RGBA')
NW, NH = 2100, 2900
CX, CY = 1050, 1450
R, C = 520, 215; X0, X1, Y0, Y1 = CX - R, CX + R, CY - R, CY + R
def octo(cx, cy, hw, hh, c): return [(cx - hw + c, cy - hh), (cx + hw - c, cy - hh), (cx + hw, cy - hh + c), (cx + hw, cy + hh - c), (cx + hw - c, cy + hh), (cx - hw + c, cy + hh), (cx - hw, cy + hh - c), (cx - hw, cy - hh + c)]
def rrect(x0, y0, x1, y1, w):   # (x0,y0)→(x1,y1) 방향의 폭 w 띠
    dx, dy = x1 - x0, y1 - y0; L = math.hypot(dx, dy); nx, ny = -dy / L * w / 2, dx / L * w / 2
    return [(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)]
# ---- 걷는 곳 ----
TPY, TPHW, TPHH = 575, 330, 185            # 옥좌 단상
BPY, BPHW, BPHH = 2330, 300, 140           # 아래 단상
SPX, SPHW, SPHH = 800, 140, 120            # 옆 단상 (가운데에서 ±800)
DK = 412; CPD, CPR = 650, 150              # 대각: 광장 대각 변 가운데(±412) → 모서리 단상 가운데(±650)
AW = 150                                    # 길 폭
REG = {
  'plaza': octo(CX, CY, R, R, C),
  'throne': octo(CX, TPY, TPHW, TPHH, 90), 'armN': [(CX - AW / 2, TPY + TPHH - 10), (CX + AW / 2, TPY + TPHH - 10), (CX + AW / 2, Y0 + 10), (CX - AW / 2, Y0 + 10)],
  'bottom': octo(CX, BPY, BPHW, BPHH, 80), 'armS': [(CX - AW / 2, Y1 - 10), (CX + AW / 2, Y1 - 10), (CX + AW / 2, BPY - BPHH + 10), (CX - AW / 2, BPY - BPHH + 10)],
  'exit': [(CX - 72, BPY + BPHH - 10), (CX + 72, BPY + BPHH - 10), (CX + 72, NH - 30), (CX - 72, NH - 30)],
}
for s in (-1, 1):
    REG['side%d' % s] = octo(CX + s * SPX, CY, SPHW, SPHH, 45)
    a0, a1 = (X1 - 10, CX + SPX - SPHW + 10) if s > 0 else (CX - SPX + SPHW - 10, X0 + 10)
    REG['armE%d' % s] = [(a0, CY - 60), (a1, CY - 60), (a1, CY + 60), (a0, CY + 60)]
    for t in (-1, 1):
        REG['corner%d%d' % (s, t)] = octo(CX + s * CPD, CY + t * CPD, CPR, CPR * 0.85, 55)
        REG['diag%d%d' % (s, t)] = rrect(CX + s * (DK - 30), CY + t * (DK - 30), CX + s * (CPD - 60), CY + t * (CPD - 60), 140)
def mask_of(keys):
    m = Image.new('L', (NW, NH), 0); d = ImageDraw.Draw(m)
    for k in keys: d.polygon(REG[k], fill=255)
    return m
WALK = mask_of(REG.keys()); WM = np.array(WALK) > 0
cv = Image.new('RGBA', (NW, NH), (0, 0, 0, 0))
def put(k, x, y, ax=0.5, ay=1.0, flip=False, img=None):
    im = img if img is not None else (G[k] if isinstance(k, str) else k)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    cv.alpha_composite(im, (int(round(x - im.width * ax)), int(round(y - im.height * ay))))
rnd = np.random.RandomState(11)
# 1) 먼 배경: 떠 있는 바위 · 양옆 고딕 성벽 · 위쪽 첨탑 (걷는 곳 뒤)
for (x, y, k) in [(120, 380, 'rockA'), (1980, 330, 'rockB'), (80, 1180, 'rockC'), (2030, 1200, 'rockA'), (180, 2050, 'rockB'), (1930, 2080, 'rockC'),
                  (90, 2600, 'cliffA'), (2010, 2620, 'cliffB'), (330, 2750, 'rockA'), (1780, 2760, 'rockB'), (420, 1980, 'rockC'), (1680, 960, 'rockA')]: put(k, x, y)
for s in (-1, 1):   # 옥좌 단상 양옆 뒤 고딕 성벽 + 첨탑 + 화로탑 (예시 위쪽 양 끝)
    f = s > 0
    put('wallA', CX + s * 470, TPY - 60, flip=f); put('wallB', CX + s * 640, TPY - 30, flip=f); put('spire', CX + s * 800, TPY + 10, flip=f)
    put('wallD', CX + s * 900, TPY + 150, flip=f); put('arches', CX + s * 930, CY - 230, flip=f); put('arches', CX + s * 930, CY + 330, flip=f)
    put('wallC', CX + s * 960, CY + 720, flip=f); put('spire', CX + s * 950, BPY + 40, flip=f)
put('wallB', CX - 120, TPY - TPHH + 10); put('wallB', CX + 120, TPY - TPHH + 10, flip=True)
# 2) 떠 있는 절벽: 걷는 곳 아래 가장자리마다 (바닥보다 먼저 — 윗면이 바닥에 덮인다) + 그 밑 흰 빛줄기
cl = ['cliffC', 'cliffA', 'cliffD', 'cliffB']; FALLS = []
for x in range(10, NW - 10, 38):
    col = WM[:, x]; ys = np.where(col[:-1] & ~col[1:])[0]
    for y in ys:
        if y > NH - 60: continue
        k = cl[(x // 38 + y // 50) % 4]; put(k, x, y + 48); FALLS.append((x, y))
top = cv.copy(); cv = Image.new('RGBA', (NW, NH), (9, 9, 11, 255))
def fall(x, y, n, a0=200):
    im = abyss.resize((abyss.width, abyss.height * n), Image.NEAREST); al = np.array(im.split()[3]).astype(float)
    f = np.linspace(1, 0, im.height)[:, None] ** 1.3 * np.sin(np.linspace(0, np.pi, im.width))[None, :] ** 0.7; im.putalpha(Image.fromarray((al * f * a0 / 255).astype(np.uint8)))
    cv.alpha_composite(im, (int(x), int(y)))
for i, (x, y) in enumerate(FALLS):
    if i % 2 == 0: fall(x - abyss.width / 2, y + 60, 4 + i % 5)
for (x, y) in [(70, 900), (2000, 880), (150, 1700), (1920, 1720), (260, 2400), (1800, 2420), (60, 300), (2020, 260)]: fall(x, y, 5, 130)
cv.alpha_composite(top)
# 3) 바닥: 광장 = 밝은 판석 테두리 + 가운데 원 안 어두운(붉은 금) 판석 · 길 = 밝은 판석 · 단상 = 어두운 판석
light = [tile(0, 1), tile(0, 3), tile(0, 1).transpose(Image.FLIP_LEFT_RIGHT)]
dark = [tile(0, 0), tile(0, 0).transpose(Image.FLIP_LEFT_RIGHT), tile(0, 0), tile(1, 4)]
def layer(ts, seed):
    L = Image.new('RGBA', (NW, NH)); r = np.random.RandomState(seed)
    for y in range(0, NH, TS):
        for x in range(0, NW, TS): L.alpha_composite(ts[r.randint(len(ts))], (x, y))
    return L
LT, DKL = layer(light, 3), layer(dark, 5)
lt = LT.copy(); lt.putalpha(WALK); cv.alpha_composite(lt)
dm = mask_of(['plaza', 'throne', 'bottom'] + [k for k in REG if k.startswith('corner') or k.startswith('side')])
md = Image.new('L', (NW, NH), 0); ImageDraw.Draw(md).ellipse((CX - 400, CY - 400, CX + 400, CY + 400), fill=255)
dmk = dm
dk = DKL.copy(); dk.putalpha(dmk); cv.alpha_composite(dk)
for (x, y) in [(X0 + 60, CY - 120), (X1 - 116, CY + 60), (CX - 300, Y1 - 90), (CX + 240, Y0 + 40), (CX - 250, TPY - 40), (CX + 200, TPY + 20)]: cv.alpha_composite(tile(3, 1), (x, y))
# 4) 광장 장식: 가운데 큰 룬 원(네 조각) + 그 안 가시 마법진 · 8방향 룬 판
q = [G['q0'], G['q1'], G['q2'], G['q3']]; g = 120   # 네 조각을 바깥으로 벌려 큰 룬 고리 (사이 틈 = 8방향 길과 맞닿는 살)
put(q[0], CX - g, CY - g, 1, 1); put(q[1], CX + g, CY - g, 0, 1); put(q[2], CX - g, CY + g, 1, 0); put(q[3], CX + g, CY + g, 0, 0)
put('sigil', CX, CY, 0.5, 0.5)
for i in range(8):
    a = i * math.pi / 4
    for rr, t in ((175, tile(1, 1) if i % 2 == 0 else tile(1, 3)), (390, tile(2, 2) if i % 2 == 0 else tile(1, 1))):
        cv.alpha_composite(t, (int(CX + math.cos(a) * rr - TS / 2), int(CY + math.sin(a) * rr - TS / 2)))
# 5) 위: 계단 → 옥좌 단상 (옥좌 · 사당 · 해골 · 화로 둘 · 깃발)
def stairs(x, ya, yb):
    sw, sh = G['stairs'].size
    for y in range(int(ya), int(yb), sh - 6): put('stairs', x - sw / 2 + 2, y, 0.5, 0); put('stairs', x + sw / 2 - 2, y, 0.5, 0, flip=True)
stairs(CX, TPY + TPHH - 30, Y0 + 10)
put('throne', CX, TPY - 20); put('shrL', CX - 190, TPY - 90); put('shrR', CX + 190, TPY - 90)
put('skulls', CX - 140, TPY + 10); put('skulls', CX + 140, TPY + 10, flip=True)
put('brzC', CX - 100, TPY + TPHH - 30); put('brzC', CX + 100, TPY + TPHH - 30)
put('ban2', CX - 270, TPY - 60); put('ban2', CX + 270, TPY - 60, flip=True)
put('brzB', CX - TPHW + 40, TPY - 60); put('brzB', CX + TPHW - 40, TPY - 60)
# 6) 아래: 계단 → 아래 단상(화로 둘 · 울타리 · 깃발) → 출구 계단 → 악마 아치
stairs(CX, Y1 - 20, BPY - BPHH + 20)
put('brzC', CX - 130, BPY + 10); put('brzC', CX + 130, BPY + 10)
put('fenceC', CX - 210, BPY - BPHH + 14); put('fenceC', CX + 210, BPY - BPHH + 14, flip=True)
put('ban1', CX - 250, BPY + BPHH - 6); put('ban1', CX + 250, BPY + BPHH - 6, flip=True)
stairs(CX, BPY + BPHH - 30, NH - 150)
put('arch', CX, NH - 20)
# 7) 좌우: 아치 다리 → 옆 단상 (오벨리스크 · 사슬 기둥)
for s in (-1, 1):
    f = s < 0; a0, a1 = REG['armE%d' % s][0][0], REG['armE%d' % s][1][0]; mx = (a0 + a1) / 2
    put('bridge', mx, CY + 60 + 46)                    # 다리 아래 아치
    put('rail', mx, CY - 56, flip=f)                    # 다리 위 난간
    put('obel', CX + s * SPX, CY - 20, flip=f); put('post', CX + s * (SPX + 100), CY + 40, flip=f)
    put('chain', CX + s * (SPX + 160), CY + 140, flip=f)
# 8) 대각: 다리 난간 + 모서리 단상 (화로 · 깃발 기둥 · 우리)
for s in (-1, 1):
    for t in (-1, 1):
        f = s < 0; px, py = CX + s * CPD, CY + t * CPD
        put('bridR' if (s * t) < 0 else 'bridL', CX + s * (DK + 120), CY + t * (DK + 120) + 50, flip=False)
        put('brzA' if t < 0 else 'brzB', px + s * 40, py - 10); put('banP', px - s * 60, py - 30, flip=f)
        if t > 0: put('cage', px + s * 70, py + 70, flip=f)
        else: put('fenceB', px - s * 20, py - CPR * 0.85 + 16, flip=f)
        put('chain', px + s * (CPR + 30), py + 60, flip=f)
# 9) 광장 위쪽 울타리 · 아래쪽 오벨리스크 (예시처럼 테두리를 따라)
for s in (-1, 1):
    f = s > 0
    put('fenceC', CX + s * 210, Y0 + 12, flip=f); put('fenceA', CX + s * 330, Y0 + 12, flip=f)
    put('obel', CX + s * 200, Y1 + 8, flip=f); put('fenceD', CX + s * 330, Y1 + 6, flip=f)
    put('post', X0 - 6 if s < 0 else X1 + 6, CY - 200, flip=f); put('post', X0 - 6 if s < 0 else X1 + 6, CY + 220, flip=f)
# 10) 걷는 곳 테두리 (어두운 선) + 다각형 (×2 = 게임 좌표)
cs, _ = cv2.findContours(WM.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE); c = max(cs, key=cv2.contourArea)
ap = cv2.approxPolyDP(c, 2.0, True)[:, 0, :].tolist()
ImageDraw.Draw(cv).line([tuple(p) for p in ap] + [tuple(ap[0])], fill=(20, 20, 24, 255), width=3)
cv.convert('RGB').save(OUT + 'pmap.webp', quality=92, method=6)
k = 2
J = {'iw': NW, 'ih': NH, 'X0': X0 * k, 'X1': X1 * k, 'Y0': Y0 * k, 'Y1': Y1 * k, 'c': C * k, 'cx': CX * k, 'cy': CY * k, 'bx': CX * k, 'by': (CY - 260) * k,
     'start': [CX * k, (BPY + 40) * k], 'exitY': (NH - 60) * k, 'itemY': (Y1 - 40) * k, 'skp': [[(CX - 420) * k, CY * k], [(CX + 420) * k, CY * k], [CX * k, (CY - 360) * k]],
     'poly': [[int(x * k), int(y * k)] for x, y in ap]}
json.dump(J, open('build/pan/pmap2.json', 'w'), separators=(',', ':'))
pv = cv.copy(); ImageDraw.Draw(pv).line([tuple(p) for p in ap] + [tuple(ap[0])], fill=(0, 255, 0, 255), width=3); pv.convert('RGB').resize((NW // 2, NH // 2)).save('build/pan/pmap2_prev.png')
print(cv.size, os.path.getsize(OUT + 'pmap.webp'), 'poly', len(ap))
