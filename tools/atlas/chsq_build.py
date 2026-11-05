"""v10.33 챌린지 특수 잡몹 3종(돌격병·주술사·자폭병) 프레임 시트 + 주사기 → src/assets/chmap/chsq.webp + chsq.json
시트 3장(build/chdot2/{knight,shaman,bomb}.png, 마젠타 배경 · 줄마다 프레임) + 주사기(build/chdot2/syringe.png). 자르기 · 마젠타 배경 제거 · 0.5배 축소만 한다 (색·도트 수정 없음).
json = {"knight":{"idle":[[x,y,w,h,ax,ay]..],"move":..,"aim":..,"run":..,"die":..}, "shaman":{...}, "bomb":{...}, "syr":[x,y,w,h]}  (ax,ay = 발 기준점)"""
import numpy as np, json, os
from PIL import Image
from scipy import ndimage as ndi
IN = 'build/chdot2/'; OUT = 'src/assets/chmap/'; SC = 0.5
# 줄(행)·칸(열) 번호는 시트를 투영해서 찾은 것. 그룹 = (줄, [칸…])
GROUPS = {
 'knight': {'idle': (0, [0,1,2,3]), 'move': (1, [0,1,2,3,4,5]), 'aim': (2, [0,1,2,3]), 'run': (3, [0,1,2,3,4,5]), 'hit': (4, [0,1,2]), 'die': (5, [0,1,2,3])},
 'shaman': {'idle': (0, [0,1,2,3]), 'move': (1, [0,1,2,3,4,5]), 'cast': (2, [0,1,2,3,4,5]), 'ring': (3, [0,1,2,3,4,5]), 'hit': (4, [0,1,2]), 'die': (5, [0,1,2,3,4])},
 'bomb': {'idle': (0, [0,1,2,3]), 'move': (1, [0,1,2,3,4,5]), 'fuse': (2, [3,4,5]), 'boom': (3, [1,2,3,4,5]), 'hit': (4, [0,1,2]), 'die': (5, [0,1,2,3])},
}
def segs(fg):
    rows = fg.sum(1) > 0; lab, n = ndi.label(rows); R = [(s[0].start, s[0].stop) for s in ndi.find_objects(lab)]
    out = []
    for (a, b) in R:
        cols = fg[a:b].sum(0) > 0; l2, m = ndi.label(ndi.binary_dilation(cols, iterations=6)); out.append((a, b, [(s[0].start, s[0].stop) for s in ndi.find_objects(l2)]))
    return out
def cut(S, y0, y1, x0, x1, pad=6):
    y0 = max(0, y0 - pad); x0 = max(0, x0 - pad); a = S[y0:y1 + pad, x0:x1 + pad]; r, g, b = a[..., 0], a[..., 1], a[..., 2]
    bg = (r > 200) & (b > 200) & (g < 110); lab, n = ndi.label(bg)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    pure = (r > 225) & (b > 225) & (g < 70); bg = np.isin(lab, list(edge)) | pure
    fr = ndi.binary_dilation(bg, iterations=1) & ~bg & (r > 170) & (b > 150) & (g < 150); bg = bg | fr
    fg = ~bg; l2, n2 = ndi.label(fg); sz = ndi.sum(fg, l2, range(1, n2 + 1)); fg = np.isin(l2, [i + 1 for i, v in enumerate(sz) if v >= 30])
    ys, xs = np.where(fg); sub = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(np.uint8); m = fg[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    im = Image.fromarray(np.dstack([sub, (m * 255).astype(np.uint8)]), 'RGBA')
    al = np.array(im.getchannel('A')); yy, xx = np.where(al > 0); yb = yy.max(); sel = xx[yy > yb - max(6, int((yb - yy.min()) * 0.1))]; ax = float(np.median(sel))
    im = im.resize((max(1, round(im.width * SC)), max(1, round(im.height * SC))), Image.BOX)
    return im, ax * SC
cells = []   # (mob, group, idx, img, ax)
for mob, G in GROUPS.items():
    S = np.array(Image.open(IN + mob + '.png').convert('RGB')).astype(int); r, g, b = S[..., 0], S[..., 1], S[..., 2]
    fg = ndi.binary_opening(~((r > 200) & (b > 200) & (g < 110)), iterations=1); R = segs(fg)
    for gn, (ri, cs) in G.items():
        y0, y1, cl = R[ri]
        for ci in cs:
            x0, x1 = cl[ci]; im, ax = cut(S, y0, y1, x0, x1); cells.append((mob, gn, len(cells), im, ax))
# 주사기
S = np.array(Image.open(IN + 'syringe.png').convert('RGB')).astype(int); r, g, b = S[..., 0], S[..., 1], S[..., 2]
fg0 = ~((r > 200) & (b > 200) & (g < 110)); ys, xs = np.where(fg0)
SY, _ = cut(S, ys.min() - 2, ys.max() + 2, xs.min() - 2, xs.max() + 2, pad=4)
SY = SY.resize((max(1, round(SY.width * 0.25)), max(1, round(SY.height * 0.25))), Image.BOX)   # 주사기는 큰 그림이라 0.125배(= 0.5 × 0.25)
W = 1400; x = y = sh = 0; pos = []
for (_, _, _, im, _) in cells + [('', '', 0, SY, 0)]:
    w, h = im.size
    if x + w > W: x = 0; y += sh + 2; sh = 0
    pos.append((x, y)); x += w + 2; sh = max(sh, h)
at = Image.new('RGBA', (W, y + sh), (0, 0, 0, 0)); meta = {m: {} for m in GROUPS}
for (mob, gn, _, im, ax), (px, py) in zip(cells, pos): at.alpha_composite(im, (px, py)); meta[mob].setdefault(gn, []).append([px, py, im.width, im.height, round(ax), im.height - 1])
at.alpha_composite(SY, pos[-1]); meta['syr'] = [pos[-1][0], pos[-1][1], SY.width, SY.height]
at.save(OUT + 'chsq.webp', lossless=True, method=6); json.dump(meta, open(OUT + 'chsq.json', 'w'), separators=(',', ':'))
pv = Image.new('RGBA', at.size, (60, 120, 90, 255)); pv.alpha_composite(at); pv.save('build/chdot2/chsq_prev.png')
print(at.size, {m: {g: len(v) for g, v in d.items()} if isinstance(d, dict) else d for m, d in meta.items()})
