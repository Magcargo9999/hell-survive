"""v10.32 챌린지 도트: 특수 잡몹 3종 · 금제의 제단 · 룰렛 판 · 룰렛 바늘 → src/assets/chmap/chdot.webp + chdot.json
시트(build/chdot/sheet.png): 1448×1086 마젠타 배경 · 그림 6개. 자르기 · 마젠타 배경 제거 · 0.5배 축소(BOX)만 한다 (색·도트 수정 없음).
칸 순서(json 인덱스): 0 돌격병(왼쪽을 봄) · 1 주술사 · 2 자폭병 · 3 금제의 제단 · 4 룰렛 판 · 5 룰렛 바늘(아래를 가리킴)"""
import numpy as np, json, os
from PIL import Image
from scipy import ndimage as ndi
IN = 'build/chdot/'; OUT = 'src/assets/chmap/'; os.makedirs(OUT, exist_ok=True)
S = np.array(Image.open(IN + 'sheet.png').convert('RGB')).astype(int)
BOX = [(21, 83, 451, 510), (491, 16, 951, 505), (994, 46, 1388, 500), (49, 568, 490, 1019), (539, 559, 1014, 1024), (1137, 578, 1312, 963)]
SC = 0.5
def cut(x0, y0, x1, y1, pad=6):
    a = S[y0 - pad:y1 + pad + 1, x0 - pad:x1 + pad + 1]; r, g, b = a[..., 0], a[..., 1], a[..., 2]
    bg = (r > 200) & (b > 200) & (g < 110)
    lab, n = ndi.label(bg); edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    pure = (r > 225) & (b > 225) & (g < 70)                    # 고리 안쪽처럼 갇힌 마젠타도 지움
    bg = np.isin(lab, list(edge)) | pure
    fr = ndi.binary_dilation(bg, iterations=1) & ~bg & (r > 170) & (b > 150) & (g < 150)
    bg = bg | fr
    fg = ~bg; lab2, n2 = ndi.label(fg); sz = ndi.sum(fg, lab2, range(1, n2 + 1)); fg = np.isin(lab2, [i + 1 for i, v in enumerate(sz) if v >= 40])
    ys, xs = np.where(fg); sub = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(np.uint8); m = fg[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    im = Image.fromarray(np.dstack([sub, (m * 255).astype(np.uint8)]), 'RGBA')
    return im.resize((max(1, round(im.width * SC)), max(1, round(im.height * SC))), Image.BOX)
P = [cut(*b) for b in BOX]
W = 1024; x = y = sh = 0; pos = []
for c in P:
    w, h = c.size
    if x + w > W: x = 0; y += sh + 2; sh = 0
    pos.append((x, y)); x += w + 2; sh = max(sh, h)
at = Image.new('RGBA', (W, y + sh), (0, 0, 0, 0)); rects = []
for c, (x, y) in zip(P, pos): at.alpha_composite(c, (x, y)); rects.append([x, y, c.size[0], c.size[1]])
at.save(OUT + 'chdot.webp', lossless=True, method=6); json.dump(rects, open(OUT + 'chdot.json', 'w'), separators=(',', ':'))
bg = Image.new('RGBA', at.size, (60, 120, 90, 255)); bg.alpha_composite(at); bg.save(IN + 'chdot_prev.png')
print(json.dumps(rects, separators=(',', ':')), at.size)
