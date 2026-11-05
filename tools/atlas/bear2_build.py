"""v10.33 팔한지옥의 백곰 마왕 고해상도 시트 4장(어두운 남색 배경) → src/assets/bear/bear.webp + bear.json
(v9.51 bear_build.py 의 새 시트판. 자르기 · 배경 제거 · 줄이기 · 좌우 뒤집기(이동 줄 · 돌진 6칸)만 — 재색칠 없음)
게임은 '왼쪽을 보는' 시트를 전제로 하므로(face>0이면 뒤집어 그림) 오른쪽을 보는 줄은 아틀라스에서 미리 뒤집는다.
사용: python3 bear2_build.py <시트1> <시트2> <시트3> <시트4>   (1: 대기·이동 · 2: 기본공격·강공격 · 3: 특수·피격·사망·변신 · 4: 폭주 돌진 6칸)"""
import sys, os, json
from PIL import Image, ImageDraw
import numpy as np
from scipy import ndimage
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
SH = [np.array(Image.open(p).convert('RGBA')) for p in sys.argv[1:5]]
FK = 0.72          # 게임은 ×2 nearest (PB_K2) — 화면 크기는 예전(0.75 · ×4)과 비슷
THR = 60
def cut(A, x0, y0, x1, y1, mask=None):
    reg = A[y0:y1, x0:x1].copy(); lum = reg[..., :3].max(axis=2).astype(int); fg = lum >= THR
    if mask is not None:
        for (a, b, c, d) in mask: fg[b:d, a:c] = False
    lab, n = ndimage.label(fg, structure=np.ones((3, 3)))
    for i, sl in enumerate(ndimage.find_objects(lab), 1):   # 가는 줄(판 테두리) · 부스러기 제거
        hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start; a = (lab[sl] == i).sum()
        if (hh <= 4 and ww >= 40) or (ww <= 4 and hh >= 40) or a < 10: fg[sl] &= ~(lab[sl] == i)
    cl = ndimage.binary_closing(fg, structure=np.ones((3, 3)), iterations=2)
    lab, n = ndimage.label(cl, structure=np.ones((3, 3)))
    if n == 0: return None
    sz = ndimage.sum(np.ones_like(lum), lab, range(1, n + 1)); order = np.argsort(-sz); keep = {int(order[0]) + 1}
    for j in order[1:]:
        if sz[j] >= max(30, sz[order[0]] * 0.004): keep.add(int(j) + 1)
    m = np.isin(lab, list(keep)); m = ndimage.binary_dilation(m, iterations=3) & (lum >= 26); m = ndimage.binary_fill_holes(m)
    reg[..., 3] = np.where(m, 255, 0); im = Image.fromarray(reg); bb = im.getchannel('A').getbbox(); return im.crop(bb)
def bounds(A, y0, y1, x0, x1, n):
    lum = A[y0:y1, x0:x1, :3].max(axis=2); h = y1 - y0; cnt = (lum[: int(h * 0.82)] >= THR).sum(0); pitch = (x1 - x0) / n; xs = [x0]
    for i in range(1, n):
        c = int(i * pitch); w = int(pitch * 0.28); seg = cnt[c - w:c + w]; m = seg.min(); idx = np.where(seg == m)[0]; xs.append(x0 + c - w + int(idx[len(idx) // 2]))
    return xs + [x1]
ROWS = {   # 이름: (시트, y0, y1, x0, x1, 칸 수, 뒤집기)
 'idle':  (0, 509, 749, 18, 1430, 6, False),
 'move':  (0, 814, 1062, 18, 1430, 8, True),
 'atk':   (1, 254, 528, 18, 1430, 6, False),
 'atk2':  (1, 674, 992, 18, 1430, 6, False),
 'spec':  (2, 133, 321, 18, 1430, 6, False),
 'hit':   (2, 380, 569, 18, 1430, 4, False),
 'death': (2, 627, 797, 18, 1430, 6, False),
 'phase': (2, 856, 1066, 18, 1430, 4, False),
}
PANELS = [(20, 202, 714, 470), (733, 202, 1429, 470), (20, 487, 714, 757), (733, 487, 1429, 757), (20, 774, 714, 1058), (733, 774, 1429, 1058)]
frames = {}
def finish(im, flip):
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    a = np.array(im.getchannel('A')); ys, xx = np.where(a > 0); yb = ys.max(); sel = xx[ys > yb - max(8, int((yb - ys.min()) * 0.12))]; ax = float(np.median(sel))
    im = im.resize((max(1, round(im.width * FK)), max(1, round(im.height * FK))), Image.LANCZOS); return (im, ax * FK)
for k, (si, y0, y1, x0, x1, n, fl) in ROWS.items():
    A = SH[si]; xs = bounds(A, y0, y1, x0, x1, n); frames[k] = [finish(cut(A, xs[i], y0, xs[i + 1], y1), fl) for i in range(n)]
frames['charge'] = []
for i, (a, b, c, d) in enumerate(PANELS):   # 판 왼쪽 위 'n / 6 프레임' 글씨 칸은 가린다 · 6칸만 오른쪽을 봄 → 뒤집기
    frames['charge'].append(finish(cut(SH[3], a + 4, b + 4, c - 4, d - 4, mask=[(0, 0, 175, 44)]), i == 5))
meta = {}; pos = []; W = 0; y = 0
for kname, Lf in frames.items():
    cw = int(max(max(ax, im.width - ax) for im, ax in Lf) * 2) + 6; ch = max(im.height for im, _ in Lf) + 4; meta[kname] = []
    for i, (im, ax) in enumerate(Lf):
        ox = i * cw + int(cw / 2 - ax); oy = y + ch - 2 - im.height
        meta[kname].append([i * cw, y, cw, ch, cw // 2, ch - 2]); pos.append((im, ox, oy))
    W = max(W, cw * len(Lf)); y += ch
at = Image.new('RGBA', (W, y), (0, 0, 0, 0))
for im, x, yy in pos: at.alpha_composite(im, (x, yy))
at.save(os.path.join(ROOT, 'src/assets/bear/bear.webp'), lossless=True, method=6); json.dump(meta, open(os.path.join(ROOT, 'src/assets/bear/bear.json'), 'w'))
b2 = Image.new('RGBA', at.size, (60, 130, 90, 255)); b2.alpha_composite(at); d = ImageDraw.Draw(b2)
for kn, ms in meta.items():
    for m in ms: d.rectangle([m[0], m[1], m[0] + m[2] - 1, m[1] + m[3] - 1], outline=(255, 255, 0, 255))
b2.save(os.path.join(ROOT, 'build/bear2_prev.png'))
print(at.size, {k: len(v) for k, v in meta.items()})
