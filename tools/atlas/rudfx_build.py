"""마하칼 루드라 이펙트 시트(자홍 배경) → src/assets/rud/rudfx.webp + rudfx.json (v9.21)
배경(자홍) 제거 + 칸 자르기 + 최종 형태 크기 맞춤(FIN_K)만 — 재색칠 없음
그룹: bead 4 · beadH 5 · boom 3 · spike 4 · pillar 4 · ring 4 · rune 8 · fwalk 7 · fcast 7 · d4 3 (기본 폼 사망 4~6)
사용: python3 rudfx_build.py <이펙트 시트.png>"""
import sys, os, json
from PIL import Image
import numpy as np
from scipy import ndimage
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
A = np.array(Image.open(sys.argv[1]).convert('RGBA')); RGB = A[..., :3].astype(int)
mag = np.minimum(RGB[..., 0], RGB[..., 2]) - RGB[..., 1]
bg = (mag > 100) & (RGB[..., 0] > 150) & (RGB[..., 2] > 150)
halo = ndimage.binary_dilation(bg, iterations=1) & (mag > 55) & ~bg
bg = bg | halo
bg = bg | (ndimage.binary_dilation(bg, iterations=1) & (mag > 75))
# 이름표(남색 사각 패널 + 글자)는 통째로 지운다
navy = (RGB[..., 0] < 70) & (RGB[..., 1] < 70) & (RGB[..., 2] < 100) & ~bg
nv = ndimage.binary_fill_holes(ndimage.binary_closing(navy, iterations=3)); lab_, n_ = ndimage.label(nv)
for i, sl in enumerate(ndimage.find_objects(lab_)):
    h = sl[0].stop - sl[0].start; w = sl[1].stop - sl[1].start; m_ = lab_[sl] == i + 1
    if w >= 45 and 18 <= h <= 80 and m_.sum() / (h * w) > 0.88:
        bg[max(0, sl[0].start - 4):sl[0].stop + 4, max(0, sl[1].start - 4):sl[1].stop + 4] = True
lab_, n_ = ndimage.label(~bg)   # 이름표 가장자리 선·글자 부스러기(납작한 조각) 제거
for i, sl in enumerate(ndimage.find_objects(lab_)):
    h = sl[0].stop - sl[0].start; w = sl[1].stop - sl[1].start
    if h <= 22 and w >= 22 and w / h > 2.2: bg[sl] |= (lab_[sl] == i + 1)
bg[806:836, 742:902] = True   # 시전 모션 이름표 남은 조각
FGM = ~bg
def valley(y0, y1, c, w=14):
    seg = FGM[y0:y1, c - w:c + w].sum(axis=0); m = seg.min(); xs = np.where(seg == m)[0]; return c - w + int(xs[len(xs) // 2])
def cut(x0, y0, x1, y1, keepall=False, gap=5):
    m = FGM[y0:y1, x0:x1].copy()
    if not keepall:
        big = ndimage.binary_dilation(m, iterations=gap); lab, n = ndimage.label(big)
        if n > 1:
            sz = ndimage.sum(m, lab, range(1, n + 1)); m = m & (lab == 1 + int(np.argmax(sz)))
    reg = A[y0:y1, x0:x1].copy(); reg[..., 3] = np.where(m, 255, 0)
    im = Image.fromarray(reg); bb = im.getchannel('A').getbbox(); return im.crop(bb), bb
def row(y0, y1, x0, x1, cs):
    xs = [x0] + [valley(y0, y1, c) for c in cs] + [x1]; return [(xs[i], xs[i + 1]) for i in range(len(xs) - 1)]
G = {}   # 이름 → (프레임 [(im, ax, ay)], 기준: 'c' 가운데 · 'b' 아래 가운데)
def add(name, boxes, y0, y1, mode, keepall=False, k=1.0, gap=5):
    L = []
    for a, c in boxes:
        im, bb = cut(a, y0, c, y1, keepall, gap)
        if k != 1.0: im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
        L.append((im, im.width / 2, im.height / 2 if mode == 'c' else im.height))
    G[name] = L
add('bead', row(70, 228, 16, 556, [100, 277, 409]), 70, 228, 'c', True)
G['bead'] = G['bead'][:4]
add('beadH', row(70, 228, 568, 1100, [666, 756, 869, 971]), 70, 228, 'c', True)
add('boom', row(40, 228, 1110, 1665, [1288, 1466]), 40, 228, 'c', True)
add('spike', row(250, 470, 16, 760, [195, 365, 533]), 250, 470, 'b')
add('pillar', row(225, 478, 790, 1672, [962, 1180, 1407]), 225, 478, 'b')
add('ring', [(16, 200), (202, 386), (386, 581), (581, 795)], 490, 662, 'c', True)
RU = [855, 930, 1062, 1130, 1215, 1320, 1415, 1530, 1625]
add('rune', [(RU[i] - (8 if i == 0 else 0), RU[i + 1]) for i in range(8)], 495, 662, 'c', True)
FK = 0.68
w = row(683, 808, 740, 1668, [1007, 1108, 1208, 1312, 1415, 1511]); w[0] = (895, w[0][1])
add('fwalk', w, 683, 808, 'b', k=FK, gap=6)
add('fcast', row(812, 934, 740, 1668, [866, 970, 1172, 1306, 1456, 1558]), 812, 934, 'b', k=FK, gap=7, keepall=True)
add('d4', row(715, 930, 14, 720, [240, 458]), 715, 930, 'b', k=0.5, gap=7)
meta = {}; pos = []; W = 0; y = 0
for kname, Lf in G.items():
    cw = max(im.width for im, _, _ in Lf) + 4; ch = max(im.height for im, _, _ in Lf) + 4; meta[kname] = []
    for i, (im, ax, ay) in enumerate(Lf):
        ox = i * cw + (cw - im.width) // 2; oy = y + (ch - im.height) // 2
        meta[kname].append([i * cw, y, cw, ch, ox - i * cw + int(ax), oy - y + int(ay)]); pos.append((im, ox, oy))
    W = max(W, cw * len(Lf)); y += ch
at = Image.new('RGBA', (W, y), (0, 0, 0, 0))
for im, x, yy in pos: at.alpha_composite(im, (x, yy))
at.save(os.path.join(ROOT, 'src/assets/rud/rudfx.webp'), lossless=True); json.dump(meta, open(os.path.join(ROOT, 'src/assets/rud/rudfx.json'), 'w'))
for nm, col in (('a', (110, 110, 110, 255)), ('b', (30, 90, 50, 255))):
    b2 = Image.new('RGBA', at.size, col); b2.alpha_composite(at); b2 = b2.resize((b2.width * 2, b2.height * 2), Image.NEAREST); b2.save(os.path.join(ROOT, 'build/rudfx_prev_%s.png' % nm))
print(at.size, {k: len(v) for k, v in meta.items()})
