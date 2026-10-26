"""지옥의 화염 호랑이(tig) 이펙트·기믹 도트: 이펙트 시트(붉은 그라데이션 배경) → src/assets/tig/tigfx.webp + tigfx.json
사용법: python3 tools/atlas/tigfx_build.py <이펙트 시트.png> [출력폴더]
자르기 · 배경 제거 · 1/2 축소만 (재색칠 없음) — 칸마다 테두리 색으로 배경 그라데이션(쿤스 패치)을 세우고, 배경과 색 차이만큼 투명도를 준다.
글씨(설명 문구)는 자르는 상자에서 뺐다."""
import os, sys, json
import numpy as np
from PIL import Image
from scipy import ndimage
SRC = sys.argv[1] if len(sys.argv) > 1 else 'build/tig/fx.png'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'src/assets/tig'
os.makedirs(OUT, exist_ok=True)
A = np.array(Image.open(SRC).convert('RGB')).astype(float)
K = 2
BOX = {   # 이름: [(x0, y0, x1, y1), …]  (시트 좌표)
    'cross': [(10, 38, 134, 152), (145, 38, 302, 160), (308, 18, 518, 162), (520, 22, 698, 170)],   # 대기 · 회전 · 불 뿜기 · 회전 루프
'cring': [(822, 62, 968, 140)], 'jet': [(976, 40, 1246, 165)],
    'cwarn': [(1256, 20, 1382, 158)], 'czone': [(1386, 58, 1522, 152)],
    'cvanish': [(12, 238, 148, 365), (155, 240, 235, 360), (240, 240, 320, 360)],
    'stun': [(338, 228, 542, 380)],
    'guard': [(570, 248, 682, 368), (706, 240, 836, 368), (856, 234, 966, 370)],
    'counter': [(982, 266, 1060, 352), (1076, 276, 1182, 352), (1192, 246, 1345, 356), (1352, 214, 1526, 362)],
    'dwarn': [(8, 514, 156, 563)], 'ghost': [(1076, 434, 1190, 562)], 'burst': [(1192, 438, 1294, 562)],
    'turn': [(1288, 452, 1381, 552)], 'land': [(1382, 438, 1526, 562)],
    'sxwarn': [(5, 686, 170, 792)], 'sxdash': [(198, 656, 338, 764)], 'grab': [(352, 638, 470, 768)],
    'jump': [(458, 612, 596, 752)], 'slam': [(590, 640, 764, 772)], 'quake': [(766, 614, 944, 782)],
    'safe': [(956, 648, 1110, 762)], 'danger': [(1116, 656, 1270, 764)], 'ghit': [(1292, 648, 1370, 770)], 'resid': [(1442, 658, 1526, 770)],
    'beads': [(10, 862, 206, 972)], 'phase': [(220, 866, 402, 972)],
    'rstr': [(628, 866, 656, 964)], 'rzig': [(695, 866, 802, 962)], 'rtri': [(826, 866, 915, 962)], 'rx': [(922, 866, 1010, 962)], 'rcurve': [(1016, 866, 1120, 962)],
    'spark': [(1132, 876, 1200, 960)], 'crack': [(1216, 868, 1305, 960)], 'smoke': [(1306, 856, 1410, 962)],
}
SOLID = {'phase'}   # 사각형 그림 그대로 (배경 제거 안 함)

def cut(x0, y0, x1, y1, solid=False):
    c = A[y0:y1, x0:x1]; h, w = c.shape[:2]
    if solid: al = np.full((h, w), 255.0)
    else:
        sm = lambda v: ndimage.uniform_filter1d(v, 9, axis=0)
        T, Bt, L, Rt = sm(c[0]), sm(c[-1]), sm(c[:, 0]), sm(c[:, -1])
        u = np.linspace(0, 1, w)[None, :, None]; v = np.linspace(0, 1, h)[:, None, None]
        bg = (1 - v) * T[None] + v * Bt[None] + (1 - u) * L[:, None] + u * Rt[:, None] \
             - ((1 - u) * (1 - v) * c[0, 0] + u * (1 - v) * c[0, -1] + (1 - u) * v * c[-1, 0] + u * v * c[-1, -1])
        d = np.sqrt(((c - bg) ** 2).sum(2))
        for _ in range(3):   # 배경 다시 세우기: 배경으로 본 곳만 넓게 흐려서 (정규화 합성곱) 칸 안의 굽은 그라데이션을 따라간다
            wgt = (d < 30).astype(float)[..., None]
            bg = ndimage.gaussian_filter(c * wgt, (14, 14, 0)) / np.maximum(ndimage.gaussian_filter(wgt, (14, 14, 0)), 1e-3)
            d = np.sqrt(((c - bg) ** 2).sum(2))
        al = np.clip((d - 24) / 40, 0, 1) * 255
        lab, n = ndimage.label(al > 60)   # 작은 부스러기 지움
        if n:
            sz = ndimage.sum(np.ones_like(al), lab, range(1, n + 1)); keep = np.isin(lab, 1 + np.nonzero(sz >= 12)[0])
            al = al * ndimage.binary_dilation(keep, iterations=3)
    ys, xs = np.nonzero(al > 8); ya, yb, xa, xb = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    im = Image.fromarray(np.dstack([c[ya:yb, xa:xb], al[ya:yb, xa:xb]]).astype(np.uint8), 'RGBA')
    return im.resize((max(1, round(im.width / K)), max(1, round(im.height / K))), Image.LANCZOS)

ims = {k: [cut(*b, solid=k in SOLID) for b in L] for k, L in BOX.items()}
# 선반 쌓기
Wd = 640; x = y = sh = 0; meta = {}; place = []
for k, L in ims.items():
    meta[k] = []
    for im in L:
        if x + im.width > Wd: x = 0; y += sh + 1; sh = 0
        place.append((im, x, y)); meta[k].append([x, y, im.width, im.height]); x += im.width + 1; sh = max(sh, im.height)
at = Image.new('RGBA', (Wd, y + sh + 1))
for im, px, py in place: at.paste(im, (px, py))
at.save(os.path.join(OUT, 'tigfx.webp'), lossless=True); json.dump(meta, open(os.path.join(OUT, 'tigfx.json'), 'w'))
pv = Image.new('RGBA', (at.width * 2, at.height * 2), (30, 20, 40, 255)); pv.alpha_composite(at.resize((at.width * 2, at.height * 2), Image.NEAREST)); pv.save('build/tigfx_prev.png')
print(at.size, {k: len(v) for k, v in meta.items()})
