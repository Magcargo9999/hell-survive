"""v10.25 8지옥 '타르타로스'(지하 36~40층) 필드·보스맵·1보스 타이탄 아틀라스
자르기 · 배경(마젠타) 제거 · 배율 조정 · 뒤집기만 한다 (재색칠 없음).
사용: python3 tools/atlas/tar_build.py <타일 시트(마젠타, 보라 바닥 5×4)> <타일셋 안내 시트(보스 아레나 예시)> <타이탄 시트(마젠타)>
 → src/assets/tar/tfloor.webp (42px 칸: 0~10 바닥 · 11~22 뒤집은 변형 · 23 붉은 빛 바닥 · 24·25 봉인 함정 지대)
   src/assets/tar/tprops.webp + tprops.json (소품 사각형)
   src/assets/tar/tmap.webp (보스 아레나 예시 그림 그대로 608×777)
   src/assets/tar/ttn.webp + ttn.json (타이탄 idle6 · walk8 · smash6 · whip6 · hit3 · death5 + 바위 rock1)"""
import sys, os, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
TS, GS, TT = sys.argv[1:4]
OUT = 'src/assets/tar/'; os.makedirs(OUT, exist_ok=True); os.makedirs('build/h8', exist_ok=True)

def magenta(a):   # 배경 마젠타
    a = a.astype(int); return (a[..., 0] > 150) & (a[..., 2] > 150) & (a[..., 1] < 110)

# ---------- 바닥 ----------
S = np.array(Image.open(TS).convert('RGB'))
CX = [(9, 85), (88, 162), (165, 239), (242, 316), (318, 390)]; RY = [(8, 92), (95, 192), (195, 279), (282, 376)]
def tile(x0, x1, y0, y1, m=4):
    cx, cy, s = (x0 + x1) // 2, (y0 + y1) // 2, min(x1 - x0, y1 - y0) - 2 * m
    return np.array(Image.fromarray(S[cy - s // 2:cy + s // 2, cx - s // 2:cx + s // 2]).resize((42, 42), Image.BOX))
BASE = [tile(*CX[c], *RY[r]) for r in range(4) for c in range(5) if not (1 <= c <= 3 and 1 <= r <= 3)]   # 가운데 룬 원 9칸 제외 → 14칸
tiles = list(BASE)
for i in (0, 2, 5, 9): tiles += [BASE[i][:, ::-1], BASE[i][::-1, :], BASE[i][::-1, ::-1]]
tiles.append(tile(397, 472, 8, 92))                       # 26 붉은 빛 바닥(가끔)
def rect_tile(x0, y0, x1, y1): return np.array(Image.fromarray(S[y0 + 3:y1 - 3, x0 + 3:x1 - 3]).resize((42, 42), Image.BOX))
tiles += [rect_tile(1117, 915, 1208, 1013), rect_tile(1336, 909, 1450, 1018)]   # 27·28 봉인 함정 지대(붉은 룬 판 · 금 간 판)
Image.fromarray(np.hstack(tiles)).save(OUT + 'tfloor.webp', lossless=True, method=6)
print('tiles', len(tiles))

# ---------- 소품 (사각형 안의 마젠타만 투명) ----------
def cut(x0, y0, x1, y1, keep_main=False):
    a = S[y0:y1, x0:x1]; fg = ~magenta(a)
    lab, n = ndi.label(fg); sz = ndi.sum(fg, lab, range(1, n + 1)) if n else []
    if keep_main and n:
        main = lab == (int(np.argmax(sz)) + 1); near = ndi.binary_dilation(main, iterations=6)
        fg = np.isin(lab, [j + 1 for j in range(n) if sz[j] >= 0.2 * max(sz) or (near & (lab == j + 1)).any()])
    else: fg = np.isin(lab, [j + 1 for j in range(n) if sz[j] >= 10])
    fg = ndi.binary_erosion(fg, iterations=1) | (fg & ~ndi.binary_dilation(~fg, iterations=1))   # 가장자리 분홍 번짐 1px
    ys, xs = np.where(fg)
    sub = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]; m = fg[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return Image.fromarray(np.dstack([sub, (m * 255).astype(np.uint8)]), 'RGBA')
P = [  # 작은 소품 0~
    ('검 깃발', 494, 386, 559, 590), ('깃발1', 560, 386, 630, 537), ('깃발2', 631, 386, 704, 561), ('깃발3', 705, 388, 775, 502), ('깃발4', 777, 387, 843, 484),
    ('늘어진 사슬', 852, 472, 882, 590), ('갈고리', 1003, 388, 1032, 516), ('작은 새장', 943, 478, 1002, 592), ('매단 사슬', 958, 610, 1029, 738),
    ('화로1', 653, 768, 707, 845), ('화로2', 711, 774, 766, 845), ('화로3', 771, 761, 830, 845), ('가시1', 835, 768, 892, 830), ('가시2', 894, 769, 956, 826),
    ('가시 기둥', 956, 738, 1016, 840), ('제단 상자', 645, 850, 766, 916), ('수정 잔해', 764, 835, 922, 919), ('가시 밭', 922, 836, 1050, 916),
    ('해골 더미', 4, 922, 137, 1014), ('뼈 더미', 137, 923, 235, 1014), ('작은 아치', 237, 918, 346, 1013), ('돌 조각', 347, 964, 399, 1013), ('돌기둥', 399, 918, 451, 1013),
    ('부서진 기둥', 452, 923, 516, 1013), ('잔해 블록', 517, 923, 626, 1013), ('부서진 아치', 628, 918, 735, 1013), ('돌무더기1', 742, 924, 912, 1013), ('돌무더기2', 920, 927, 1048, 1009),
    ('바위1', 1284, 4, 1349, 65), ('바위2', 1351, 5, 1418, 65), ('바위3', 1341, 68, 1408, 134), ('바위4', 1284, 76, 1341, 134), ('바위5', 1341, 139, 1412, 217), ('작은 돌들', 1285, 225, 1365, 279),
    ('수정 첨탑1', 1450, 11, 1483, 64), ('수정 첨탑2', 1409, 135, 1533, 217), ('수정 첨탑3', 1450, 217, 1532, 282),
    # 큰 구조물 37~
    ('감옥 기둥1', 496, 595, 570, 784), ('감옥 기둥2', 574, 595, 648, 784), ('짧은 기둥1', 494, 791, 568, 914), ('짧은 기둥2', 572, 791, 646, 914),
    ('새장1', 658, 588, 737, 751), ('새장2', 739, 588, 838, 760), ('새장3', 843, 588, 949, 754),
    ('톱니 바퀴', 1027, 484, 1191, 592), ('반 톱니', 1039, 384, 1188, 484), ('작은 톱니', 1192, 500, 1268, 560),
    ('아치 다리1', 1188, 383, 1357, 502), ('아치 다리2', 1357, 383, 1530, 502), ('난간 다리', 1274, 501, 1444, 604),
    ('수정 첨탑 큰', 1409, 15, 1533, 134), ('수정 첨탑 큰2', 1288, 275, 1407, 374), ('수정 첨탑 큰3', 1392, 283, 1533, 378)]
cells = [cut(x0, y0, x1, y1, keep_main=True) for _, x0, y0, x1, y1 in P]
W = 1024; x = y = sh = 0; pos = []
for c in cells:
    w, h = c.size
    if x + w > W: x = 0; y += sh + 2; sh = 0
    pos.append((x, y)); x += w + 2; sh = max(sh, h)
at = Image.new('RGBA', (W, y + sh), (0, 0, 0, 0)); rects = []
for c, (x, y) in zip(cells, pos): at.alpha_composite(c, (x, y)); rects.append([x, y, c.size[0], c.size[1]])
at.save(OUT + 'tprops.webp', lossless=True, method=6); json.dump(rects, open(OUT + 'tprops.json', 'w'), separators=(',', ':'))
bg = Image.new('RGBA', at.size, (60, 140, 90, 255)); bg.alpha_composite(at); bg.save('build/h8/tprops_prev.png')
print('props', len(rects), at.size, 'big from', 37)
print(json.dumps(rects, separators=(',', ':')))

# ---------- 보스맵: 안내 시트의 예시 아레나 그림 (액자 안쪽만) ----------
Image.open(GS).convert('RGB').crop((829, 250, 1437, 1027)).save(OUT + 'tmap.webp', quality=95, method=6)

# ---------- 타이탄 ----------
T = np.array(Image.open(TT).convert('RGB')); TB = magenta(T); TF = ~TB
ROWS = [  # (이름, y0, y1, [x 구간…]) — 칸 사이 빈 세로줄 기준
    ('idle', 292, 441, [(198, 351), (402, 549), (600, 749), (800, 948), (1000, 1147), (1198, 1353)]),
    ('walk', 441, 573, [(87, 219), (272, 407), (460, 590), (641, 759), (815, 931), (983, 1088), (1155, 1269), (1334, 1459)]),
    ('smash', 573, 720, [(101, 274), (339, 498), (576, 731), (796, 948), (1009, 1195), (1232, 1466)]),
    ('whip', 728, 850, [(28, 188), (251, 440), (482, 683), (727, 966), (975, 1214), (1250, 1506)]),
    ('hit', 864, 1008, [(9, 143), (160, 292), (309, 440)]),
    ('death', 864, 1008, [(618, 755), (771, 953), (966, 1150), (1163, 1347), (1359, 1526)]),
]
frames = {}; imgs = []
for name, y0, y1, xs in ROWS:
    for a, b in xs:
        reg = T[y0:y1, a - 2:b + 2]; fg = TF[y0:y1, a - 2:b + 2].copy()
        lab, n = ndi.label(fg); sz = ndi.sum(fg, lab, range(1, n + 1))
        main = lab == (int(np.argmax(sz)) + 1); near = ndi.binary_dilation(main, iterations=10)   # 몸 + 가까운 이펙트(사슬·먼지)만
        keep = np.isin(lab, [j + 1 for j in range(n) if (near & (lab == j + 1)).any() and sz[j] >= 6])
        ys, xs2 = np.where(keep)
        sub = reg[ys.min():ys.max() + 1, xs2.min():xs2.max() + 1]; m = keep[ys.min():ys.max() + 1, xs2.min():xs2.max() + 1]
        # 발 기준점: 가장 큰 덩어리(몸)의 아래 끝 · 가로 가운데
        my, mx = np.where(main[ys.min():ys.max() + 1, xs2.min():xs2.max() + 1])
        foot = my.max(); bx = mx[my >= foot - 25].mean() if name not in ('death',) else mx.mean()
        imgs.append((name, Image.fromarray(np.dstack([sub, (m * 255).astype(np.uint8)]), 'RGBA'), float(bx), int(foot + 1)))
# 바위 (대차륜 철퇴 · 낙석) — 타일 시트 오른쪽 위 큰 바위 덩어리
rk = cut(1341, 139, 1412, 217, True); imgs.append(('rock', rk, rk.size[0] / 2, rk.size[1]))
rk2 = cut(1284, 4, 1349, 65, True); imgs.append(('rock', rk2, rk2.size[0] / 2, rk2.size[1]))
W = 2048; x = y = sh = 0; at = []
for nm, im, ax, ay in imgs:
    w, h = im.size
    if x + w > W: x = 0; y += sh + 2; sh = 0
    at.append((nm, im, x, y, ax, ay)); x += w + 2; sh = max(sh, h)
A = Image.new('RGBA', (W, y + sh), (0, 0, 0, 0))
for nm, im, x, y, ax, ay in at:
    A.alpha_composite(im, (x, y)); frames.setdefault(nm, []).append([x, y, im.size[0], im.size[1], round(ax, 1), ay])
A.save(OUT + 'ttn.webp', lossless=True, method=6); json.dump(frames, open(OUT + 'ttn.json', 'w'), separators=(',', ':'))
bg = Image.new('RGBA', A.size, (60, 140, 90, 255)); bg.alpha_composite(A); bg.save('build/h8/ttn_prev.png')
print('titan', {k: len(v) for k, v in frames.items()}, A.size)
print(json.dumps(frames, separators=(',', ':')))
