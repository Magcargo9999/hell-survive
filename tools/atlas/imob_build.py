"""v8.99 팔한지옥(지하 21~25층) 잡몹 9종 → src/assets/ice/imob.webp (2프레임 × 9종, 칸 108×114, 발 아래·가운데 맞춤)
시트(build/ice/): mobs.png(필드 몬스터 스프라이트 시트 1448×1086) · peng.png(팽귄 병사) · icic.png(고드름 괴물) · slime.png(빙하 슬라임)
자르기 · 배경(어두운 남색) 제거 · 배율 조정(칸에 맞춤)만 — 재색칠 없음."""
import numpy as np, os, sys, json
from PIL import Image
from scipy import ndimage as ndi
IN = 'build/ice/'; OUT = 'src/assets/ice/'; os.makedirs(OUT, exist_ok=True)
CW, CH = 108, 114

def fgmask(a, thr):
    dark = a.max(2) <= thr
    lab, n = ndi.label(dark); edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    fg = ~np.isin(lab, list(edge))
    lab2, n2 = ndi.label(fg)   # 칸 테두리선(가늘고 긴 줄) 제거
    for i, sl in enumerate(ndi.find_objects(lab2)):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if (h <= 8 and w >= 40) or (w <= 5 and h >= 16): fg[lab2 == i + 1] = False
    return fg

def blobs(path, box, thr=44, gap=6, minw=14, minh=14):
    im = np.array(Image.open(IN + path).convert('RGB')).astype(int); x0, y0, x1, y1 = box; a = im[y0:y1, x0:x1]
    fg = fgmask(a, thr); fg = ndi.binary_closing(fg, structure=np.ones((3, 3)), iterations=1)
    cols = fg.sum(0) > 0; out = []; x = 0; W = len(cols)
    while x < W:   # 세로로 비어 있는 틈으로 칸 나누기
        if cols[x]:
            s = x
            while x < W and (cols[x] or (x + gap < W and cols[x:x + gap].any())): x += 1
            seg = fg[:, s:x]
            if seg.sum() > 40:
                ys, xs = np.where(seg)
                if xs.max() - xs.min() >= minw and ys.max() - ys.min() >= minh: out.append((s + xs.min(), ys.min(), s + xs.max() + 1, ys.max() + 1, fg[:, s:x], a[:, s:x]))
        x += 1
    return out, fg, a

def sprite(a, fg, bx):
    x0, y0, x1, y1 = bx[:4]; seg = bx[4]; img = bx[5]
    lab, n = ndi.label(seg)   # 가장 큰 덩어리와 가까운 조각만 남기지 않고, 칸 안의 모든 전경을 유지(빙결 조각 포함)
    rgba = np.dstack([img.astype(np.uint8), (seg * 255).astype(np.uint8)])[y0:y1, :]
    cols = np.where(seg.any(0))[0]; rgba = rgba[:, cols.min():cols.max() + 1]
    return Image.fromarray(rgba, 'RGBA')

def fit(sp, maxh=100, maxw=104):
    w, h = sp.size; k = min(maxh / h, maxw / w)
    if k >= 1.9: k = int(k)   # 작은 그림은 정수 배(2배)로 키운다
    nw, nh = max(1, round(w * k)), max(1, round(h * k))
    sp = sp.resize((nw, nh), Image.NEAREST if k >= 1.9 else Image.LANCZOS)
    c = Image.new('RGBA', (CW, CH), (0, 0, 0, 0)); c.alpha_composite(sp, ((CW - nw) // 2, CH - 2 - nh)); return c, nh

SP = []   # (이름, 순위 r, 이속, [두 프레임], 키)
def panel(path, box, pick, name, **kw):
    bl, fg, a = blobs(path, box, **kw)
    fr = [sprite(a, fg, bl[i]) for i in pick]; return fr, len(bl)

TOP = (313, 398); BOT = (813, 893)
walk = [  # 이름, 시트 상자, 고를 프레임
    ('동상 걸린 해골 망령', (75, TOP[0], 478, TOP[1]), [0, 2]),
    ('빙결 해골 승려',     (560, TOP[0], 955, TOP[1]), [0, 2]),
    ('설한 늑대령',        (1030, TOP[0], 1445, TOP[1]), [0, 2]),
    ('얼어붙은 죄수',      (75, BOT[0], 478, BOT[1]), [0, 2]),
    ('한빙 작은 귀신',     (560, BOT[0], 955, BOT[1]), [0, 2]),
    ('빙저의 기어가는 시체', (1030, BOT[0], 1445, BOT[1]), [0, 2]),
]
cells = []; meta = []
for name, box, pick in walk:
    fr, n = panel('mobs.png', box, pick, name); fitted = [fit(f) for f in fr]
    # 두 프레임의 크기가 다르면 같은 배율로 맞춘다 (큰 쪽 기준)
    cells.append([c for c, _ in fitted]); meta.append((name, max(h for _, h in fitted), n))
def segs(path, box, cuts, pick, **kw):   # 가로로 붙어 있는 칸은 직접 정한 경계(cuts)로 나눈다
    xs = [box[0]] + cuts + [box[2]]; out = []
    for i in pick:
        bl, fg, a = blobs(path, (xs[i], box[1], xs[i + 1], box[3]), **kw)
        bl = max(bl, key=lambda q: q[4].sum()); out.append(sprite(a, fg, bl))
    return out
extra = [('팽귄 병사', 'peng.png', (8, 44, 424, 214), [112], [0, 1], dict(thr=55)),
         ('고드름 괴물', 'icic.png', (8, 30, 402, 152), [123, 218, 304], [0, 1], dict(thr=50, gap=3)),
         ('빙하 슬라임', 'slime.png', (8, 30, 388, 138), [97, 182, 288], [0, 1], dict(thr=50, gap=3))]
for name, path, box, cuts, pick, kw in extra:
    fr = segs(path, box, cuts, pick, **kw); fitted = [fit(f) for f in fr]
    cells.append([c for c, _ in fitted]); meta.append((name, max(h for _, h in fitted), len(fr)))
A = Image.new('RGBA', (CW * len(cells), CH * 2), (0, 0, 0, 0))
for i, fr in enumerate(cells):
    for k, c in enumerate(fr): A.alpha_composite(c, (i * CW, k * CH))
A.save(OUT + 'imob.webp', lossless=True, method=6); json.dump([[m[0], m[1]] for m in meta], open(OUT + 'imob.json', 'w'), ensure_ascii=False)
print(A.size, meta)
bg = Image.new('RGBA', A.size, (90, 120, 160, 255)); bg.alpha_composite(A); bg.save('build/ice/imob_prev.png')
