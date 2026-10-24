"""유령 기사(1진화) · 듀라한(최종) · 잃어버린 머리(소환체) 시트 → src/assets/dk/dk.webp + dk.json
자르기 · 배경 제거(칸 테두리에서 이어진 어두운 바탕을 투명하게) · 배율 조정만. 도트는 손대지 않는다.
사용: python3 dk_build.py <유령 기사 시트.png> <듀라한 시트.png>
키: k1_* = 유령 기사 · k2_* = 듀라한 · hd_* = 잃어버린 머리 · k2*_nh = 듀라한 몸에서 떠 있는 머리 덩어리만 가린 것(소환 중)"""
import sys, os, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
S = [np.array(Image.open(p).convert('RGB')).astype(int) for p in sys.argv[1:3]]

THR = [30, 32]; DEEP = [16, -1]; SEAL = [0, 3]   # 듀라한은 흑색 갑옷이라 바탕 판정을 낮게
CUR = [0]
def mask_dark(a, thr=None):
    thr = THR[CUR[0]] if thr is None else thr
    dark = a.max(2) <= thr
    if SEAL[CUR[0]]: dark = ~ndi.binary_closing(~dark, iterations=SEAL[CUR[0]])   # 흑색 갑옷 속 어두운 면이 팔다리 틈으로 바탕과 이어져 지워지지 않게 좁은 틈은 막고 판정
    lab, n = ndi.label(dark); edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    fg = ~np.isin(lab, list(edge))
    deep = a.max(2) <= DEEP[CUR[0]]   # 불꽃 사이에 갇힌 넓은 바탕 구멍도 투명하게 (아주 어둡고 넓은 덩어리만)
    lab3, n3 = ndi.label(deep)
    if n3:
        sz3 = ndi.sum(deep, lab3, range(1, n3 + 1)); fg &= ~np.isin(lab3, [i + 1 for i, q in enumerate(sz3) if q >= 60])
    lab2, n2 = ndi.label(fg)   # 부스러기·숫자 제거
    if n2:
        sz = ndi.sum(fg, lab2, range(1, n2 + 1)); H = fg.shape[0]
        cy = ndi.center_of_mass(fg, lab2, range(1, n2 + 1))
        fg &= ~np.isin(lab2, [i + 1 for i, s in enumerate(sz) if s < 8 or (s < 60 and cy[i][0] > H - 16)])   # 아래 칸 번호 숫자
    return unline(fg)

def alpha(a, fg):   # 바탕 쪽 어두운 빛 번짐(남색 안개)은 밝기만큼 반투명 — 밝은 윤곽이 감싼 안쪽(흑색 갑옷)은 그대로 불투명
    thr = THR[CUR[0]]; mx = a.max(2).astype(float); L = 72
    core = ndi.binary_fill_holes(ndi.binary_closing(fg & (mx > L), iterations=3))
    core = ndi.binary_dilation(core, iterations=2)
    al = np.where(fg, 255.0, 0.0); soft = fg & ~core & (mx < L)
    al[soft] = np.clip((mx[soft] - thr) / (L - thr), 0.0, 1) ** 1.3 * 255
    return al.astype(np.uint8)

def unline(fg):   # 칸 테두리선(가늘고 긴 세로·가로줄) 제거
    H, W = fg.shape
    for x in range(W):
        c = fg[:, x]
        if c.sum() >= 0.6 * H:
            l = fg[:, x - 2] if x >= 2 else np.zeros(H, bool); r = fg[:, x + 2] if x + 2 < W else np.zeros(H, bool)
            if (c & ~l & ~r).sum() > 0.4 * H: fg[:, max(0, x - 1):x + 2] &= (l | r)[:, None]
    lab, n = ndi.label(fg)
    for i, sl in enumerate(ndi.find_objects(lab)):
        if sl is None: continue
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if (h <= 4 and w >= 20) or (w <= 4 and h >= 20): fg[lab == i + 1] = False
    return fg

def valley(col, n, win=24):
    xs = np.where(col > 0)[0]; L, R = xs[0], xs[-1] + 1; step = (R - L) / n; cuts = [L]
    for i in range(1, n):
        c = int(L + i * step); lo, hi = max(L + 1, c - win), min(R - 1, c + win)
        cuts.append(lo + int(np.argmin(col[lo:hi])))
    return cuts + [R]

def row(si, x0, x1, y0, y1, n, mid=0.5, tshift=None):   # 위·아래 절반의 칸 경계를 따로 찾는다 (앞 칸의 떠 있는 머리와 뒤 칸의 칼끝이 같은 x에 겹쳐서)
    CUR[0] = si; a = S[si][y0:y1, x0:x1]; fg = mask_dark(a); H = fg.shape[0]; m = int(H * mid)
    ct = valley(fg[:m].sum(0) + 0.15 * fg[m:].sum(0), n); cb = valley(fg[m:].sum(0) + 0.15 * fg[:m].sum(0), n)
    if tshift is not None:   # 위쪽 경계 = 아래 경계 + tshift 근처의 가장 빈 세로줄 (떠 있는 머리가 몸 오른쪽 위에 붙어 있음)
        colt = fg[:m].sum(0); ct = [min(ct[0], cb[0])]
        for c in cb[1:-1]:
            lo, hi = c + tshift - 12, c + tshift + 12; ct.append(lo + int(np.argmin(colt[lo:hi])))
        ct.append(max(ct[-1] + 1, cb[-1], len(colt)))
    al = alpha(a, fg); out = []
    for i in range(n):
        k = np.zeros_like(fg); k[:m, ct[i]:ct[i + 1]] = True; k[m:, cb[i]:cb[i + 1]] = True; f = fg & k
        ys, xs = np.where(f)
        if not len(xs): out.append(None); continue
        bx0, bx1, by0, by1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        out.append(Image.fromarray(np.dstack([a.astype(np.uint8), np.where(f, al, 0).astype(np.uint8)])[by0:by1, bx0:bx1], 'RGBA'))
    return out

def rowx(si, y0, y1, xs):   # 칸 경계를 직접 정한 줄 (이웃 칸과 궤적이 많이 겹치는 줄)
    CUR[0] = si; out = []
    for i in range(len(xs) - 1):
        a = S[si][y0:y1, xs[i]:xs[i + 1]]; fg = mask_dark(a); ys, xq = np.where(fg)
        if not len(xq): out.append(None); continue
        al = alpha(a, fg); bx0, bx1, by0, by1 = xq.min(), xq.max() + 1, ys.min(), ys.max() + 1
        out.append(Image.fromarray(np.dstack([a.astype(np.uint8), np.where(fg, al, 0).astype(np.uint8)])[by0:by1, bx0:bx1], 'RGBA'))
    return out

def nohead(f):   # 듀라한 몸 프레임에서 오른쪽 위에 떠 있는 머리만 가린다 (마스크만) — 밝은 머리 덩어리를 찾아 그 둘레만 지움
    a = np.array(f); H, W = a.shape[:2]; mx = a[:, :, :3].max(2)
    br = (mx > 120) & (a[:, :, 3] > 0); br[:, :int(W * 0.45)] = False; br[int(H * 0.6):] = False
    lab, n = ndi.label(ndi.binary_closing(br, iterations=2))
    if not n: return f
    sz = ndi.sum(br, lab, range(1, n + 1)); cxs = ndi.center_of_mass(br, lab, range(1, n + 1))
    ok = [i for i in range(n) if sz[i] >= 40]
    if not ok: return f
    hb = lab == 1 + max(ok, key=lambda i: cxs[i][1])   # 가장 오른쪽 밝은 덩어리 = 떠 있는 머리
    ys, xs = np.where(hb); cx, cy = xs.mean(), ys.mean(); r = max(xs.max() - xs.min(), ys.max() - ys.min()) * 0.62 + 6
    Y, X = np.mgrid[0:H, 0:W]; m = ((X - cx) ** 2 + (Y - cy) ** 2 < r * r) & (X > cx - r * 0.55)
    a[:, :, 3][m] = 0
    return Image.fromarray(a, 'RGBA')

F = {}
F['k1_idle'] = row(0, 25, 690, 563, 670, 6)
F['k1_walk'] = row(0, 705, 1432, 563, 670, 8)
F['k1_atk'] = row(0, 20, 955, 738, 851, 8)
F['k1_hit'] = row(0, 980, 1428, 738, 851, 4)
F['k1_death'] = row(0, 890, 1430, 922, 1044, 6)
F['k2_idle'] = row(1, 20, 692, 506, 603, 6)
F['k2_walk'] = row(1, 708, 1424, 506, 603, 8, tshift=20)
F['k2_atk'] = row(1, 18, 930, 653, 745, 8)
F['k2_hit'] = row(1, 945, 1424, 653, 745, 4)
F['k2_sum'] = row(1, 18, 862, 795, 889, 8)
F['k2_death'] = rowx(1, 795, 889, [875, 967, 1057, 1142, 1220, 1340, 1430])
F['hd_idle'] = row(1, 25, 248, 970, 1040, 4)
F['hd_move'] = row(1, 255, 572, 970, 1040, 6)
F['hd_atk'] = rowx(1, 970, 1040, [575, 627, 681, 721, 761, 807, 865])
for k in ['k2_idle', 'k2_walk']: F[k + '_nh'] = [nohead(f) for f in F[k]]
F = {k: [f for f in v if f is not None] for k, v in F.items()}

pad = 2; Wt = 1600; x = y = 0; rowH = 0; place = {}
items = [(k, i, f) for k, v in F.items() for i, f in enumerate(v)]
for k, i, f in items:
    if x + f.width > Wt: x = 0; y += rowH + pad; rowH = 0
    place[(k, i)] = (x, y); x += f.width + pad; rowH = max(rowH, f.height)
A = Image.new('RGBA', (Wt, y + rowH), (0, 0, 0, 0)); J = {}
for k, i, f in items:
    px, py = place[(k, i)]; A.alpha_composite(f, (px, py))
    fa = np.array(f).astype(int); op = fa[:, :, 3] > 0
    body = op & (fa[:, :, :3].max(2) - fa[:, :, :3].min(2) < 70)   # 기준점 x = 갑옷(채도 낮은 은빛·흑색) 픽셀이 가장 몰린 세로 띠 — 칼·불꽃·머리가 한쪽으로 뻗어도 몸이 흔들리지 않게
    al = (body if body.sum() > 50 else op).sum(0).astype(float); win = min(40, len(al))
    ax = int(np.argmax(np.convolve(al, np.ones(win), 'same'))) if not k.startswith('hd') else f.width // 2
    J.setdefault(k, []).append([px, py, f.width, f.height, ax, f.height if not k.startswith('hd') else f.height // 2])
out = os.path.join(ROOT, 'src', 'assets', 'dk'); os.makedirs(out, exist_ok=True)
A.save(os.path.join(out, 'dk.webp'), lossless=True, method=6); json.dump(J, open(os.path.join(out, 'dk.json'), 'w'), separators=(',', ':'))
print(A.size, {k: len(v) for k, v in J.items()}, os.path.getsize(os.path.join(out, 'dk.webp')) // 1024, 'KB')
bg = Image.new('RGBA', A.size, (150, 90, 150, 255)); bg.alpha_composite(A); bg.save(os.path.join(ROOT, 'build', 'dk_prev.png'))
