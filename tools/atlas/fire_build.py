"""v9.24 팔열지옥(지하 26~30층) 필드: 바닥 타일 · 소품 → src/assets/fire/ffloor.webp · fprops.webp/json
시트(build/fire/tiles.png): 팔열지옥 맵 타일셋 1448×1086 (팔한지옥과 같은 판형). 자르기 · 배경(검정) 제거 · 배율(42px 칸 맞춤) · 뒤집기(같은 그림, 색 그대로)만 한다.
ffloor 칸: 0~8 = 시트 1번 줄(타는 돌·검은 철·마그마 균열·의식진·가열된 청동·피재·지옥 벽돌·그을린 벽돌·심연의 그을린 땅), 9~20 = 0·1·5·7번을 뒤집은 변형, 21·22 = 위험 지대(용암 웅덩이·발화 바닥)
fprops: 0~10 = 3번 줄 장식, 11~19 = 4번 줄 구조물"""
import numpy as np, json, os
from PIL import Image
from scipy import ndimage as ndi
IN = 'build/fire/'; OUT = 'src/assets/fire/'; os.makedirs(OUT, exist_ok=True)
S = np.array(Image.open(IN + 'tiles.png').convert('RGB'))
CX = [(22, 101), (110, 189), (198, 277), (286, 365), (374, 453), (462, 541), (549, 628), (636, 715), (724, 803)]; Y0, Y1 = 160, 239
base = []
for x0, x1 in CX:
    t = S[Y0 + 3:Y1 - 3, x0 + 3:x1 - 3]; base.append(np.array(Image.fromarray(t).resize((42, 42), Image.BOX)))
tiles = list(base)
FLIP = [0, 1, 5, 7]   # 자주 깔리는 타일은 뒤집은 변형을 더해 반복을 줄인다
for i in FLIP:
    tiles += [base[i][:, ::-1], base[i][::-1, :], base[i][::-1, ::-1]]
hz = np.array(Image.fromarray(S[831:890, 25:86]).resize((42, 42), Image.BOX)); hz2 = np.array(Image.fromarray(S[831:890, 721:780]).resize((42, 42), Image.BOX)); tiles += [hz, hz2]   # 위험 지대: 5번 줄 '용암 웅덩이' · '발화 바닥'
Image.fromarray(np.hstack(tiles)).save(OUT + 'ffloor.webp', lossless=True, method=6); print('tiles', len(tiles), 'flip idx', {i: 9 + 3 * k for k, i in enumerate(FLIP)})

# ---- 소품: 3번(장식) · 4번(구조물) 줄 — 칸마다 따로 자르고(테두리선 3px 안쪽), 칸 가장자리와 이어진 어두운 배경만 투명하게 ----
def cell(x0, x1, y0, y1, pad=3):
    a = S[y0 + pad:y1 - pad, x0 + pad:x1 - pad].astype(int); mx = a.max(2)
    ring = np.concatenate([mx[:2].ravel(), mx[-2:].ravel(), mx[:, :2].ravel(), mx[:, -2:].ravel()]); bgv = np.median(ring)
    dark = mx <= bgv + 10
    lab, n = ndi.label(dark); edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    fg = ~np.isin(lab, list(edge))
    fg = fg & ndi.binary_dilation(ndi.binary_opening(fg, iterations=1), iterations=2)   # 1px 테두리선·밑줄 제거 (그림 가장자리는 되살림)
    lab2, n2 = ndi.label(fg); sz = ndi.sum(fg, lab2, range(1, n2 + 1))
    fg = np.isin(lab2, [i + 1 for i, v in enumerate(sz) if v >= 30])   # 작은 부스러기·글자 조각 제거
    ys, xs = np.where(fg)
    sub = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(np.uint8); m = fg[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return Image.fromarray(np.dstack([sub, (m * 255).astype(np.uint8)]), 'RGBA')
R3 = [(22, 95), (100, 172), (176, 245), (250, 299), (303, 370), (373, 451), (456, 521), (521, 617), (618, 667), (671, 720), (722, 798)]
R4 = [(13, 109), (116, 198), (202, 322), (325, 402), (411, 538), (538, 641), (641, 688), (688, 736), (739, 796)]
row3 = [cell(a, b, 470, 559) for a, b in R3]; row4 = [cell(a, b, 629, 746) for a, b in R4]
print('row3', len(row3), [i.size for i in row3]); print('row4', len(row4), [i.size for i in row4])
SEL = row3 + row4
W = 1024; x = y = sh = 0; pos = []
for c in SEL:
    w, h = c.size
    if x + w > W: x = 0; y += sh + 2; sh = 0
    pos.append((x, y)); x += w + 2; sh = max(sh, h)
at = Image.new('RGBA', (W, y + sh), (0, 0, 0, 0)); rects = []
for c, (x, y) in zip(SEL, pos): at.alpha_composite(c, (x, y)); rects.append([x, y, c.size[0], c.size[1]])
at.save(OUT + 'fprops.webp', lossless=True, method=6); json.dump(rects, open(OUT + 'fprops.json', 'w'), separators=(',', ':'))
bg = Image.new('RGBA', at.size, (120, 70, 150, 255)); bg.alpha_composite(at); bg.save(IN + 'fprops_prev.png')
fl = Image.open(OUT + 'ffloor.webp').convert('RGB'); fl.resize((fl.width * 2, fl.height * 2), Image.NEAREST).save(IN + 'ffloor_prev.png')
print('props', len(rects), at.size)
