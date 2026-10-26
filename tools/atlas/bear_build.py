"""팔한지옥의 백곰 마왕 도트 시트(어두운 남색 배경) → src/assets/bear/bear.webp + bear.json (v9.51)
인게임 줄(대기6 · 이동8 · 기본 공격6 · 강공격6 · 특수6 · 피격4 · 사망6 · 변신4 · 돌진6)을 자르고, 가장자리에서 이어진 어두운 배경만 지운다 (재색칠 없음, 자르기·배경 제거·줄이기만)
칸 경계는 대략 위치 둘레에서 가장 빈 세로줄(valley) · 기준점 = 바닥 둘레 x 중앙값 · 높이를 FK 배로 줄임(게임이 ×4 nearest) · 시트는 모두 왼쪽을 본다
특수 줄은 칸마다 뒤에 붉은 깃발·안개 배경 그림이 있어 가장 큰 덩어리(몸)만 남긴다
사용: python3 bear_build.py <시트.png>"""
import sys, os, json
from PIL import Image, ImageDraw
import numpy as np
from scipy import ndimage
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
S = Image.open(sys.argv[1]).convert('RGBA'); A = np.array(S); L = A[..., :3].max(axis=2).astype(int)
FK = 0.75
def valley(y0, y1, c, w=10):
    seg = (L[y0:y1, max(0, c - w):c + w] > 40).sum(axis=0); m = seg.min(); xs = np.where(seg == m)[0]; return max(0, c - w) + int(xs[len(xs) // 2])
def cut(x0, y0, x1, y1, thr=40, big=False):
    reg = A[y0:y1, x0:x1].copy(); lum = reg[..., :3].max(axis=2)
    fg = lum >= thr
    if big:   # 깃발(붉은 천) · 안개 배경은 몸과 따로 떼어서 본다: 붉은색이 강한 픽셀 · 어두운 회색 안개는 일단 빼고 가장 큰 덩어리를 찾는다
        r, g_, b_ = [reg[..., i].astype(int) for i in range(3)]
        red = (r > 100) & (r > 1.8 * g_) & (r > 1.6 * b_); fg = (lum >= 88) & ~red
    lab, n = ndimage.label(fg, structure=np.ones((3, 3)))
    for i, sl in enumerate(ndimage.find_objects(lab), 1):   # 가는 줄(칸 테두리 · 바닥선) · 부스러기 제거
        hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start; a = (lab[sl] == i).sum()
        if (hh <= 4 and ww >= 30) or (ww <= 4 and hh >= 30) or a < 14: fg[sl] &= ~(lab[sl] == i)
    cl = ndimage.binary_closing(fg, structure=np.ones((3, 3)), iterations=2)   # 몸 안쪽 어두운 그림자 틈을 이어서
    lab, n = ndimage.label(cl, structure=np.ones((3, 3)))
    if n == 0: return None, None
    sz = ndimage.sum(np.ones_like(lum), lab, range(1, n + 1)); order = np.argsort(-sz)
    keep = {int(order[0]) + 1}
    for j in order[1:]:   # 큰 덩어리 둘레(이펙트 조각)는 남기고, 멀리 떨어진 배경 조각은 버린다
        if (not big) and sz[j] >= max(40, sz[order[0]] * 0.01): keep.add(int(j) + 1)
    m = np.isin(lab, list(keep))
    if big:   # 몸 둘레 4칸 안의 붉은 피 · 어두운 털은 되살린다 (깃발은 멀리 있어 안 닿음)
        m = ndimage.binary_dilation(m, iterations=4) & (lum >= thr)
    m = ndimage.binary_fill_holes(m)
    reg[..., 3] = np.where(m & (lum >= 14) | (ndimage.binary_erosion(m, iterations=2) & m), 255, 0)
    im = Image.fromarray(reg); return im, im.getchannel('A').getbbox()
ROWS = {  # 이름: (y0, y1, x0, x1, 경계 대략, 창, big)
 'idle':  (332, 441, 12, 690, [116, 226, 345, 451, 567], 8, False),
 'move':  (335, 441, 696, 1444, [786, 881, 976, 1073, 1173, 1270, 1363], 8, False),
 'atk':   (492, 611, 12, 712, [108, 224, 348, 473, 591], 8, False),
 'atk2':  (485, 611, 724, 1444, [850, 982, 1122, 1207, 1329], 8, False),
 'spec':  (653, 782, 12, 790, [140, 300, 452, 572, 673], 8, True),
 'hit':   (652, 778, 802, 1444, [962, 1112, 1270], 8, False),
 'death': (822, 930, 12, 785, [128, 245, 372, 520, 645], 12, False),
 'phase': (826, 932, 802, 1444, [952, 1101, 1270], 8, False),
 'charge': (972, 1078, 12, 1444, [170, 385, 590, 820, 1050], 14, False),
}
AX = {}
frames = {}
for k, (y0, y1, x0, x1, cs, w, big) in ROWS.items():
    xs = [x0] + [valley(y0, y1, c, w) for c in cs] + [x1]; Lf = []
    for i in range(len(xs) - 1):
        im, bb = cut(xs[i], y0, xs[i + 1], y1, big=big)
        if bb is None: continue
        a = np.array(im.getchannel('A')); ys, xx = np.where(a > 0); yb = ys.max(); sel = xx[ys > yb - max(8, int((yb - ys.min()) * 0.12))]
        ax = AX.get((k, i), None); ax = float(np.median(sel)) if ax is None else ax
        im = im.crop(bb); ax -= bb[0]
        im = im.resize((max(1, round(im.width * FK)), max(1, round(im.height * FK))), Image.LANCZOS); Lf.append((im, ax * FK, im.height))
    frames[k] = Lf
meta = {}; pos = []; W = 0; y = 0
for kname, Lf in frames.items():
    cw = int(max(max(ax, im.width - ax) for im, ax, _ in Lf) * 2) + 6; ch = max(im.height for im, _, _ in Lf) + 4; meta[kname] = []
    for i, (im, ax, ay) in enumerate(Lf):
        ox = i * cw + int(cw / 2 - ax); oy = y + ch - 2 - im.height
        meta[kname].append([i * cw, y, cw, ch, cw // 2, ch - 2]); pos.append((im, ox, oy))
    W = max(W, cw * len(Lf)); y += ch
at = Image.new('RGBA', (W, y), (0, 0, 0, 0))
for im, x, yy in pos: at.alpha_composite(im, (x, yy))
os.makedirs(os.path.join(ROOT, 'src/assets/bear'), exist_ok=True); os.makedirs(os.path.join(ROOT, 'build'), exist_ok=True)
at.save(os.path.join(ROOT, 'src/assets/bear/bear.webp'), lossless=True); json.dump(meta, open(os.path.join(ROOT, 'src/assets/bear/bear.json'), 'w'))
for nm, col in (('a', (110, 110, 110, 255)), ('b', (60, 130, 90, 255))):
    b2 = Image.new('RGBA', at.size, col); b2.alpha_composite(at); d = ImageDraw.Draw(b2)
    for kn, ms in meta.items():
        for m in ms: d.ellipse([m[0] + m[4] - 2, m[1] + m[5] - 2, m[0] + m[4] + 2, m[1] + m[5] + 2], fill=(255, 0, 0, 255))
    b2.resize((b2.width * 2, b2.height * 2), Image.NEAREST).save(os.path.join(ROOT, 'build/bear_prev_%s.png' % nm))
print(at.size, {k: len(v) for k, v in meta.items()})
