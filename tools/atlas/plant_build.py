"""v8.53 지하 16~20층 '악마 식물원' 잡몹 · 네임드 마물 아틀라스 (자르기 · 배경 제거 · 정수 배율만, 재색칠 없음)
사용: python3 tools/atlas/plant_build.py <악마 도감 시트(1536×1024)> <가시덩굴> <식인 꽃> <거대 달팽이>
출력(src/assets/gard/):
  gmob.webp  식물형 악마 8종 (작은 4종 정수 2배 · 2프레임 + 큰 4종 원본) — 108×114 칸, 버섯형 악마(mmob)와 같은 배치
  gnm.webp + gnm.json  네임드 3종: 키 = 동작 이름, 값 = [[x, y, w, h], …]
"""
import sys, os, json
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mush_build_helpers import load, cut
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'src/assets/gard'); os.makedirs(OUT, exist_ok=True)
PREV = os.path.join(ROOT, 'build/plant'); os.makedirs(PREV, exist_ok=True)

# ---- 식물형 악마 8종 (도감 시트 오른쪽 위 칸) ----
B = load(sys.argv[1]); CW, CH = 108, 114
SMALL = [[(1030, 182, 1083, 234), (1100, 182, 1143, 232)], [(1172, 182, 1212, 232), (1225, 182, 1264, 232)],
         [(1287, 180, 1335, 234), (1344, 180, 1392, 234)], [(1410, 180, 1458, 234), (1464, 180, 1510, 234)]]
BIG = [(1030, 66, 1139, 169), (1171, 61, 1261, 168), (1292, 61, 1386, 169), (1415, 61, 1509, 169)]
cells = []
for fr in SMALL:
    cs = [cut(B, b, 14, 34, center=False) for b in fr]
    cells.append([np.array(Image.fromarray(c).resize((c.shape[1] * 2, c.shape[0] * 2), Image.NEAREST)) for c in cs])
for b in BIG:
    c = cut(B, b, 14, 34, center=False); cells.append([c, c])
at = np.zeros((CH * 2, CW * len(cells), 4), np.uint8); nh = []
for i, cs in enumerate(cells):
    for k, c in enumerate(cs):
        h, w = c.shape[:2]; assert h <= CH - 2 and w <= CW, (i, h, w)
        ox = i * CW + (CW - w) // 2; oy = k * CH + CH - 2 - h; at[oy:oy + h, ox:ox + w] = c
    nh.append(max(c.shape[0] for c in cs))
Image.fromarray(at).save(os.path.join(OUT, 'gmob.webp'), lossless=True, method=6)
print('gmob nh', nh)

# ---- 네임드 3종 (검은 배경 카드) ----
NM = {
  'vine': (sys.argv[2], {
    'walk': [(166, 40, 228, 93), (229, 40, 287, 93), (288, 40, 347, 93), (348, 40, 413, 93)],
    'atk': [(250, 108, 306, 160), (306, 108, 412, 160)],
    'port': [(8, 42, 238, 168)]}),
  'fly': (sys.argv[3], {
    'walk': [(146, 44, 212, 104), (213, 44, 277, 104), (277, 44, 343, 104), (343, 44, 408, 104)],
    'atk': [(146, 110, 224, 171), (225, 113, 299, 171)],
    'fx': [(300, 125, 357, 165), (360, 128, 407, 162)],
    'port': [(8, 44, 134, 171)]}),
  'snl': (sys.argv[4], {
    'walk': [(160, 46, 246, 103), (248, 52, 318, 103), (319, 52, 379, 103)],
    'hide': [(162, 120, 240, 162)],
    'ball': [(379, 66, 414, 96)],
    'blob': [(246, 118, 292, 162), (292, 118, 338, 162), (338, 118, 389, 162)],
    'port': [(8, 42, 160, 166)]}),
}
tiles = []
for nm, (f, rows) in NM.items():
    S = load(f); S2 = S.copy()
    if nm == 'vine': S2[30:97, 160:240] = (8, 6, 7)   # 큰 그림 상자와 겹치는 걷기 칸 자리는 배경색으로 (큰 그림 자르기용 사본)
    for k, boxes in rows.items():
        for b in boxes: tiles.append((nm + '_' + k, cut(S2 if k == 'port' else S, b, 16, 40, center=False)))
W = 1024; x = y = rh = 0; place = []
for k, t in tiles:
    h, w = t.shape[:2]
    if x + w > W: x = 0; y += rh + 2; rh = 0
    place.append((k, t, x, y)); x += w + 2; rh = max(rh, h)
out = np.zeros((y + rh, W, 4), np.uint8); F = {}
for k, t, x, y in place:
    h, w = t.shape[:2]; out[y:y + h, x:x + w] = t; F.setdefault(k, []).append([x, y, w, h])
Image.fromarray(out).save(os.path.join(OUT, 'gnm.webp'), lossless=True, method=6)
json.dump(F, open(os.path.join(OUT, 'gnm.json'), 'w'), separators=(',', ':'))
print('gnm', out.shape, {k: len(v) for k, v in F.items()})
for name, arr in (('gmob', at), ('gnm', out)):
    bg = Image.new('RGBA', (arr.shape[1], arr.shape[0]), (70, 60, 90, 255)); bg.alpha_composite(Image.fromarray(arr))
    bg.resize((bg.width * 2, bg.height * 2), Image.NEAREST).save(os.path.join(PREV, name + '_prev.png'))
