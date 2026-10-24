"""v8.63 타락한 원예의 여왕(지하 15층 최종 마왕) 아틀라스 — 자르기·배경 제거만 (색 수정 없음)
사용: python3 tools/atlas/qn_build.py <시트(1448×1086)>
출력 src/assets/qn/qn.webp + qn.json : 키 → [[x, y, w, h, 기준x(몸 가운데), 기준y(발)] …]"""
import sys, os, json
import numpy as np
from PIL import Image
from scipy import ndimage as nd
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'src/assets/qn'); os.makedirs(OUT, exist_ok=True)
A = np.array(Image.open(sys.argv[1]).convert('RGB')).astype(int); THR = 34
def _unline(A):   # 제목 상자·패널의 가는 분홍 테두리선(두께 3px 이하, 길이 28px 이상)만 지운다 — 그림은 건드리지 않는다
    R, G, B = A[:, :, 0], A[:, :, 1], A[:, :, 2]; pk = (R > 110) & (G < 110) & (R > B * 0.9) & (R - G > 50)
    out = np.zeros_like(pk)
    for ax_ in (0, 1):
        M = pk if ax_ == 0 else pk.T; o = out if ax_ == 0 else out.T
        H, Wd = M.shape
        for y in range(H):
            row = M[y]; x = 0
            while x < Wd:
                if not row[x]: x += 1; continue
                s0 = x
                while x < Wd and row[x]: x += 1
                if x - s0 >= 28:
                    ab = M[max(0, y - 3), s0:x].mean() if y >= 3 else 0; be = M[min(H - 1, y + 3), s0:x].mean() if y + 3 < H else 0
                    if ab < 0.3 and be < 0.3:
                        for yy in range(max(0, y - 1), min(H, y + 2)): o[yy, s0:x] = True
    A[out] = 0
_unline(A)
for x_ in range(818, 846):   # 제목 상자 오른쪽 세로선의 짧은 끄트머리
    col = A[215:640, x_]; pkc = (col[:, 0] > 110) & (col[:, 1] < 110) & (col[:, 0] - col[:, 1] > 50)
    side = ((A[215:640, x_ - 3, 0] > 110) & (A[215:640, x_ - 3, 1] < 110)) | ((A[215:640, x_ + 3, 0] > 110) & (A[215:640, x_ + 3, 1] < 110))
    A[215:640, x_][pkc & ~side] = 0
def cut(x0, y0, x1, y1, keep_all=False):
    sub = A[y0:y1, x0:x1]; m = sub.max(2) > THR
    lab, n = nd.label(m, structure=np.ones((3, 3))); assert n, (x0, y0)
    sz = nd.sum(m, lab, range(1, n + 1)); mx = sz.max(); ok = []
    for i, sl in enumerate(nd.find_objects(lab)):
        edge = sl[1].start == 0 or sl[1].stop == m.shape[1] or sl[0].start == 0
        if sz[i] < 3: continue
        if edge and sz[i] < 0.12 * mx and not keep_all: continue
        h_, w_ = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if sz[i] < mx and max(h_, w_) > 18 and sz[i] / (h_ * w_) < 0.12: continue   # 제목 상자 테두리(가는 선)
        if sz[i] < mx and min(h_, w_) <= 3 and max(h_, w_) > 14: continue
        ok.append(i + 1)
    k = nd.binary_fill_holes(np.isin(lab, ok)); big = lab == (int(np.argmax(sz)) + 1)
    ys, xs = np.where(k); by, bx = np.where(big)
    X0, X1, Y0, Y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    t = np.zeros((Y1 - Y0, X1 - X0, 4), np.uint8); t[:, :, :3] = sub[Y0:Y1, X0:X1]; t[:, :, 3] = k[Y0:Y1, X0:X1] * 255
    return Image.fromarray(t), int(round((bx.min() + bx.max()) / 2)) - X0, int(by.max() + 1) - Y0
def valleys(y0, y1, bounds, w=22):
    occ = (A[y0:y1].max(2) > THR).sum(0); b = list(bounds)
    for i in range(1, len(b) - 1):
        lo, hi = b[i] - w, b[i] + w; seg = occ[lo:hi]; xs = np.where(seg == seg.min())[0]; b[i] = lo + int(xs[len(xs) // 2])
    return b
T = []   # (키, 그림, ax, ay)
ROWS = {   # 몸통 줄: (y0, y1, 칸 경계) — 제목 상자는 칸 밖(왼쪽 위)
  'idle':  (232, 310, [760, 882, 990, 1100, 1212, 1322, 1430]),
  'walk':  (326, 406, [735, 830, 928, 1022, 1120, 1225, 1330, 1432]),
  'atk':   (440, 508, [735, 838, 950, 1065, 1185, 1305, 1432]),
  'hit':   (528, 596, [780, 905, 1052, 1195]),
  'death': (612, 690, [728, 890, 1008, 1132, 1262, 1436]),
}
for k, (y0, y1, b) in ROWS.items():
    b = valleys(y0, y1, b) if k not in ('hit',) else b
    for i in range(len(b) - 1):
        x0, x1 = b[i], b[i + 1]
        if k == 'hit' and i > 0: x0 += 24   # 화살표 빼기
        T.append((k,) + cut(x0, y0, x1, y1))
BOX = {   # 패턴·소환물 조각 (x0, y0, x1, y1)
  'spore': [(272, 752, 322, 778)], 'orb': [(436, 738, 466, 768)],
  'sack': [(18, 852, 92, 942), (103, 852, 177, 942), (198, 852, 272, 942), (288, 848, 372, 944), (382, 848, 478, 944)],
  'root': [(973, 742, 1062, 830), (1065, 742, 1154, 830), (1158, 728, 1208, 830), (1213, 730, 1282, 830)],
  'pool': [(1133, 866, 1212, 912), (1222, 862, 1308, 914), (1292, 852, 1432, 944)],
  'ms': [(60, 1000, 100, 1043)], 'mm': [(143, 993, 190, 1043)], 'mb': [(218, 980, 280, 1045)], 'mbp': [(295, 975, 367, 1052)],
  'lotus': [(503, 866, 645, 946)], 'hpil': [(836, 852, 950, 946)],
  'fxg': [(718, 975, 782, 1065)], 'fxp': [(798, 975, 866, 1065)], 'fxa': [(958, 970, 1052, 1068)], 'fxm': [(1348, 965, 1428, 1068)],
}
for k, L in BOX.items():
    for bx in L: T.append((k,) + cut(*bx))
W = 1024; x = y = rh = 0; place = []
for k, t, ax, ay in T:
    if x + t.width > W: x = 0; y += rh + 2; rh = 0
    place.append((k, t, x, y, ax, ay)); x += t.width + 2; rh = max(rh, t.height)
out = Image.new('RGBA', (W, y + rh), (0, 0, 0, 0)); F = {}
for k, t, x, y, ax, ay in place: out.paste(t, (x, y)); F.setdefault(k, []).append([int(v) for v in (x, y, t.width, t.height, ax, ay)])
out.save(os.path.join(OUT, 'qn.webp'), lossless=True, method=6); json.dump(F, open(os.path.join(OUT, 'qn.json'), 'w'), separators=(',', ':'))
print(out.size, {k: [(f[2], f[3]) for f in v] for k, v in F.items()})
bg = Image.new('RGBA', out.size, (70, 60, 90, 255)); bg.alpha_composite(out); bg.resize((out.width * 2, out.height * 2), Image.NEAREST).save(os.path.join(ROOT, 'build/qn_prev.png'))
