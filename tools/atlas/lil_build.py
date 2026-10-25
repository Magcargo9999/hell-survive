"""팔한지옥의 대공작 릴세르카 도트 시트(어두운 남색 배경) → src/assets/lil/lil.webp + lil.json (v9.22)
인게임 스프라이트 줄(대기 6 · 이동/부유 8 · 기본 공격 5 · 스킬 시전 6 · 피격 4 · 사망 4)을 자르고, 가장자리에서 이어진 어두운 배경만 지운다 (재색칠 없음)
칸 경계는 대략 위치 둘레에서 가장 빈 세로줄(valley) · 기준점 = 바닥 둘레 x 중앙값(손으로 정한 칸은 AX) · 높이 100에 맞게 FK 로 줄임(게임이 ×3 nearest)
거울(냉기의 거울 대기·피격·파괴)은 첫 번째 시트에서: python3 lil_build.py <인게임 줄 시트.png> [<캐릭터 시트.png>]"""
import sys, os, json
from PIL import Image
import numpy as np
from scipy import ndimage
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
S = Image.open(sys.argv[1]).convert('RGBA'); A = np.array(S); L = A[..., :3].max(axis=2).astype(int)
FK = 0.53
def valley(y0, y1, c, w=14):
    seg = (L[y0:y1, max(0, c - w):c + w] > 34).sum(axis=0); m = seg.min(); xs = np.where(seg == m)[0]; return max(0, c - w) + int(xs[len(xs) // 2])
def cut(x0, y0, x1, y1, thr=34, hole=22):
    reg = A[y0:y1, x0:x1].copy(); lum = reg[..., :3].max(axis=2)
    lab, n = ndimage.label(lum < thr)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(edge))
    lab3, n3 = ndimage.label(lum < hole)
    if n3:
        sz = ndimage.sum(np.ones_like(lum), lab3, range(1, n3 + 1)); bg |= np.isin(lab3, [i + 1 for i, v in enumerate(sz) if v >= 12])
    fg = ~bg
    lab2, n2 = ndimage.label(fg)   # 옆 칸에서 넘어온 작은 조각(칸 가장자리에 닿은 부스러기) 제거
    for i, sl in enumerate(ndimage.find_objects(lab2)):
        a = (lab2[sl] == i + 1).sum()
        if a < 260 and (sl[1].start == 0 or sl[1].stop == fg.shape[1]): fg[sl] &= ~(lab2[sl] == i + 1)
    reg[..., 3] = np.where(fg, 255, 0); im = Image.fromarray(reg); return im, im.getchannel('A').getbbox()
ROWS = {  # 이름: (y0, y1, x0, x1, 경계 대략, 칸 수 맞추기용 최대 창, 꼭 쓸 기준 x(없으면 바닥 중앙값))
 'idle':  (70, 280, 34, 936, [190, 328, 458, 603, 742], 12),
 'move':  (325, 515, 40, 992, [160, 297, 432, 553, 672, 770, 868], 8),
 'atk':   (565, 765, 33, 980, [185, 335, 478, 668], 14),
 'cast':  (70, 285, 1013, 1980, [1190, 1332, 1460, 1645, 1800], 14),
 'hit':   (330, 530, 1040, 1940, [1240, 1435, 1642], 12),
 'death': (570, 775, 1005, 1975, [1195, 1375, 1650], 14),
}
AX = {('atk', 3): 548, ('atk', 4): 830}   # 몸이 가려진 칸의 기준 x (시트 좌표)
frames = {}
for k, (y0, y1, x0, x1, cs, w) in ROWS.items():
    xs = [x0] + [valley(y0, y1, c, w) for c in cs] + [x1]; Lf = []
    for i in range(len(xs) - 1):
        im, bb = cut(xs[i], y0, xs[i + 1], y1)
        if bb is None: continue
        # 기준 x: 바닥 둘레(아래 14%) 의 중앙값
        a = np.array(im.getchannel('A')); ys, xx = np.where(a > 0); yb = ys.max(); sel = xx[ys > yb - max(8, int((yb - ys.min()) * 0.14))]
        ax = AX.get((k, i), None); ax = (ax - xs[i]) if ax is not None else float(np.median(sel))
        im = im.crop(bb); ax -= bb[0]; ay = im.height
        if k == 'death' and i >= 2: ax = im.width * (0.45 if i == 2 else 0.5)
        im = im.resize((max(1, round(im.width * FK)), max(1, round(im.height * FK))), Image.LANCZOS); Lf.append((im, ax * FK, ay * FK))
    frames[k] = Lf
# 첫 시트의 냉기의 거울 3칸 (있으면)
if len(sys.argv) > 2:
    S2 = Image.open(sys.argv[2]).convert('RGBA'); A2 = np.array(S2); L2 = A2[..., :3].max(axis=2).astype(int)
    MIR = [(560, 678, 638, 808), (763, 688, 848, 808)]; Lf = []   # 피격(반사) 칸은 설명용 화살표가 몸 위에 겹쳐 있어 쓰지 않는다 (흰 번쩍임으로 대신)
    for (x0, y0, x1, y1) in MIR:
        reg = A2[y0:y1, x0:x1].copy(); lum = reg[..., :3].max(axis=2); lab, n = ndimage.label(lum < 34)
        edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}; bg = np.isin(lab, list(edge)) | ((reg[..., 0].astype(int) > 170) & (reg[..., 1] < 100) & (reg[..., 2] < 120)); reg[..., 3] = np.where(bg, 0, 255)   # 시트 위 설명용 붉은 화살표도 지움
        im = Image.fromarray(reg); bb = im.getchannel('A').getbbox(); im = im.crop(bb); Lf.append((im, im.width / 2, im.height))
    frames['mirror'] = Lf
meta = {}; pos = []; W = 0; y = 0
for kname, Lf in frames.items():
    cw = int(max(max(ax, im.width - ax) for im, ax, _ in Lf) * 2) + 6; ch = max(im.height for im, _, _ in Lf) + 4; meta[kname] = []
    for i, (im, ax, ay) in enumerate(Lf):
        ox = i * cw + int(cw / 2 - ax); oy = y + ch - 2 - im.height
        meta[kname].append([i * cw, y, cw, ch, cw // 2, ch - 2]); pos.append((im, ox, oy))
    W = max(W, cw * len(Lf)); y += ch
at = Image.new('RGBA', (W, y), (0, 0, 0, 0))
for im, x, yy in pos: at.alpha_composite(im, (x, yy))
os.makedirs(os.path.join(ROOT, 'src/assets/lil'), exist_ok=True)
at.save(os.path.join(ROOT, 'src/assets/lil/lil.webp'), lossless=True); json.dump(meta, open(os.path.join(ROOT, 'src/assets/lil/lil.json'), 'w'))
for nm, col in (('a', (110, 110, 110, 255)), ('b', (60, 130, 90, 255))):
    b2 = Image.new('RGBA', at.size, col); b2.alpha_composite(at)
    # 기준점(가운데 아래)에 빨간 점
    from PIL import ImageDraw
    d = ImageDraw.Draw(b2)
    for kn, ms in meta.items():
        for m in ms: d.ellipse([m[0] + m[4] - 2, m[1] + m[5] - 2, m[0] + m[4] + 2, m[1] + m[5] + 2], fill=(255, 0, 0, 255))
    b2.save(os.path.join(ROOT, 'build/lil_prev_%s.png' % nm))
print(at.size, {k: len(v) for k, v in meta.items()})
