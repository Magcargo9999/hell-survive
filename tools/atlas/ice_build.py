"""v8.99 팔한지옥(지하 21~25층) 필드: 바닥 타일 · 소품 → src/assets/ice/ifloor.webp · iprops.webp/json
시트(build/ice/tiles.png): 팔한지옥 맵 타일셋 1448×1086. 자르기 · 배경(어두운 남색) 제거 · 배율(42px 칸 맞춤) · 좌우·위아래 뒤집기(같은 그림, 색 그대로)만 한다.
ifloor 칸 순서: 0~7 = 시트 1번 줄(균열진 빙판·흑빙·눈보라 설원·서리 묻은 돌·혈흔 균열·빙결 의식진·사원 바닥·산산한 영구빙), 8~ = 뒤집은 변형"""
import numpy as np, json, os
from PIL import Image
from scipy import ndimage as ndi
IN = 'build/ice/'; OUT = 'src/assets/ice/'; os.makedirs(OUT, exist_ok=True)
S = np.array(Image.open(IN + 'tiles.png').convert('RGB'))
CX = [(21, 106), (115, 200), (210, 294), (304, 388), (398, 482), (491, 575), (584, 669), (678, 765)]; Y0, Y1 = 147, 233
base = []
for x0, x1 in CX:
    t = S[Y0 + 3:Y1 - 3, x0 + 3:x1 - 3]; base.append(np.array(Image.fromarray(t).resize((42, 42), Image.BOX)))
tiles = list(base)
FLIP = [0, 2, 3, 6, 7]   # 자주 깔리는 타일은 뒤집은 변형을 더해 반복을 줄인다
for i in FLIP:
    tiles += [base[i][:, ::-1], base[i][::-1, :], base[i][::-1, ::-1]]
hz = np.array(Image.fromarray(S[801:871, 592:674]).resize((42, 42), Image.BOX)); tiles += [hz, hz[:, ::-1]]   # 23·24 = 위험 지대(5번 줄 '붉은 균열 지대') 두 장이 번갈아
Image.fromarray(np.hstack(tiles)).save(OUT + 'ifloor.webp', lossless=True, method=6); print('tiles', len(tiles), 'flip idx', {i: 8 + 3 * k for k, i in enumerate(FLIP)})

# ---- 소품: 3번(장식) · 4번(구조물) 줄의 그림 ----
def fgmask(a, thr=44):
    dark = a.max(2) <= thr
    lab, n = ndi.label(dark); edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    return ~np.isin(lab, list(edge))
def items(box, gap=4, thr=44):
    x0, y0, x1, y1 = box; a = S[y0:y1, x0:x1].astype(int); fg = fgmask(a, thr); fg = ndi.binary_opening(fg, iterations=1) | (fg & ndi.binary_dilation(ndi.binary_opening(fg, iterations=1), iterations=2))
    cols = fg.sum(0) > 0; out = []; x = 0; W = len(cols)
    while x < W:
        if cols[x]:
            s = x
            while x < W and (cols[x] or (x + gap < W and cols[x:x + gap].any())): x += 1
            seg = fg[:, s:x]; ys, xs = np.where(seg)
            if seg.sum() > 120 and xs.max() - xs.min() > 14 and ys.max() - ys.min() > 14:
                sub = a[ys.min():ys.max() + 1, s + xs.min():s + xs.max() + 1].astype(np.uint8); m = seg[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
                out.append(Image.fromarray(np.dstack([sub, (m * 255).astype(np.uint8)]), 'RGBA'))
        x += 1
    return out
row3 = items((12, 455, 782, 556)); row4 = items((12, 620, 782, 724))
print('row3', len(row3), [i.size for i in row3]); print('row4', len(row4), [i.size for i in row4])
SEL = row3 + row4
W = 1024; x = y = sh = 0; pos = []
for c in SEL:
    w, h = c.size
    if x + w > W: x = 0; y += sh + 2; sh = 0
    pos.append((x, y)); x += w + 2; sh = max(sh, h)
at = Image.new('RGBA', (W, y + sh), (0, 0, 0, 0)); rects = []
for c, (x, y) in zip(SEL, pos): at.alpha_composite(c, (x, y)); rects.append([x, y, c.size[0], c.size[1]])
at.save(OUT + 'iprops.webp', lossless=True, method=6); json.dump(rects, open(OUT + 'iprops.json', 'w'), separators=(',', ':'))
bg = Image.new('RGBA', at.size, (110, 130, 170, 255)); bg.alpha_composite(at); bg.save(IN + 'iprops_prev.png')
fl = Image.open(OUT + 'ifloor.webp').convert('RGB'); fl.resize((fl.width * 2, fl.height * 2), Image.NEAREST).save(IN + 'ifloor_prev.png')
print('props', len(rects), at.size)
