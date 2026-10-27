"""심해의 시체고래(whl) 이펙트 도트: 이펙트 시트(남색 배경) → src/assets/whlfx/whlfx.webp + whlfx.json
사용법: python3 tools/atlas/whlfx_build.py <이펙트 시트.png> [출력폴더]
자르기 · 배경 제거 · 1/2 축소만 (재색칠 없음) — 칸마다 테두리 색으로 배경 그라데이션(쿤스 패치)을 세우고, 배경과 색 차이만큼 투명도를 준다.
글씨(설명 문구)는 자르는 상자에서 뺐다."""
import os, sys, json
import numpy as np
from PIL import Image
from scipy import ndimage
SRC = sys.argv[1] if len(sys.argv) > 1 else 'build/whl/fx.png'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'src/assets/whlfx'
os.makedirs(OUT, exist_ok=True)
A = np.array(Image.open(SRC).convert('RGB')).astype(float)
K = 1
BOX = {   # 이름: [(x0, y0, x1, y1), …]  (시트 좌표 · 설명 글씨 줄은 뺐다)
    'breath': [(135, 55, 300, 135), (300, 55, 470, 135), (555, 55, 720, 135), (880, 48, 1120, 142), (1240, 45, 1435, 140)],
    'bone': [(12, 225, 70, 318), (80, 215, 150, 318), (150, 235, 225, 318), (228, 225, 312, 318), (315, 205, 412, 318), (414, 205, 545, 318), (545, 210, 665, 318), (668, 225, 765, 318)],
    'quake': [(795, 205, 895, 322), (895, 205, 1000, 322), (1030, 225, 1150, 322), (1150, 215, 1290, 322), (1295, 225, 1435, 322)],
    'vortex': [(12, 440, 98, 560), (102, 440, 192, 560), (205, 425, 325, 560), (335, 420, 505, 560), (518, 405, 765, 560), (772, 435, 910, 560)],
    'warn': [(935, 438, 1032, 500), (1045, 425, 1165, 500), (1172, 425, 1305, 500), (1315, 425, 1435, 500)],
    'emerge': [(935, 570, 1032, 640), (1035, 548, 1140, 640), (1140, 535, 1250, 640), (1252, 520, 1425, 640)],
    'wave': [(12, 650, 100, 757), (100, 640, 300, 757), (300, 640, 500, 757), (500, 640, 740, 757), (720, 635, 960, 757), (960, 665, 1130, 757), (1130, 670, 1440, 757)],
    'chain': [(12, 810, 100, 908), (100, 810, 490, 908), (490, 810, 605, 908), (605, 810, 735, 908), (775, 810, 1000, 908), (1015, 810, 1325, 908), (1327, 810, 1435, 908)],
    'drop': [(20, 972, 55, 1045), (65, 972, 108, 1045), (118, 972, 165, 1045), (178, 972, 225, 1045), (232, 972, 285, 1045), (295, 972, 345, 1045), (352, 972, 400, 1045), (410, 972, 470, 1045), (478, 972, 525, 1045), (532, 972, 580, 1045), (590, 972, 640, 1045), (645, 972, 700, 1045), (705, 972, 760, 1045), (770, 972, 835, 1045), (850, 972, 900, 1045), (920, 972, 995, 1045)],
    'soul': [(1037, 972, 1075, 1045), (1097, 972, 1135, 1045), (1155, 972, 1200, 1045), (1230, 972, 1280, 1045), (1300, 972, 1375, 1045), (1395, 972, 1435, 1045)],
}
SOLID = set()   # 사각형 그림 그대로 (배경 제거 안 함)

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
        for yy in range(h):   # 판 테두리 가는 줄 지움
            if (yy < 8 or yy > h - 9) and (al[yy] > 60).mean() > 0.55: al[max(0, yy - 1):yy + 2] = 0
        for xx in range(w):
            if (xx < 8 or xx > w - 9) and (al[:, xx] > 60).mean() > 0.55: al[:, max(0, xx - 1):xx + 2] = 0
        lab, n = ndimage.label(al > 60)   # 작은 부스러기 지움
        if n:
            sz = ndimage.sum(np.ones_like(al), lab, range(1, n + 1)); keep = np.isin(lab, 1 + np.nonzero(sz >= 12)[0])
            al = al * ndimage.binary_dilation(keep, iterations=3)
    ys, xs = np.nonzero(al > 8); ya, yb, xa, xb = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    im = Image.fromarray(np.dstack([c[ya:yb, xa:xb], al[ya:yb, xa:xb]]).astype(np.uint8), 'RGBA')
    return im.resize((max(1, round(im.width / K)), max(1, round(im.height / K))), Image.LANCZOS)

ims = {k: [cut(*b, solid=k in SOLID) for b in L] for k, L in BOX.items()}
# 선반 쌓기
Wd = 1400; x = y = sh = 0; meta = {}; place = []
for k, L in ims.items():
    meta[k] = []
    for im in L:
        if x + im.width > Wd: x = 0; y += sh + 1; sh = 0
        place.append((im, x, y)); meta[k].append([x, y, im.width, im.height]); x += im.width + 1; sh = max(sh, im.height)
at = Image.new('RGBA', (Wd, y + sh + 1))
for im, px, py in place: at.paste(im, (px, py))
at.save(os.path.join(OUT, 'whlfx.webp'), lossless=True); json.dump(meta, open(os.path.join(OUT, 'whlfx.json'), 'w'))
pv = Image.new('RGBA', (at.width * 2, at.height * 2), (30, 20, 40, 255)); pv.alpha_composite(at.resize((at.width * 2, at.height * 2), Image.NEAREST)); pv.save('build/whlfx_prev.png')
print(at.size, {k: len(v) for k, v in meta.items()})
