"""v10.31 챌린지 전용 맵(영겁의 균열 평원): 바닥 · 소품 → src/assets/chmap/chfloor.webp · chprops.webp/json
시트(build/chmap/sheet.png): 1448×1086, 181px 칸 8×6 (검은 격자선 · 큰 소품 4개는 2×2칸). 자르기 · 마젠타 배경 제거 · 배율(소품은 그대로)만 한다. 색·도트는 안 건드린다.
타일은 이음새가 안 맞아서(가장자리 차이 ≈ 안쪽 5배) 게임이 가장자리를 겹쳐 그린다 → 타일마다 격자선 4px 안쪽을 잘라 176px 정사각형(0.75배 안팎)으로 둔다.
chfloor 칸(176px): 0~7 = 1번 줄 · 8~13 = 2번 줄 앞 6칸(깨진 판석·의식진·사슬·해골·핏자국·보라 균열) · 14 = 불바닥 · 15 = 가시 구멍(접힘) · 16 = 가시 솟음 ·
  17~23 = 일반 돌바닥 변형 7장(2번 줄 끝 2칸 + 3번 줄 4~8칸 — 같은 돌바닥이라 반복을 줄이는 용도)
chprops: 0~7 = 4번 줄 작은 소품 · 8~11 = 큰 소품(무너진 아치 · 거대 갈비뼈 · 폐허 사당 · 균열 수정)"""
import numpy as np, json, os
from PIL import Image
from scipy import ndimage as ndi
IN = 'build/chmap/'; OUT = 'src/assets/chmap/'; os.makedirs(OUT, exist_ok=True)
S = np.array(Image.open(IN + 'sheet.png').convert('RGB'))
X = [0, 181, 362, 543, 724, 905, 1086, 1267, 1448]; Y = [0, 181, 362, 543, 724, 905, 1086]
T = 176
def tile(r, c, p=4):
    a = S[Y[r] + p:Y[r + 1] - p, X[c] + p:X[c + 1] - p]
    return np.array(Image.fromarray(a).resize((T, T), Image.LANCZOS))
cells = [(0, c) for c in range(8)] + [(1, c) for c in range(6)] + [(2, 0), (2, 1), (2, 2)] + [(1, 6), (1, 7)] + [(2, c) for c in range(3, 8)]
tiles = [tile(r, c) for r, c in cells]
fl = np.hstack(tiles); Image.fromarray(fl).save(OUT + 'chfloor.webp', lossless=True, method=6); print('tiles', len(tiles), fl.shape)

def cut(x0, x1, y0, y1, pad=4):
    a = S[y0 + pad:y1 - pad, x0 + pad:x1 - pad].astype(int); r, g, b = a[..., 0], a[..., 1], a[..., 2]
    bg = (r > 200) & (b > 200) & (g < 110)                      # 마젠타 배경
    lab, n = ndi.label(bg); edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    pure = (r > 225) & (b > 225) & (g < 70)                       # 아치 안쪽·갈비뼈 사이·새장 안쪽처럼 갇힌 배경도 순수 마젠타라 같이 지움
    bg = np.isin(lab, list(edge)) | (bg & ndi.binary_dilation(np.isin(lab, list(edge)), iterations=2)) | pure
    fr = ndi.binary_dilation(bg, iterations=1) & ~bg & (r > 170) & (b > 150) & (g < 150)               # 배경 바로 옆 분홍 번짐 1칸
    bg = bg | fr
    fg = ~bg; lab2, n2 = ndi.label(fg); sz = ndi.sum(fg, lab2, range(1, n2 + 1)); fg = np.isin(lab2, [i + 1 for i, v in enumerate(sz) if v >= 40])
    ys, xs = np.where(fg); sub = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(np.uint8); m = fg[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return Image.fromarray(np.dstack([sub, (m * 255).astype(np.uint8)]), 'RGBA')
props = [cut(X[c], X[c + 1], Y[3], Y[4]) for c in range(8)] + [cut(X[2 * k], X[2 * k + 2], Y[4], Y[6]) for k in range(4)]
print('props', [p.size for p in props])
W = 1024; x = y = sh = 0; pos = []
for c in props:
    w, h = c.size
    if x + w > W: x = 0; y += sh + 2; sh = 0
    pos.append((x, y)); x += w + 2; sh = max(sh, h)
at = Image.new('RGBA', (W, y + sh), (0, 0, 0, 0)); rects = []
for c, (x, y) in zip(props, pos): at.alpha_composite(c, (x, y)); rects.append([x, y, c.size[0], c.size[1]])
at.save(OUT + 'chprops.webp', lossless=True, method=6); json.dump(rects, open(OUT + 'chprops.json', 'w'), separators=(',', ':'))
bg = Image.new('RGBA', at.size, (60, 120, 90, 255)); bg.alpha_composite(at); bg.save(IN + 'chprops_prev.png')
print('rects', json.dumps(rects, separators=(',', ':')), at.size)
