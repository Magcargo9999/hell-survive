"""썩어버린 해군 제독 시트 → 아틀라스 (자르기·배경 제거(마스크)만, 색 수정 없음)
사용: python3 tools/atlas/adm_build.py <시트.png> → src/assets/adm/adm.{webp,json}
프레임 [x, y, 너비, 높이, 기준x(몸통 가운데), 기준y(발)] · 원본은 오른쪽을 본다(게임에서 face<0이면 뒤집음)
attack 줄은 시트에 사슬·닻·휘두름 이펙트가 번져 있어 몸통만 남긴다(닻·사슬·베기는 게임이 따로 그림) · anc = 닻 머리(시트 attack 6번 칸)"""
import sys, json, os
import numpy as np
from PIL import Image
from scipy import ndimage as nd
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'src/assets/adm'); os.makedirs(OUT, exist_ok=True)
A = np.array(Image.open(sys.argv[1]).convert('RGBA')); AL = A[:, :, 3] > 40
# 줄: (위, 아래, 경계들, 첫 칸 위 보정 y0, 몸통만 남기기)
ROWS = {
  'idle':  (28, 181, [428, 632, 830, 1038, 1238, 1432], 38, False),
  'walk':  (232, 369, [420, 558, 692, 797, 912, 1032, 1148, 1262, 1430], 240, False),
  'atk':   (410, 565, [445, 581, 713, 843, 968, 1095, 1210, 1320, 1445], 432, True),
  'sum':   (595, 762, [3, 155, 255, 360, 470, 585, 730], 611, False),
  'hit':   (630, 758, [740, 868, 995, 1128, 1252], 632, False),
  'death': (826, 928, [3, 250, 470, 665, 830, 975, 1110, 1290, 1445], 826, False),
  'cspawn': (981, 1043, [12, 120, 235, 350, 505], 981, False),
  'cfire': (981, 1043, [520, 660, 790, 925, 1100], 981, False),
  'ball':  (985, 1040, [1110, 1175, 1235, 1300, 1365, 1440], 985, False),
}
def refine(y0, y1, cells):
    occ = AL[y0:y1 - 12].sum(axis=0); c = [list(v) for v in cells]
    for i in range(len(c) - 1):
        lo, hi = c[i][1] - 18, c[i][1] + 18; seg = occ[lo:hi]; xs = np.where(seg == seg.min())[0]; v = lo + int(xs[len(xs) // 2]); c[i][1] = c[i + 1][0] = v
    return [tuple(v) for v in c]
tiles = []
for k, (y0, y1, bnd, yf, body) in ROWS.items():
    cells = [(bnd[i], bnd[i + 1]) for i in range(len(bnd) - 1)]
    if k in ('idle', 'walk', 'sum', 'hit', 'death'): cells = refine(y0, y1, cells)
    for i, (x0, x1) in enumerate(cells):
        ya = yf if i == 0 else y0
        m = AL[ya:y1, x0:x1].copy()
        lab, n = nd.label(nd.binary_dilation(m, iterations=1)); lab = lab * m
        sz = nd.sum(m, lab, range(1, n + 1)); mx = sz.max(); ok = []
        for j, sl in enumerate(nd.find_objects(lab)):
            if sl is None: continue
            w = sl[1].stop - sl[1].start; h = sl[0].stop - sl[0].start
            thin = (w <= 4 and h >= 20) or (h <= 3 and w >= 40)
            if sz[j] >= 8 and not thin and not ((sl[1].start == 0 or sl[1].stop == m.shape[1]) and sz[j] < 0.12 * mx): ok.append(j + 1)
        keep = np.isin(lab, ok)
        if body:   # 몸통만: 얇은 사슬·휘두름 이펙트·떨어진 닻을 지운다
            core = nd.binary_opening(keep, structure=np.ones((3, 3)), iterations=4)
            l2, n2 = nd.label(core)
            if n2: s2 = nd.sum(core, l2, range(1, n2 + 1)); core = l2 == (1 + int(np.argmax(s2)))
            keep = keep & nd.binary_dilation(core, iterations=9)
            lab3, n3 = nd.label(keep)
            if n3: s3 = nd.sum(keep, lab3, range(1, n3 + 1)); keep = lab3 == (1 + int(np.argmax(s3)))
        keep = nd.binary_closing(np.pad(keep, 3), structure=np.ones((3, 3)))[3:-3, 3:-3] | keep
        keep = nd.binary_fill_holes(keep) if k not in ('cspawn', 'cfire', 'ball', 'sum') else keep
        ys, xs = np.where(keep); X0, X1, Y0, Y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        if k in ('ball',): ax = (X1 - X0) / 2; ay = (Y1 - Y0) / 2
        else:
            mid = (ys >= Y0 + 0.3 * (Y1 - Y0)) & (ys <= Y0 + 0.8 * (Y1 - Y0)); ax = float(xs[mid].mean()) - X0; ay = Y1 - Y0
        t = np.zeros((Y1 - Y0, X1 - X0, 4), np.uint8); t[:, :, :3] = A[ya + Y0:ya + Y1, x0 + X0:x0 + X1, :3]; t[:, :, 3] = keep[Y0:Y1, X0:X1] * A[ya + Y0:ya + Y1, x0 + X0:x0 + X1, 3]
        if k == 'atk' and i == 5: continue   # 시트 attack 6번 칸은 몸통 없이 닻·물보라뿐 → 뺀다 (atk = 7칸: 원래 1~5·7·8)
        tiles.append((k, Image.fromarray(t), int(round(ax)), int(round(ay))))
# 닻 머리 (attack 6번 칸): 사슬 쪽(왼쪽)은 잘라낸다
ax0, ay0, ax1, ay1 = 1160, 440, 1236, 508
m = AL[ay0:ay1, ax0:ax1]; lab, n = nd.label(m); s = nd.sum(m, lab, range(1, n + 1)); keep = lab == (1 + int(np.argmax(s)))
ys, xs = np.where(keep); t = np.zeros((ys.max() - ys.min() + 1, xs.max() - xs.min() + 1, 4), np.uint8)
sub = A[ay0:ay1, ax0:ax1][ys.min():ys.max() + 1, xs.min():xs.max() + 1]; t[:, :, :3] = sub[:, :, :3]; t[:, :, 3] = keep[ys.min():ys.max() + 1, xs.min():xs.max() + 1] * sub[:, :, 3]
tiles.append(('anc', Image.fromarray(t), t.shape[1] // 2, t.shape[0] // 2))
W = 1024; x = y = rh = 0; place = []; F = {}
for k, t, ax, ay in tiles:
    if x + t.width > W: x = 0; y += rh + 2; rh = 0
    place.append((k, t, x, y, ax, ay)); x += t.width + 2; rh = max(rh, t.height)
out = Image.new('RGBA', (W, y + rh), (0, 0, 0, 0))
for k, t, x, y, ax, ay in place: out.paste(t, (x, y)); F.setdefault(k, []).append([int(v) for v in (x, y, t.width, t.height, ax, ay)])
out.save(os.path.join(OUT, 'adm.webp'), lossless=True); json.dump(F, open(os.path.join(OUT, 'adm.json'), 'w'))
print(out.size, {k: len(v) for k, v in F.items()})
bg = Image.new('RGBA', out.size, (60, 60, 80, 255)); bg.alpha_composite(out); bg.save(os.path.join(ROOT, 'build/adm/atlas_prev.png'))
