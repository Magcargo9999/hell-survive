"""타락한 어인왕(kng) 시트 → src/assets/kng/kng.webp + kng.json
자르기 · 배경 제거(칸 테두리에서 이어진 어두운 바탕을 투명하게) · 배율 조정만. 도트는 손대지 않는다.
사용: python3 kng_build.py <시트.png>"""
import sys, os, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
src = np.array(Image.open(sys.argv[1]).convert('RGB')).astype(int)

def mask_dark(a, thr=34):
    dark = a.max(2) <= thr
    lab, n = ndi.label(dark); edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    fg = ~np.isin(lab, list(edge))
    deep = a.max(2) <= 20   # 물보라 사이에 갇힌 넓은 바탕(구멍)도 투명하게: 아주 어둡고 넓은 덩어리만
    lab3, n3 = ndi.label(deep)
    if n3:
        sz3 = ndi.sum(deep, lab3, range(1, n3 + 1)); fg &= ~np.isin(lab3, [i + 1 for i, q in enumerate(sz3) if q >= 70])
    lab2, n2 = ndi.label(fg)   # 1~2px 부스러기 제거
    if n2:
        sz = ndi.sum(fg, lab2, range(1, n2 + 1)); small = np.isin(lab2, [i + 1 for i, s in enumerate(sz) if s < 6]); fg &= ~small
    return unline(fg)

def unline(fg):   # 칸 테두리선(가늘고 긴 가로·세로줄) 제거
    lab, n = ndi.label(fg)
    for i, sl in enumerate(ndi.find_objects(lab)):
        if sl is None: continue
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if (h <= 4 and w >= 20) or (w <= 4 and h >= 20): fg[lab == i + 1] = False
    H, W = fg.shape   # 스프라이트에 붙은 테두리선: 자른 칸의 가장자리 몇 줄만 본다
    for y in list(range(0, 9)) + list(range(H - 6, H)):
        if fg[y].sum() >= 0.3 * W and (fg[y].sum() - fg[min(H - 1, y + 3)].sum() > 0.2 * W or fg[y].sum() - fg[max(0, y - 3)].sum() > 0.2 * W): fg[y] = False
    for x in list(range(0, 5)) + list(range(W - 5, W)):
        if fg[:, x].sum() >= 0.5 * H: fg[:, x] = False
    lab, n = ndi.label(fg)
    if n:
        sz = ndi.sum(fg, lab, range(1, n + 1)); fg &= ~np.isin(lab, [i + 1 for i, q in enumerate(sz) if q < 6])
    return fg

def mask_heart(a):   # 붉은 빛 번짐 위 하트: 밝고 채도 높은 덩어리만
    mx, mn = a.max(2), a.min(2); fg = (mx > 120) & ((mx - mn) > 60)
    fg = ndi.binary_closing(fg, iterations=2); lab, n = ndi.label(fg)
    if n: sz = ndi.sum(fg, lab, range(1, n + 1)); fg = lab == 1 + int(np.argmax(sz)); fg = ndi.binary_fill_holes(fg)
    return fg

def mask_sat(a, sat=46, keep_largest=True):   # 바위 배경 위 덫: 채도 높은 부분만 + 가장 큰 덩어리
    mx, mn = a.max(2), a.min(2); fg = ((mx - mn) > sat) | (mx > 170)
    fg = ndi.binary_closing(fg, iterations=1)
    lab, n = ndi.label(fg)
    if n and keep_largest:
        sz = ndi.sum(fg, lab, range(1, n + 1)); big = 1 + int(np.argmax(sz)); fg = lab == big
        fg = ndi.binary_fill_holes(fg)
    return fg

def split(x0, y0, x1, y1, n, win=26):
    a = src[y0:y1, x0:x1]; fg = mask_dark(a); col = fg.sum(0)
    xs = np.where(col > 0)[0]; L, R = xs[0], xs[-1] + 1; step = (R - L) / n; cuts = [L]
    for i in range(1, n):
        c = int(L + i * step); lo, hi = max(L + 1, c - win), min(R - 1, c + win)
        cuts.append(lo + int(np.argmin(col[lo:hi])))
    cuts.append(R)
    return [(x0 + cuts[i], y0, x0 + cuts[i + 1], y1) for i in range(n)]

def cut(box, mode='dark'):
    x0, y0, x1, y1 = box; a = src[y0:y1, x0:x1]
    fg = mask_dark(a) if mode == 'dark' else mask_heart(a) if mode == 'heart' else mask_sat(a)
    ys, xs = np.where(fg)
    if not len(xs): return None
    bx0, bx1, by0, by1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    rgba = np.dstack([a, np.where(fg, 255, 0)]).astype(np.uint8)[by0:by1, bx0:bx1]
    return Image.fromarray(rgba, 'RGBA')

frames = {}
X0, X1 = 568, 1530
frames['idle'] = [cut(b) for b in split(X0, 300, X1, 384, 6)]
def cuts(y0, y1, xs): return [cut((xs[i], y0, xs[i + 1], y1)) for i in range(len(xs) - 1)]
# 시트의 프레임은 물보라·창이 이웃 칸까지 겹쳐 그려져 있어서, 칸 경계는 몸통 사이 빈 곳(눈으로 확인한 x)으로 직접 정한다
frames['walk'] = cuts(387, 456, [560, 705, 839, 990, 1077, 1212, 1364, 1521])
frames['atk'] = cuts(459, 533, [560, 702, 833, 945, 1108, 1240, 1343, 1521])
frames['skill'] = cuts(536, 622, [572, 735, 916, 1050, 1262, 1398, 1521])
frames['hit'] = [cut(b) for b in [(574, 625, 708, 680), (725, 625, 840, 680), (893, 625, 1029, 680), (1039, 625, 1193, 680), (1225, 625, 1340, 680)]]
frames['death'] = cuts(683, 745, [560, 699, 867, 1056, 1309, 1525])
frames = {k: [f for f in v if f is not None] for k, v in frames.items()}

pad = 2; Wt = 1400; x = y = 0; rowH = 0; place = {}
items = [(k, i, f) for k, v in frames.items() for i, f in enumerate(v)]
for k, i, f in items:
    if x + f.width > Wt: x = 0; y += rowH + pad; rowH = 0
    place[(k, i)] = (x, y); x += f.width + pad; rowH = max(rowH, f.height)
A = Image.new('RGBA', (Wt, y + rowH), (0, 0, 0, 0)); J = {}
for k, i, f in items:
    px, py = place[(k, i)]; A.alpha_composite(f, (px, py))
    fa = np.array(f).astype(int); al = ((fa[:, :, 3] > 0) & ((fa[:, :, 0] > fa[:, :, 2] - 10) | (fa[:, :, :3].min(2) > 150))).sum(0).astype(float); win = min(50, len(al))   # 기준점 x = 몸통(불투명 픽셀이 가장 몰린 세로 띠)의 가운데 — (붉은 망토·흰 털 = 파랗지 않은 픽셀) 물보라·창이 한쪽으로 뻗어도 몸이 흔들리지 않게
    ax = int(np.argmax(np.convolve(al, np.ones(win), 'same')))
    J.setdefault(k, []).append([px, py, f.width, f.height, ax, f.height])
out = os.path.join(ROOT, 'src', 'assets', 'kng'); os.makedirs(out, exist_ok=True)
A.save(os.path.join(out, 'kng.webp'), lossless=True, method=6); json.dump(J, open(os.path.join(out, 'kng.json'), 'w'), separators=(',', ':'))
print(A.size, {k: len(v) for k, v in J.items()}, os.path.getsize(os.path.join(out, 'kng.webp')) // 1024, 'KB')
bg = Image.new('RGBA', A.size, (150, 90, 150, 255)); bg.alpha_composite(A); bg.save(os.path.join(ROOT, 'build', 'kng_prev.png'))
