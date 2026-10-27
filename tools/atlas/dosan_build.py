"""v9.71 7지옥 '도산과 업경의 심판정'(지하 31~35층) 필드: 바닥 타일 · 칼날 지대 · 소품 → src/assets/dosan/dfloor.webp · dprops.webp/json
시트: 7지옥 맵 컨셉 시트(1536×1024) — '타일/지형 시트' · '주요 기믹 오브젝트' · '추가 오브젝트' 칸.
자르기 · 배경(검정) 제거 · 배율 조정 · 뒤집기만 한다 (재색칠 없음).
dfloor 칸(42px): 0~ = 바닥 타일(작은 타일 2×2 묶음을 42px로) + 뒤집은 변형, 마지막 2칸 = 칼날 지대 바닥(핏물 타일)
dblade: 칼날 지대 (기본)·(확장) 두 장 → dprops 맨 앞 두 칸
사용: python3 tools/atlas/dosan_build.py <맵 시트>"""
import sys, os, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
SRC = sys.argv[1] if len(sys.argv) > 1 else 'build/h7/map.png'
OUT = 'src/assets/dosan/'; os.makedirs(OUT, exist_ok=True); os.makedirs('build/h7', exist_ok=True)
S = np.array(Image.open(SRC).convert('RGB'))

def tile(x0, y0, w=35, h=35): return np.array(Image.fromarray(S[y0:y0 + h, x0:x0 + w]).resize((42, 42), Image.BOX))
# 회색 판석(왼쪽 위 묶음) · 붉은 갈색 판석(가운데 위) · 핏자국 판석(아래 가운데)
BASE = [tile(584, 139), tile(619, 139), tile(584, 174), tile(637, 174),     # 0~3 회색 판석 (3 = 핏자국)
        tile(680, 139), tile(714, 139), tile(680, 172),                    # 4~6 붉은 갈색 판석
        tile(663, 240), tile(663, 275), tile(680, 290)]                    # 7~9 핏줄 판석
tiles = list(BASE)
FLIP = [0, 1, 4, 7]
for i in FLIP: tiles += [BASE[i][:, ::-1], BASE[i][::-1, :], BASE[i][::-1, ::-1]]
HAZ = [tile(684, 207, 76, 20), tile(589, 228, 56, 32)]   # 칼날 지대 바닥: 갈색 판석 아래 핏물 · 핏빛 연못
tiles += HAZ
Image.fromarray(np.hstack(tiles)).save(OUT + 'dfloor.webp', lossless=True, method=6)
print('tiles', len(tiles), 'flip', {i: len(BASE) + 3 * k for k, i in enumerate(FLIP)}, 'haz', [len(tiles) - 2, len(tiles) - 1])

def cell(x0, y0, x1, y1, keep_main=False, thr=34):
    a = S[y0:y1, x0:x1].astype(int); mx = a.max(2); dark = mx <= thr
    lab, n = ndi.label(dark); edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    fg = ~np.isin(lab, list(edge))
    lab2, n2 = ndi.label(fg); sz = ndi.sum(fg, lab2, range(1, n2 + 1))
    if keep_main:   # 가장 큰 덩어리 + 그 둘레 6px 안 조각만
        main = lab2 == (int(np.argmax(sz)) + 1); near = ndi.binary_dilation(main, iterations=6)
        fg = np.isin(lab2, [j + 1 for j in range(n2) if sz[j] >= 0.2 * sz.max() or (near & (lab2 == j + 1)).any()])
    else: fg = np.isin(lab2, [j + 1 for j in range(n2) if sz[j] >= 12])
    ys, xs = np.where(fg)
    sub = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(np.uint8); m = fg[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return Image.fromarray(np.dstack([sub, (m * 255).astype(np.uint8)]), 'RGBA')

# [이름, x0, y0, x1, y1, 가장 큰 덩어리만]
P = [('칼날 지대(기본)', 578, 405, 683, 501, True), ('칼날 지대(확장)', 684, 403, 782, 501, True),
     ('나무 팻말', 988, 118, 1009, 193, True), ('걸린 깃발', 1023, 105, 1052, 188, True), ('해골 깃발', 1063, 142, 1096, 232, True),
     ('작은 팻말 기둥', 943, 205, 962, 277, True), ('촛대 기둥', 975, 263, 995, 328, True), ('찢긴 깃발', 1163, 263, 1246, 330, False),
     ('기둥 등롱', 1243, 275, 1279, 357, True), ('매단 등롱', 1310, 105, 1356, 197, True), ('부적 깃발', 942, 791, 989, 937, True),
     ('저승 깃발', 985, 796, 1043, 966, True), ('저승문 현판', 1052, 806, 1109, 964, True), ('해골 더미', 1113, 866, 1198, 963, True),
     # ---- 큰 구조물 ----
     ('짧은 울타리', 965, 195, 1057, 257, True), ('긴 울타리', 995, 262, 1158, 330, True), ('앞 울타리', 863, 280, 967, 338, True),
     ('저승 문(일주문)', 1092, 108, 1237, 260, True), ('깃대', 1253, 105, 1300, 268, True), ('돌 등롱 깃발', 1275, 220, 1325, 356, True),
     ('염라 좌상', 1328, 105, 1462, 341, False), ('작은 석상', 1462, 240, 1525, 356, True), ('저승수', 1348, 780, 1525, 976, False)]
cells = [cell(x0, y0, x1, y1, km) for _, x0, y0, x1, y1, km in P]
W = 1024; x = y = sh = 0; pos = []
for c in cells:
    w, h = c.size
    if x + w > W: x = 0; y += sh + 2; sh = 0
    pos.append((x, y)); x += w + 2; sh = max(sh, h)
at = Image.new('RGBA', (W, y + sh), (0, 0, 0, 0)); rects = []
for c, (x, y) in zip(cells, pos): at.alpha_composite(c, (x, y)); rects.append([x, y, c.size[0], c.size[1]])
at.save(OUT + 'dprops.webp', lossless=True, method=6); json.dump(rects, open(OUT + 'dprops.json', 'w'), separators=(',', ':'))
bg = Image.new('RGBA', at.size, (120, 70, 150, 255)); bg.alpha_composite(at); bg.save('build/h7/dprops_prev.png')
fl = Image.open(OUT + 'dfloor.webp').convert('RGB'); fl.resize((fl.width * 3, fl.height * 3), Image.NEAREST).save('build/h7/dfloor_prev.png')
print('props', len(rects), at.size); print(json.dumps(rects, separators=(',', ':'))); print([p[0] for p in P])
