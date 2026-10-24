"""파리지옥 마왕(vft) 시트 → src/assets/vft/vft.webp + vft.json
자르기 · 배경 제거(칸 테두리에서 이어진 어두운 바탕을 투명하게) · 배율 조정만. 도트는 손대지 않는다.
사용: python3 vft_build.py <시트.png>"""
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
frames['idle'] = [cut(b) for b in split(605, 349, 1435, 428, 6)]
frames['walk'] = [cut(b) for b in split(605, 473, 1435, 551, 9)]
frames['atk'] = [cut(b) for b in split(605, 596, 1435, 684, 8, win=40)]
frames['hit'] = [cut(b) for b in split(15, 943, 575, 1062, 4)]
frames['death'] = [cut(b) for b in split(590, 943, 1440, 1062, 6, win=40)]
frames['heart'] = [cut((513, 733, 572, 806), 'heart')]
frames['spore'] = [cut((1383, 742, 1432, 792), 'heart')]
trapX = [(620, 668), (680, 720), (722, 780), (782, 832), (838, 905), (910, 1012)]
frames['trap'] = [cut((x0, 728, x1, 846), 'sat') for x0, x1 in trapX]
frames = {k: [f for f in v if f is not None] for k, v in frames.items()}

# 아틀라스로 붙이기 (줄마다 가로로)
pad = 2; Wt = 1600; x = y = 0; rowH = 0; place = {}
items = [(k, i, f) for k, v in frames.items() for i, f in enumerate(v)]
for k, i, f in items:
    if x + f.width > Wt: x = 0; y += rowH + pad; rowH = 0
    place[(k, i)] = (x, y); x += f.width + pad; rowH = max(rowH, f.height)
A = Image.new('RGBA', (Wt, y + rowH), (0, 0, 0, 0)); J = {}
for k, i, f in items:
    px, py = place[(k, i)]; A.alpha_composite(f, (px, py))
    ay = f.height if k not in ('heart', 'spore') else f.height // 2
    J.setdefault(k, []).append([px, py, f.width, f.height, f.width // 2, ay])
out = os.path.join(ROOT, 'src', 'assets', 'vft'); os.makedirs(out, exist_ok=True)
A.save(os.path.join(out, 'vft.webp'), lossless=True, method=6); json.dump(J, open(os.path.join(out, 'vft.json'), 'w'), separators=(',', ':'))
print(A.size, {k: len(v) for k, v in J.items()}, os.path.getsize(os.path.join(out, 'vft.webp')) // 1024, 'KB')
bg = Image.new('RGBA', A.size, (90, 60, 110, 255)); bg.alpha_composite(A); bg.save(os.path.join(ROOT, 'build', 'vft_prev.png'))
