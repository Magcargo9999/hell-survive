"""v10.57 타락천사 새 도트(리비주얼) → src/assets/an3/an3.webp (몸) · an3fx.webp (이펙트) + 프레임 표 build/an3/an3.json
받은 시트 7장(투명 배경 PNG): 자르기 · 아주 옅은 배경 잡티(알파 < 14) 제거만 (재색칠 · 배율 없음)
사용: python3 tools/atlas/an3_build.py <몸1> <몸2> <몸3> <이펙트D> <이펙트E(원진)> <이펙트F(후광 방패)> <이펙트G(빛기둥)>"""
import sys, json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
A, B, C, D, E, F, G = sys.argv[1:8]
OUT = 'src/assets/an3/'
def load(f):
    a = np.array(Image.open(f).convert('RGBA')).copy(); a[..., 3] = np.where(a[..., 3] < 14, 0, a[..., 3]); return a
def keep_main(al, gap=22, thr=30):   # 몸 칸: 옆 칸에서 넘어온 깃털 끝은 버린다
    m = al > thr; lab, n = ndi.label(m, structure=np.ones((3, 3)))
    if n < 2: return al
    sz = ndi.sum(m, lab, range(1, n + 1)); main = ndi.binary_dilation(lab == (np.argmax(sz) + 1), iterations=gap)
    keep = set(np.unique(lab[main & m])) - {0}; km = np.isin(lab, list(keep)); near = ndi.binary_dilation(km, iterations=4)
    out = al.copy(); out[m & ~km] = 0; out[(al > 0) & ~m & ~near] = 0; return out
def body_row(a, y0, y1, n, cuts=None, keep=True, float_=False):
    band = a[y0:y1]; col = np.convolve((band[..., 3] > 40).sum(0).astype(float), np.ones(7) / 7, 'same')
    if cuts is None:
        nz = np.where(col > 0)[0]; L, R = nz[0], nz[-1] + 1; win = int((R - L) / n * 0.3)
        cuts = [L] + [int(np.argmin(col[c - win:c + win]) + c - win) for c in [round(L + i * (R - L) / n) for i in range(1, n)]] + [R]
    out = []
    for j in range(n):
        c = band[:, cuts[j]:cuts[j + 1]].copy()
        if keep: c[..., 3] = keep_main(c[..., 3])
        ys, xs = np.where(c[..., 3] > 20); c = c[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        op = c[..., 3] > 160; yy, xx = np.where(op); bot = int(np.percentile(yy, 99.6))
        if float_: ax = c.shape[1] / 2
        else: low = op[int(bot - (bot - yy.min()) * 0.14):bot + 1]; ax = float(np.median(np.where(low)[1]))
        out.append((c, ax, bot))
    return out
def fx_cells(a, cells, ground=False):   # 이펙트: 덩어리(알파 > 12)를 무게중심이 들어간 칸에 넣는다 · 칸보다 많이 넓은 덩어리만 칸 경계에서 자른다
    m = a[..., 3] > 0; lab, n = ndi.label(ndi.binary_dilation(m, iterations=2)); lab[~m] = 0
    objs = ndi.find_objects(lab); com = ndi.center_of_mass(m, lab, range(1, n + 1)); res = []
    for (x0, x1, y0, y1) in cells:
        res.append(np.zeros(a.shape[:2], bool))
    for i, sl in enumerate(objs, 1):
        if sl is None: continue
        cy, cx = com[i - 1]; mi = lab[sl] == i; w = sl[1].stop - sl[1].start
        for k, (x0, x1, y0, y1) in enumerate(cells):
            if not (x0 <= cx < x1 and y0 <= cy < y1): continue
            if w > (x1 - x0) * 1.25:   # 겹친 덩어리: 같은 줄의 칸 경계로 나눈다
                for kk, (u0, u1, v0, v1) in enumerate(cells):
                    if v0 <= cy < v1:
                        sub = np.zeros_like(mi); xs = np.arange(sl[1].start, sl[1].stop); sub[:, (xs >= u0) & (xs < u1)] = True
                        res[kk][sl] |= mi & sub
            else: res[k][sl] |= mi
            break
    out = []
    for r in res:
        ys, xs = np.where(r)
        if not len(ys): out.append(None); continue
        c = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy(); c[..., 3] = np.where(r[ys.min():ys.max() + 1, xs.min():xs.max() + 1], c[..., 3], 0)
        out.append((c, c.shape[1] / 2, c.shape[0] if ground else c.shape[0] / 2))
    return out
def row_cells(cuts, y0, y1): return [(cuts[i], cuts[i + 1], y0, y1) for i in range(len(cuts) - 1)]

S1, S2, S3 = load(A), load(B), load(C)
Gb = {}
Gb['idle'] = body_row(S1, 40, 300, 8); Gb['dash'] = body_row(S1, 330, 540, 8); Gb['slash'] = body_row(S1, 560, 790, 8); Gb['thrust'] = body_row(S1, 810, 1050, 6)
Gb['cast0'] = body_row(S2, 0, 212, 4); Gb['cast'] = body_row(S2, 212, 445, 6)
Gb['blink'] = body_row(S2, 440, 655, 4, cuts=[0, 300, 600, 940, 1448], keep=False)
Gb['hit'] = body_row(S2, 655, 862, 6); Gb['death'] = body_row(S2, 860, 1080, 8)
Gb['trans'] = body_row(S3, 30, 320, 8); Gb['float'] = body_row(S3, 330, 640, 4, float_=True); Gb['idle2'] = body_row(S3, 650, 950, 6)
SD, SE, SF, SG = load(D), load(E), load(F), load(G)
X = {}
d1 = fx_cells(SD, row_cells([566, 703, 845, 965, 1073, 1168, 1272, 1448], 15, 200))
X['sg'] = [d1[0]]; X['sr'] = [d1[1]]; X['gb'] = d1[2:]
X['gp'] = fx_cells(SD, row_cells([40, 260, 500, 730, 1065, 1400], 399, 585), ground=True)
d4 = fx_cells(SD, [(0, 236, 588, 770), (236, 487, 588, 770), (487, 805, 588, 770), (805, 1060, 588, 770), (1060, 1200, 588, 770), (1200, 1290, 588, 770), (1290, 1448, 588, 770)])
X['db'] = d4[0:3]; X['fe'] = [d4[3]]; X['sp'] = d4[4:7]
X['ob'] = fx_cells(SD, row_cells([0, 137, 282, 442, 607, 777, 947, 1100, 1257, 1448], 770, 909))
X['ow'] = fx_cells(SD, row_cells([0, 145, 290, 447, 615, 782, 950, 1117, 1275, 1448], 909, 1086))
X['cs'] = fx_cells(SE, row_cells([0, 430, 820, 1402], 0, 345))
X['wr'] = fx_cells(SE, row_cells([0, 380, 683, 985, 1402], 345, 515))
X['pb'] = fx_cells(SE, row_cells([0, 470, 860, 1402], 515, 800), ground=True)
X['bu'] = fx_cells(SE, row_cells([0, 232, 478, 767, 1040, 1402], 800, 1122), ground=True)
X['hg'] = fx_cells(SF, row_cells([0, 280, 557, 847, 1199], 0, 268))
X['hf'] = fx_cells(SF, [(300, 900, 268, 640)]); X['hs'] = fx_cells(SF, [(400, 800, 640, 985)])
X['hx'] = fx_cells(SF, row_cells([0, 245, 488, 738, 980, 1199], 985, 1312))
X['mk'] = fx_cells(SG, row_cells([0, 365, 668, 960, 1341], 0, 292), ground=True)
X['mr'] = fx_cells(SG, row_cells([0, 350, 637, 933, 1341], 292, 580), ground=True)
X['mb'] = fx_cells(SG, row_cells([0, 250, 499, 783, 1050, 1341], 580, 900), ground=True)
X['mf'] = fx_cells(SG, row_cells([0, 360, 665, 970, 1341], 900, 1173), ground=True)
for k, L in X.items():
    bad = [i for i, f in enumerate(L) if f is None]
    if bad: print('빈 칸', k, bad)
    X[k] = [f for f in L if f is not None]

def pack(Dd, wmax):
    x = y = rh = 0; meta = {}; place = []
    for k, L in Dd.items():
        meta[k] = []
        for f, ax, ay in L:
            h, w = f.shape[:2]
            if x + w > wmax: x = 0; y += rh + 2; rh = 0
            place.append((f, x, y)); meta[k].append([x, y, w, h, round(float(ax), 1), round(float(ay), 1)]); x += w + 2; rh = max(rh, h)
    can = np.zeros((y + rh, wmax, 4), np.uint8)
    for f, px, py in place: can[py:py + f.shape[0], px:px + f.shape[1]] = f
    used = max(m[0] + m[2] for L in meta.values() for m in L)
    return Image.fromarray(can[:, :used]), meta
im, mb = pack(Gb, 3000); im.save(OUT + 'an3.webp', quality=90, alpha_quality=100, method=6); im.save('build/an3/body.png')
im2, mx = pack(X, 3000); im2.save(OUT + 'an3fx.webp', quality=90, alpha_quality=100, method=6); im2.save('build/an3/fx.png')
json.dump({'body': mb, 'fx': mx}, open('build/an3/an3.json', 'w'), separators=(',', ':'))
print('body', im.size, {k: len(v) for k, v in mb.items()}); print('fx', im2.size, {k: len(v) for k, v in mx.items()})
