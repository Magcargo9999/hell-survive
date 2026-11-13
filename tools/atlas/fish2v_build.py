"""공허의 마해룡 새 디자인 (v10.47): 받은 시트 5장(투명 배경)을 칸별로 잘라 fish2.webp 의 몸 그룹(i2·w2·a2·h2·d2)을 바꾼다.
수압 원(press)·포식자의 파도(wave)는 지금 fish2.webp 의 그림을 그대로 옮긴다. 자르기 · 배율만 (재색칠 없음).
실행: python3 tools/atlas/fish2v_build.py <대기 3x2> <공격 3x2> <이동 4x2> <사망 3x2> <피격 2x2>
- 칸 경계는 고르게 나눈 자리 둘레(±70px)에서 가장 빈 세로줄 · 가로줄
- 시트마다 그림 크기가 달라서, 각 시트 첫 칸의 몸 면적(알파 합)이 대기 첫 칸과 같아지게 배율을 맞춘다 → 대기 첫 칸 높이 H0 px
- 기준점(ax, ay) = 칸 안 고정 위치(가로 가운데 · 그 줄 그림들의 공통 바닥) → 프레임끼리 흔들리지 않는다. 몸은 오른쪽을 본다."""
import sys, os, json, re
import numpy as np
from PIL import Image
H0 = 150
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
def rgba(p): return np.asarray(Image.open(p).convert('RGBA'))
def valley(prof, c, w=70):
    lo, hi = max(1, c - w), min(len(prof) - 1, c + w); return lo + int(np.argmin(prof[lo:hi]))
def grid(A, nc, nr):
    al = A[..., 3].astype(float); H, W = al.shape
    ys = [0] + [valley(al.sum(1), H * k // nr) for k in range(1, nr)] + [H]
    cells = []
    for r in range(nr):
        band = al[ys[r]:ys[r + 1]]
        xs = [0] + [valley(band.sum(0), W * k // nc) for k in range(1, nc)] + [W]
        rowc = []
        for c in range(nc):
            sub = A[ys[r]:ys[r + 1], xs[c]:xs[c + 1]].copy(); m = sub[..., 3] > 12
            sub[~m] = 0; rowc.append(sub)
        cells.append(rowc)
    return cells
def area(c): return (c[..., 3].astype(float) / 255).sum()
SPEC = [('i2', 3, 2), ('a2', 3, 2), ('w2', 4, 2), ('d2', 3, 2), ('h2', 2, 2)]
paths = sys.argv[1:6]
groups = {}; base = None
for (k, nc, nr), p in zip(SPEC, paths):
    cells = grid(rgba(p), nc, nr); first = cells[0][0]
    if base is None:
        ys = np.where(first[..., 3].max(1) > 12)[0]; s = H0 / (ys[-1] - ys[0] + 1); base = area(first) * s * s
    else: s = (base / area(first)) ** 0.5
    fr = []
    for rowc in cells:
        for c in rowc:
            al = c[..., 3] > 12; ys_, xs_ = np.where(al)
            if not len(ys_): continue
            fr.append((c, s))
    groups[k] = fr; print(k, 'scale %.3f' % s, len(fr))
# 배율 적용 · 칸 안 기준점: 가로 가운데, 세로는 그 그룹 모든 칸의 그림 바닥 중 가장 아래
out = {}
for k, fr in groups.items():
    bottoms = [np.where(c[..., 3].max(1) > 12)[0][-1] for c, s in fr]; B = max(bottoms)
    res = []
    for c, s in fr:
        im = Image.fromarray(c).convert('RGBa'); W, H = im.size
        im = im.resize((max(1, round(W * s)), max(1, round(H * s))), Image.LANCZOS).convert('RGBA')
        a = np.asarray(im); m = a[..., 3] > 8; ys_, xs_ = np.where(m)
        x0, x1, y0, y1 = xs_.min(), xs_.max() + 1, ys_.min(), ys_.max() + 1
        ax, ay = W * s / 2 - x0, B * s - y0
        res.append((im.crop((x0, y0, x1, y1)), round(ax, 1), round(ay, 1)))
    out[k] = res
# 옛 아틀라스에서 press · wave 가져오기
s = open(os.path.join(ROOT, 'src/game_template.html'), encoding='utf8').read()
OLD = json.loads(re.search(r'const FISHA2 = (\{.*?\});', s).group(1))
old = Image.open(os.path.join(ROOT, 'src/assets/fish/fish2.webp')).convert('RGBA')
for k in ('press', 'wave'):
    x, y, w, h, ax, ay = OLD[k][0]; out[k] = [(old.crop((x, y, x + w, y + h)), ax, ay)]
# 줄 단위 포장
MAXW = 1600; x = y = rowh = 0; place = {}
for k in ['i2', 'w2', 'a2', 'h2', 'd2', 'press', 'wave']:
    for i, (im, ax, ay) in enumerate(out[k]):
        if x + im.width > MAXW: x = 0; y += rowh + 2; rowh = 0
        place.setdefault(k, []).append([x, y, im.width, im.height, ax, ay]); x += im.width + 2; rowh = max(rowh, im.height)
AT = Image.new('RGBA', (MAXW, y + rowh), (0, 0, 0, 0))
for k, lst in place.items():
    for (px, py, w, h, ax, ay), (im, _, _) in zip(lst, out[k]): AT.paste(im, (px, py))
AT.save(os.path.join(ROOT, 'src/assets/fish/fish2.webp'), lossless=True, quality=100)
print(AT.size); print('JSON', json.dumps(place, separators=(',', ':')))
