"""v10.39 10지옥 '판데모니움' 보스맵 — 받은 '보스맵 조각' 시트(build/pan/boss.png, 마젠타 배경 1448×1086)의 타일·구조물을
예시 보스맵(7. EXAMPLE BOSS MAP)처럼 원래 크기 그대로 이어 붙여 만든다 (예시 그림을 키우지 않으므로 해상도가 깨지지 않는다).
쓰는 법: python3 tools/atlas/pmap_build.py  →  src/assets/pan/pmap.webp (게임에서 ×2 nearest = IMAP_PAN.s)
자르기 · 마젠타 배경 제거 · 이어 붙이기 · 좌우 뒤집기(대칭 자리)만 — 색·도트 수정 없음 (심연 바탕만 어둡게 눌러 깔았다).
구성 (예시 맵 그대로): 가운데 팔각 광장(걷는 곳) + 한가운데 원형 마법진 · 위쪽 계단 위 옥좌와 고딕 성벽 · 네 모서리 다리 끝 작은 단상과 백염 화로
· 아래 계단 = 출구 · 바깥은 심연(흰 빛줄기) · 아래쪽 가장자리는 떠 있는 절벽."""
import numpy as np, os, json
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
SRC = 'build/pan/boss.png'; OUT = 'src/assets/pan/'; os.makedirs(OUT, exist_ok=True)
S = Image.open(SRC).convert('RGB'); A = np.array(S).astype(int)
def bgmask(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return ((r - g > 60) & (b - g > 60)) | ((r > 180) & (b > 180) & (g < 120))
def piece(box, big=False):   # 상자 안 전경(가장 큰 덩어리만 big=True)
    x0, y0, x1, y1 = box; s = A[y0:y1, x0:x1]; fg = ~bgmask(s); fg = ndi.binary_opening(fg, iterations=1); L, n = ndi.label(fg)
    if n:
        sz = ndi.sum(fg, L, range(1, n + 1))
        fg = (L == int(np.argmax(sz)) + 1) if big else np.isin(L, [i + 1 for i, v in enumerate(sz) if v >= 25])
    for _ in range(2):   # 가장자리에 남은 마젠타 번짐(보랏빛 테두리)도 배경으로
        r, g, b = s[..., 0], s[..., 1], s[..., 2]; edge = fg & ~ndi.binary_erosion(fg); fg = fg & ~(edge & (r - g > 22) & (b - g > 22))
    ys, xs = np.where(fg); bx0, bx1, by0, by1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    return Image.fromarray(np.dstack([s[by0:by1, bx0:bx1].astype(np.uint8), (fg[by0:by1, bx0:bx1] * 255).astype(np.uint8)]), 'RGBA')
FC = [(10, 66), (69, 125), (128, 186), (189, 246), (249, 302)]; FR = [(41, 104), (107, 165), (169, 227), (230, 294)]
TS = 56
def tile(r, c, ins=2): (x0, x1), (y0, y1) = FC[c], FR[r]; return S.crop((x0 + ins, y0 + ins, x1 - ins, y1 - ins)).resize((TS, TS), Image.BOX).convert('RGBA')
P = {   # 쓰는 조각 (시트 좌표)
  'cliffA': [317, 38, 368, 110], 'cliffB': [369, 37, 428, 111], 'cliffC': [430, 37, 535, 109], 'cliffD': [536, 37, 611, 111],
  'rockA': [705, 36, 758, 100], 'rockB': [757, 37, 806, 108], 'rockC': [810, 37, 850, 108],
  'wallA': [317, 110, 466, 221], 'wallB': [472, 112, 620, 221], 'wallC': [625, 118, 707, 221], 'wallD': [318, 229, 478, 297], 'stairs': [481, 228, 550, 297],
  'gateW': [555, 229, 615, 297], 'arches': [626, 228, 742, 297], 'colm': [818, 177, 852, 257],
  'q0': [8, 346, 107, 449], 'q1': [113, 346, 212, 449], 'q2': [8, 454, 107, 555], 'q3': [113, 454, 212, 555],
  'arch': [364, 340, 541, 488], 'shrL': [545, 340, 601, 450], 'throne': [569, 340, 800, 523], 'shrR': [774, 340, 850, 472],
  'pillar': [202, 517, 267, 670], 'plat': [346, 490, 440, 562], 'platS': [274, 528, 344, 580], 'post': [440, 488, 478, 558],
  'chain': [488, 518, 557, 617], 'banP': [560, 523, 641, 667], 'spire': [760, 481, 847, 670], 'bridL': [15, 544, 107, 613], 'bridR': [115, 544, 206, 613],
  'brzA': [275, 587, 331, 670], 'brzB': [344, 566, 404, 670], 'brzC': [416, 562, 486, 670], 'altar': [499, 610, 605, 667],
  'fenceA': [16, 719, 86, 783], 'fenceB': [97, 720, 147, 779], 'fenceC': [155, 721, 246, 776], 'fenceD': [249, 718, 311, 776],
  'ban1': [473, 712, 528, 808], 'ban2': [533, 712, 616, 782], 'skulls': [74, 783, 142, 881], 'ruin': [184, 784, 274, 882], 'obel': [682, 778, 762, 890], 'ribs': [763, 803, 851, 876],
}
G = {k: piece(v, big=k in ('throne', 'arch', 'spire', 'pillar')) for k, v in P.items()}
abyss = S.crop((12, 943, 61, 994)).convert('RGBA')   # 5번 위험 지대 '심연'
NW, NH = 1500, 1720
X0, X1, Y0, Y1, C = 225, 1275, 380, 1280, 225; CX, CY = 750, 830; CX0, CX1, YB = 681, 819, 1660
cv = Image.new("RGBA", (NW, NH), (0, 0, 0, 0))   # 투명 위에 쌓고, 절벽 밑 빛줄기를 깐 검은 바탕 위로 옮긴다
def put(k, x, y, ax=0.5, ay=1.0, flip=False):   # (x, y) = 그림의 (ax, ay) 자리
    im = G[k] if isinstance(k, str) else k
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    cv.alpha_composite(im, (int(round(x - im.width * ax)), int(round(y - im.height * ay))))
# 1) 심연: 검은 바탕 — 흰 빛줄기 타일은 떠 있는 절벽 아래로만 흘러내리게(아래로 갈수록 옅어지는 마스크)
def fall(x, y, n, a0=200):   # 심연 타일 한 장을 세로로 늘려(이음매 없이) 아래·양옆으로 옅어지게
    im = abyss.resize((abyss.width, abyss.height * n), Image.NEAREST); al = np.array(im.split()[3]).astype(float)
    f = np.linspace(1, 0, im.height)[:, None] ** 1.3 * np.sin(np.linspace(0, np.pi, im.width))[None, :] ** 0.7; im.putalpha(Image.fromarray((al * f * a0 / 255).astype(np.uint8)))
    cv.alpha_composite(im, (int(x), int(y)))
FALLS = []
cv.alpha_composite(Image.new('RGBA', (NW, NH), (0, 0, 0, 0)))
# 2) 멀리 떠 있는 바위
rnd = np.random.RandomState(7)
for (x, y, k) in [(90, 300, 'rockA'), (1400, 260, 'rockB'), (70, 1150, 'rockC'), (1430, 1180, 'rockA'), (160, 1560, 'rockB'), (1350, 1600, 'rockC'), (60, 760, 'cliffA'), (1440, 720, 'cliffB')]: put(k, x, y)
# 3) 위쪽 고딕 성벽(뒤) · 첨탑
for x, k, f in [(330, 'wallA', False), (500, 'wallC', False), (1000, 'wallC', True), (1170, 'wallA', True)]: put(k, x, Y0 + 14, flip=f)
put('wallD', 200, 250); put('wallD', 1300, 250, flip=True)
put('spire', X0 + C - 20, Y0 + 30); put('spire', X1 - C + 20, Y0 + 30, flip=True)
# 4) 아래쪽 가장자리 밑 떠 있는 절벽 (광장 두께) — 바닥보다 먼저 깔아 윗면이 바닥과 겹치게
cl = ['cliffC', 'cliffA', 'cliffD', 'cliffB']
def skirt(xa, ya, xb, yb, step):
    n = max(1, int(np.hypot(xb - xa, yb - ya) / step))
    for i in range(n + 1):
        t = i / n; k = cl[(i + int(xa)) % 4]; x, y = xa + (xb - xa) * t, ya + (yb - ya) * t; FALLS.append((x, y)); put(k, x, y + 44)
skirt(X0, Y1 - C, X0 + C, Y1, 42); skirt(X0 + C, Y1, CX0 - 20, Y1, 50); skirt(CX1 + 20, Y1, X1 - C, Y1, 50); skirt(X1 - C, Y1, X1, Y1 - C, 42)
skirt(X0, Y0 + C, X0, Y1 - C, 999); skirt(X1, Y0 + C, X1, Y1 - C, 999)
for y in range(Y0 + C + 60, Y1 - C, 120): put('cliffA', X0 + 6, y + 40); put('cliffA', X1 - 6, y + 40, flip=True)
# 절벽 밑 빛줄기는 절벽 뒤에 깔아야 하므로 지금까지 그린 걸 잠깐 떼어 두고 다시 얹는다
top = cv.copy(); cv = Image.new('RGBA', (NW, NH), (9, 9, 11, 255))
for i, (x, y) in enumerate(FALLS):
    if i % 2 == 0: fall(x - abyss.width / 2, y + 60, 4 + i % 4)
for (x, y) in [(60, 840), (1420, 820), (140, 1240), (1340, 1260)]: fall(x, y, 3, 120)
cv.alpha_composite(top)
# 5) 광장 바닥: 밝은 판석 + 가운데 원(반지름 390) 안은 어두운 판석, 테두리는 조각 경계 대신 원 모양으로
light = [tile(0, 1), tile(0, 3), tile(0, 1).transpose(Image.FLIP_LEFT_RIGHT)]   # 밝기가 다른 (3,0) 판석은 격자처럼 보여서 뺐다
dark = [tile(0, 0), tile(0, 0), tile(0, 0).transpose(Image.FLIP_LEFT_RIGHT)]
fl = Image.new('RGBA', (NW, NH)); dk = Image.new('RGBA', (NW, NH))
for ty, y in enumerate(range(Y0 - TS, Y1 + TS, TS)):
    for tx, x in enumerate(range(X0 - TS, X1 + TS, TS)):
        fl.alpha_composite(light[(tx * 7 + ty * 3) % 3], (x, y)); dk.alpha_composite(dark[(tx * 5 + ty * 11) % 3], (x, y))
poly = [(X0 + C, Y0), (X1 - C, Y0), (X1, Y0 + C), (X1, Y1 - C), (X1 - C, Y1), (X0 + C, Y1), (X0, Y1 - C), (X0, Y0 + C)]
m = Image.new('L', (NW, NH), 0); ImageDraw.Draw(m).polygon(poly, fill=255)
md = Image.new('L', (NW, NH), 0); ImageDraw.Draw(md).ellipse((CX - 390, CY - 390, CX + 390, CY + 390), fill=255)
fl.putalpha(m); cv.alpha_composite(fl)
dk.putalpha(Image.fromarray(np.minimum(np.array(md), np.array(m)))); cv.alpha_composite(dk)
# 해골 판석 몇 장 (가장자리)
for (x, y) in [(X0 + 40, Y0 + C + 40), (X1 - 96, Y1 - C - 120), (X0 + C + 60, Y1 - 70), (X1 - C - 140, Y0 + 20)]: cv.alpha_composite(tile(3, 1), (x, y))
# 6) 가운데 원형 마법진 (네 조각 이어 붙이기) + 사방 룬 판
q = [G['q0'], G['q1'], G['q2'], G['q3']]; w0, h0 = q[0].size
put(q[0], CX, CY, 1, 1); put(q[1], CX - 2, CY, 0, 1); put(q[2], CX, CY - 2, 1, 0); put(q[3], CX - 2, CY - 2, 0, 0)
for (dx, dy, r, c) in [(0, -300, 2, 2), (0, 300, 2, 2), (-300, 0, 1, 2), (300, 0, 1, 2)]: cv.alpha_composite(tile(r, c), (CX + dx - TS // 2, CY + dy - TS // 2))
for (dx, dy) in [(-212, -212), (212, -212), (-212, 212), (212, 212)]: cv.alpha_composite(tile(1, 1), (CX + dx - TS // 2, CY + dy - TS // 2))
# 7) 위: 옥좌(계단 포함) · 양옆 사당 · 깃발
put('throne', CX, Y0 + 26); put('shrL', CX - 150, Y0 + 6); put('shrR', CX + 150, Y0 + 6)
put('ban2', CX - 250, Y0 + 30); put('ban2', CX + 250, Y0 + 30, flip=True)
# 8) 네 모서리: 다리 → 작은 단상 + 백염 화로
dxy = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
for sx, sy in dxy:   # 대각 변 가운데에 붙은 작은 단상(발코니) + 백염 화로 — 걷는 곳 밖 장식
    ex, ey = (X0 + C / 2 if sx < 0 else X1 - C / 2), (Y0 + C / 2 if sy < 0 else Y1 - C / 2)
    px, py = ex + sx * 62, ey + sy * 56
    put('plat', px, py + 44); put('brzC' if sy < 0 else 'brzB', px, py + 8)
# 9) 양옆 벽: 기둥과 사슬
for y in range(Y0 + C + 40, Y1 - C + 40, 150): put('post', X0 - 8, y); put('post', X1 + 8, y, flip=True)
put('banP', X0 - 40, CY + 70); put('banP', X1 + 40, CY + 70, flip=True)
# 10) 아래: 출구 계단 두 줄 + 끝의 악마 아치
sw = G['stairs'].width
for i, y in enumerate(range(Y1 + 2, YB - 40, G['stairs'].height - 6)):
    put('stairs', CX - sw / 2 + 2, y, 0.5, 0); put('stairs', CX + sw / 2 - 2, y, 0.5, 0, flip=True)
put('arch', CX, YB + 30)
put('fenceC', X0 + C + 140, Y1 + 8); put('fenceC', X1 - C - 140, Y1 + 8, flip=True)
put('obel', X0 + C + 30, Y1 + 10); put('obel', X1 - C - 30, Y1 + 10, flip=True)
ImageDraw.Draw(cv).line(poly[:5] + [(CX1, Y1)], fill=(20, 20, 24, 255), width=3); ImageDraw.Draw(cv).line([(CX0, Y1)] + poly[5:] + [poly[0]], fill=(20, 20, 24, 255), width=3)   # 광장 테두리
cv.save(OUT + 'pmap.webp', lossless=True, method=6)
pv = cv.copy(); d = ImageDraw.Draw(pv); d.polygon(poly + [], outline=(0, 255, 0)); d.rectangle((CX0, Y1, CX1, YB), outline=(0, 255, 0)); pv.save('build/pan/pmap_prev.png')
print(cv.size, os.path.getsize(OUT + 'pmap.webp'))
