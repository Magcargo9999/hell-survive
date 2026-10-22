"""v6.44 타락천사 프레임 다시 자르기 (원본 시트 없이 지금 an.webp에서)
옛 an_build.py는 줄마다 칸을 '같은 폭'으로 나눴는데, 실제 그림은 폭이 제각각이라
한 칸에 옆 그림 반쪽이 같이 들어가 있었다 (특히 흑화 줄 → 2페이즈 내내 사각형으로 잘린 몸이 보임).
줄마다 칸들을 이어 붙여 원래 띠를 되살린 뒤, 그림 사이 빈틈(손으로 고른 위치 ±20 안의 가장 빈 세로줄)에서 다시 자른다.
자르기 · 잘린 가장자리 알파 페이드(마스크) · 옆 그림 조각 제거만 — 색은 건드리지 않는다.
한 번만 실행: python3 tools/atlas/an_fix.py  (an.webp 덮어쓰고 템플릿의 ANB 표를 바꾼다)"""
import re, json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
T = 'src/game_template.html'; P = 'src/assets/an/an.webp'
src = open(T, encoding='utf-8').read()
m = re.search(r'const ANB = (\{.*?\});', src); ANB = json.loads(m.group(1))
A = np.array(Image.open(P).convert('RGBA'))
CUT = {'idle': [160, 315, 475, 650, 805, 945], 'atk': [185, 340, 460, 640, 835, 1005, 1210],
       'death': [132, 246, 365], 'trans': [165, 310, 462, 650, 840, 1134]}   # 그림 사이 대략 위치 (run · hit은 이미 맞음)
FE = 20   # 잘린 가장자리 페이드 폭(원본 px)
def band(L):
    top = max(r[5] for r in L); bot = max(r[3] - r[5] for r in L); B = np.zeros((top + bot, sum(r[2] for r in L), 4), np.uint8); x = 0
    for r in L: B[top - r[5]:top - r[5] + r[3], x:x + r[2]] = A[r[1]:r[1] + r[3], r[0]:r[0] + r[2]]; x += r[2]
    return B, top
info = {}
for nm, L in ANB.items():
    if nm not in CUT: info[nm] = [(A[r[1]:r[1] + r[3], r[0]:r[0] + r[2]].copy(), r[4], r[5]) for r in L]; continue
    B, top = band(L); W = B.shape[1]; col = (B[..., 3] > 60).sum(0).astype(float); col = np.convolve(col, np.ones(3) / 3, 'same')
    cuts = [0] + [c - 20 + int(np.argmin(col[c - 20:c + 21])) for c in CUT[nm]] + [W]
    for j in range(len(cuts) - 1):
        c = B[:, cuts[j]:cuts[j + 1]].copy(); a = c[..., 3].astype(float); w = c.shape[1]
        lab, n = ndi.label(a > 0, structure=np.ones((3, 3)))   # 잘린 쪽 가장자리에 붙은 작은 조각 = 옆 그림 부스러기
        if n:
            sz = ndi.sum(a > 0, lab, range(1, n + 1)); big = np.argmax(sz) + 1
            ed = set()
            if j > 0: ed |= set(np.unique(lab[:, :3]))
            if j < len(cuts) - 2: ed |= set(np.unique(lab[:, -3:]))
            for i in ed - {0, big}:
                if sz[i - 1] < 600: a[lab == i] = 0
        xs = np.arange(w, dtype=float); k = np.ones(w)
        if j > 0: k = np.minimum(k, (xs + 1) / FE)
        if j < len(cuts) - 2: k = np.minimum(k, (w - xs) / FE)
        a = a * np.clip(k, 0, 1)[None, :]
        if (a[0] > 60).sum() > 3: a = a * np.clip((np.arange(a.shape[0]) + 1) / FE, 0, 1)[:, None]   # 시트 칸 위쪽에서 잘린 것도 페이드
        c[..., 3] = a.astype(np.uint8)
        op = c[..., 3] > 160; ys, xx = np.where(op); bot = int(np.percentile(ys, 99.6))
        lx = np.where(op[int(bot - (bot - ys.min()) * 0.14):bot + 1])[1]; ax = float(np.median(lx))
        ys, xx = np.where(c[..., 3] > 6); a0, a1, b0, b1 = ys.min(), ys.max() + 1, xx.min(), xx.max() + 1
        info.setdefault(nm, []).append((c[a0:a1, b0:b1], ax - b0, top - a0))
    print(nm, 'cuts', cuts)
def floor_cut(c):   # 맨 아래 5줄의 넓은 바닥 그림자 띠: 바로 위 줄의 몸 폭(±6) 밖은 지운다
    a = c[..., 3]; h = a.shape[0]; xs = np.where(a[h - 6] > 60)[0]
    if xs.size: a[h - 5:, :max(0, xs.min() - 6)] = 0; a[h - 5:, xs.max() + 7:] = 0
    return c
def bottom_fade(c, ax, nm):   # 시트 칸 아래 경계에서 평평하게 잘린 날개·기운: 발(앵커 ±40) 밖은 아래쪽 FE줄을 페이드
    if nm not in CUT: return c
    a = c[..., 3].astype(float); h, w = a.shape; ry = np.clip((h - np.arange(h)) / FE, 0, 1)[:, None]
    far = np.clip((np.abs(np.arange(w) - ax) - 40) / 15, 0, 1)[None, :]
    c[..., 3] = (a * (1 - far * (1 - ry))).astype(np.uint8); return c
for nm in info: info[nm] = [(bottom_fade(c, ax, nm), ax, ay) for c, ax, ay in info[nm]]
for nm in info: info[nm] = [(floor_cut(c.copy()), ax, ay) for c, ax, ay in info[nm]]
x = y = sh = 0; pos = {}; Wd = 1600
for nm in ANB:
    for i, (c, ax, ay) in enumerate(info[nm]):
        h, w = c.shape[:2]
        if x + w > Wd: x = 0; y += sh + 2; sh = 0
        pos[(nm, i)] = (x, y); x += w + 2; sh = max(sh, h)
at = np.zeros((y + sh, Wd, 4), np.uint8); meta = {}
for (nm, i), (x, y) in pos.items():
    c, ax, ay = info[nm][i]; h, w = c.shape[:2]; at[y:y + h, x:x + w] = c; meta.setdefault(nm, []).append([x, y, w, h, round(float(ax), 1), int(ay)])
Image.fromarray(at).save(P, lossless=True, method=6)
src = src.replace(m.group(0), 'const ANB = ' + json.dumps(meta, separators=(',', ':')) + ';', 1); open(T, 'w', encoding='utf-8').write(src)
print(at.shape, {k: [f[2] for f in v] for k, v in meta.items()})
