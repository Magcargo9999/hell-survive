"""v10.39 10지옥 '판데모니움' 필드 타일셋 (받은 시트 '흑백 지옥도시 타일셋', 마젠타 배경 1448×1086)
쓰는 법: 시트를 build/pan/tiles.png 로 두고 python3 tools/atlas/pan_build.py
→ src/assets/pan/pfloor.webp (42px 바닥 16칸) · pprops.webp (소품, 원래 크기) + 템플릿 PPROP_RECTS 한 줄 출력
자르기 · 마젠타 배경 제거 · 축소 · 좌우 뒤집기(바닥 변형)만 — 색·도트 수정 없음.
바닥 칸: 0 어두운 판석(붉은 금) · 1 밝은 판석 · 2 쇠창살 격자 · 3 밝은 마름모 판석 · 4 흰 균열 · 5 체크무늬 · 6 룬 원 · 7 별 문양 · 8 흰 균열(2) · 9 해골 판석
        10~13 = 0~3 좌우 뒤집기 · 14·15 위험 지대 (5번 칸 '흰 용암 균열' 두 장, 번갈아 일렁임)"""
import numpy as np, json, os
from PIL import Image
from scipy import ndimage as ndi
IN = 'build/pan/tiles.png'; OUT = 'src/assets/pan/'; os.makedirs(OUT, exist_ok=True)
A = np.array(Image.open(IN).convert('RGB')).astype(int); SRCIM = Image.open(IN).convert('RGB')
def bgmask(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return ((r - g > 60) & (b - g > 60)) | ((r > 180) & (b > 180) & (g < 120))
T = 42
FC = [(15, 84), (88, 158), (162, 231), (235, 304), (308, 377)]; FR = [(119, 195), (198, 274)]
HC = [(16, 81), (85, 151), (156, 223), (227, 294), (298, 368), (371, 435)]; HR = [(758, 815), (819, 876)]
def cell(x0, x1, y0, y1, ins=3): return SRCIM.crop((x0 + ins, y0 + ins, x1 - ins, y1 - ins)).resize((T, T), Image.BOX)
tiles = [cell(x0, x1, y0, y1) for (y0, y1) in FR for (x0, x1) in FC]
tiles += [tiles[i].transpose(Image.FLIP_LEFT_RIGHT) for i in (0, 1, 2, 3)]
haz = [cell(*HC[0], *HR[0]), cell(*HC[2], *HR[1])]   # 흰 용암 균열 · 흰 균열
tiles += haz
st = Image.new('RGB', (T * len(tiles), T))
for i, t in enumerate(tiles): st.paste(t, (i * T, 0))
st.save(OUT + 'pfloor.webp', lossless=True, method=6)
# 소품 (3번 건축·오브젝트 + 4번 구조물) — 상자 안의 전경만, 아주 작은 부스러기는 버림
PROPS = [[12, 325, 192, 487], [190, 325, 301, 469], [305, 322, 361, 428], [364, 322, 420, 428], [418, 322, 470, 414], [485, 322, 640, 400], [643, 322, 694, 422], [697, 322, 772, 427],
         [771, 322, 869, 420], [878, 331, 979, 437], [422, 408, 516, 498], [507, 400, 571, 444], [576, 394, 629, 497], [771, 398, 890, 564], [209, 471, 290, 564], [522, 448, 571, 492],
         [633, 430, 724, 489], [728, 430, 778, 495], [888, 443, 987, 504], [12, 488, 141, 564], [137, 487, 212, 564], [292, 515, 371, 564], [377, 509, 458, 564], [464, 505, 515, 564],
         [518, 500, 573, 564], [579, 500, 647, 564], [653, 497, 722, 564], [728, 498, 768, 564], [891, 506, 986, 564], [300, 428, 366, 511], [362, 428, 422, 501],
         [12, 606, 188, 710], [188, 605, 312, 710], [317, 656, 344, 710], [322, 606, 441, 655], [351, 656, 380, 710], [445, 606, 530, 656], [385, 660, 436, 710], [443, 660, 529, 709],
         [536, 600, 573, 710], [580, 600, 622, 710], [627, 600, 764, 712], [764, 600, 835, 711], [835, 600, 932, 712], [926, 600, 985, 712]]
cuts = []
for x0, y0, x1, y1 in PROPS:
    s = A[y0:y1, x0:x1]; fg = ~bgmask(s); fg = ndi.binary_opening(fg, iterations=1); L, n = ndi.label(fg)
    if n: sz = ndi.sum(fg, L, range(1, n + 1)); fg = np.isin(L, [i + 1 for i, v in enumerate(sz) if v >= 25])
    ys, xs = np.where(fg); bx0, bx1, by0, by1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    sub = s[by0:by1, bx0:bx1].astype(np.uint8); m = fg[by0:by1, bx0:bx1]
    cuts.append(Image.fromarray(np.dstack([sub, (m * 255).astype(np.uint8)]), 'RGBA'))
Wd = 1024; x = y = sh = 0; R = []
for im in cuts:
    if x + im.width > Wd: x = 0; y += sh + 2; sh = 0
    R.append([x, y, im.width, im.height]); x += im.width + 2; sh = max(sh, im.height)
at = Image.new('RGBA', (Wd, y + sh), (0, 0, 0, 0))
for im, r in zip(cuts, R): at.alpha_composite(im, (r[0], r[1]))
at.save(OUT + 'pprops.webp', lossless=True, method=6)
big = [i for i, r in enumerate(R) if r[3] >= 140 or r[2] >= 140]
print('const PPROP_RECTS = ' + json.dumps(R, separators=(',', ':')) + ';')
print('BIG', big)
pv = Image.new('RGBA', at.size, (40, 40, 44, 255)); pv.alpha_composite(at); pv.save('build/pan/pprops_prev.png')
Image.open(OUT + 'pfloor.webp').resize((T * len(tiles) * 2, T * 2), Image.NEAREST).save('build/pan/pfloor_prev.png')
print(os.path.getsize(OUT + 'pfloor.webp'), os.path.getsize(OUT + 'pprops.webp'))
