"""마하칼 루드라(지하 23~24층 마왕) 시트 → src/assets/rud/rud.webp + rud.json
자르기 + 가장자리에서 이어진 어두운 배경 제거 + 칸 정렬만 (재색칠 없음). 시트의 인게임 스프라이트는 오른쪽을 봄(대기는 정면)
프레임: idle 6 · walk 8 · atk 5 · cast 6 · hit 4 · death 3 · fin 3(최종 형태, 시트에서 더 크게 그려져 있어 FIN_K로 맞춤)
이펙트: lotus 5(꽃봉오리 → 작은 꽃 → 핀 꽃 → 큰 꽃 → 폭발) · petal 3 (패널 배경이 밝아 문턱을 높게)
사용: python3 rud_build.py <마하칼 루드라 시트.png>"""
import sys, os, json
from PIL import Image
import numpy as np
from scipy import ndimage
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
sh = Image.open(sys.argv[1]).convert('RGBA'); A = np.array(sh); L = A[..., :3].max(axis=2).astype(int)
def valley(x0, y0, y1, c, w=18):   # 대략적인 칸 경계 c 둘레에서 가장 빈 세로줄
    seg = (L[y0:y1 - 6, c - w:c + w] > 40).sum(axis=0); return c - w + int(np.argmin(seg))
ROWS = {   # (x0, y0, x1, y1, 대략 칸 경계)
 'idle':  (592, 324, 1122, 403, [668, 756, 840, 928, 1013]),
 'walk':  (592, 417, 1122, 499, [664, 728, 792, 855, 918, 982, 1045]),
 'atk':   (592, 511, 1122, 604, [688, 784, 858, 958]),
 'cast':  (592, 617, 1122, 711, [676, 761, 878, 972, 1046]),
 'hit':   (592, 723, 1122, 808, [684, 773, 867]),
 'death': (592, 822, 888, 909, [695, 786]),   # 4번째부터는 배경 탑 그림과 섞여 쓰지 않는다 (게임에서 입자로 사라짐)
}
def cut(reg, thr, keepall=False, hole=0):
    lum = reg[..., :3].max(axis=2); lab, n = ndimage.label(lum < thr)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(edge))
    if hole:   # 안쪽에 갇힌 배경색 구멍(후광 고리 안 · 팔 사이)도 지운다 — 시트 배경과 같은 아주 어두운 덩어리만
        lab3, n3 = ndimage.label(lum < hole); sz = ndimage.sum(np.ones_like(lum), lab3, range(1, n3 + 1))
        big = [i + 1 for i, v in enumerate(sz) if v >= 10]; bg |= np.isin(lab3, big)
    reg[..., 3] = np.where(bg, 0, 255)
    if not keepall:   # 가장 큰 덩어리와 가까운 것만 (옆 칸 부스러기 · 줄 제거)
        m = reg[..., 3] > 0; big = ndimage.binary_dilation(m, iterations=4); lab2, n2 = ndimage.label(big)
        if n2 > 1:
            sz = ndimage.sum(m, lab2, range(1, n2 + 1)); keep = 1 + int(np.argmax(sz)); reg[..., 3] = np.where((lab2 == keep) & m, 255, 0)
    im = Image.fromarray(reg); bb = im.getchannel('A').getbbox(); return im, bb
frames = {}
for k, (x0, y0, x1, y1, cs) in ROWS.items():
    xs = [x0] + [valley(x0, y0, y1, c) for c in cs] + [x1]; Lf = []
    for i in range(len(xs) - 1):
        a, c = xs[i], xs[i + 1]
        if k == 'death' and i == 2: a = 803   # 쓰러진 몸 왼쪽의 배경 탑 그림 빼기
        reg = A[y0:y1, a:c].copy()
        im, bb = cut(reg, 34, keepall=(k == 'atk' and i == 4) or k == 'cast')
        cx = (a + c) / 2 - a   # 칸 가운데 = 몸 가운데 (시트 칸 간격이 고르다)
        Lf.append((im.crop((0, 0, im.width, bb[3])), cx, 1.0))   # 바닥(아래)은 bbox 아래로 맞춤 · 위는 줄 위쪽 그대로
    frames[k] = Lf
# 최종 형태 3장 (시트에서 약 1.6배 크게 그려져 있다 → 인게임 줄 높이에 맞게 줄인다)
FIN = [(1138, 808, 1303, 929), (1303, 808, 1397, 929), (1397, 808, 1523, 929)]; FIN_K = 0.66; Lf = []
for b in FIN:
    reg = A[b[1]:b[3], b[0]:b[2]].copy(); im, bb = cut(reg, 46); im = im.crop((0, 0, im.width, bb[3]))
    im = im.resize((round(im.width * FIN_K), round(im.height * FIN_K)), Image.LANCZOS); Lf.append((im, im.width / 2, 1.0))
frames['fin'] = Lf
# 이펙트
FX = {'lotus': [(1229, 503, 1278, 586), (1281, 510, 1314, 586), (1309, 500, 1392, 586), (1404, 493, 1493, 586), (1512, 520, 1625, 592)],
      'petal': [(1578, 470, 1610, 500), (1517, 488, 1550, 512), (1600, 500, 1640, 525)]}
for k, L2 in FX.items():
    Lf = []
    for b in L2:
        reg = A[b[1]:b[3], b[0]:b[2]].copy(); im, bb = cut(reg, 135, keepall=(k == 'lotus'), hole=0); im = im.crop((0, 0, im.width, bb[3]))
        Lf.append((im, im.width / 2, 1.0))
    frames[k] = Lf
# 아틀라스: 그룹마다 한 줄, 칸 = 그 줄 최대 크기, 기준점 = 칸 가운데 아래
meta = {}; pos = []; W = 0; y = 0
for k, Lf in frames.items():
    cw = int(max(max(cx, im.width - cx) for im, cx, _ in Lf) * 2) + 4; ch = max(im.height for im, _, _ in Lf) + 2
    meta[k] = []
    for i, (im, cx, _) in enumerate(Lf):
        meta[k].append([i * cw, y, cw, ch, cw // 2, ch - 1]); pos.append((im, i * cw + int(cw // 2 - cx), y + ch - 1 - im.height))
    W = max(W, cw * len(Lf)); y += ch
at = Image.new('RGBA', (W, y), (0, 0, 0, 0))
for im, x, yy in pos: at.alpha_composite(im, (x, yy))
at.save(os.path.join(ROOT, 'src/assets/rud/rud.webp'), lossless=True); json.dump(meta, open(os.path.join(ROOT, 'src/assets/rud/rud.json'), 'w'))
for nm, col in (('a', (150, 150, 150, 255)), ('b', (40, 120, 60, 255))):
    bg = Image.new('RGBA', at.size, col); bg.alpha_composite(at); bg = bg.resize((bg.width * 2, bg.height * 2), Image.NEAREST); bg.save(os.path.join(ROOT, 'build/rud_prev_%s.png' % nm))
print(at.size, {k: len(v) for k, v in meta.items()})
