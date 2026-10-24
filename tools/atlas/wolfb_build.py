"""토끼 후드 늑대 스킨(wolfB) 시트(1448×1086, 검은 배경, 모두 오른쪽을 봄) → src/assets/skin/wolfB.{webp,json} + wolfB_art.webp
자르기·배경 제거만 (색 수정 없음). 사용: python3 tools/atlas/wolfb_build.py <시트.png>
프레임 [x, y, w, h, 기준x(몸통 가운데), 기준y(발)] — 키 = 게임 동작 이름(idle/walk/attack/hit/death)"""
import sys, os, json
import numpy as np
from PIL import Image
from scipy import ndimage as nd
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'src/assets/skin')
im = Image.open(sys.argv[1]).convert('RGB'); A = np.array(im).astype(int)
m = A.max(2) > 20
lab, n = nd.label(m, structure=np.ones((3, 3))); objs = nd.find_objects(lab)
keep = np.zeros_like(m); artm = np.zeros_like(m)
for i, sl in enumerate(objs):
    h = sl[0].stop - sl[0].start; w = sl[1].stop - sl[1].start; c = lab == i + 1
    if sl[1].start >= 1062 and 100 <= sl[0].start < 700: artm |= c; continue   # 오른쪽 큰 일러스트(+반짝이·하트)
    if any(t0 - 4 <= sl[0].start and sl[0].stop <= t1 + 4 for t0, t1 in ((108, 138), (290, 320), (472, 502), (653, 682), (831, 860))): continue   # 제목 글자·발바닥
    keep |= c
ROWS = {'idle': (130, 275, 8), 'walk': (320, 455, 8), 'attack': (495, 642, 6), 'hit': (682, 815, 4), 'death': (862, 985, 9)}
tiles = []; frames = {}
for k, (y0, y1, cnt) in ROWS.items():
    occ = keep[y0:y1].any(0); runs = []; s = None
    for x, v in enumerate(occ):
        if v and s is None: s = x
        if not v and s is not None: runs.append((s, x)); s = None
    runs = runs[:cnt]; assert len(runs) == cnt, (k, runs)
    frames[k] = []
    for (a, b) in runs:
        sub = keep[y0:y1, a:b]; sub = nd.binary_fill_holes(sub)
        l2, n2 = nd.label(sub); sz = nd.sum(sub, l2, range(1, n2 + 1)); big = l2 == (int(np.argmax(sz)) + 1)
        ys, xs = np.where(sub); by, bx = np.where(big)
        X0, X1, Y0, Y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        t = np.zeros((Y1 - Y0, X1 - X0, 4), np.uint8); t[:, :, :3] = A[y0 + Y0:y0 + Y1, a + X0:a + X1]; t[:, :, 3] = sub[Y0:Y1, X0:X1] * 255
        tiles.append((k, Image.fromarray(t), int(round((bx.min() + bx.max()) / 2)) - X0, int(by.max() + 1) - Y0)); frames[k].append(None)
W = 1024; x = y = rh = 0; place = []; idx = {k: 0 for k in ROWS}
for k, t, ax, ay in tiles:
    if x + t.width > W: x = 0; y += rh + 2; rh = 0
    place.append((k, t, x, y, ax, ay)); x += t.width + 2; rh = max(rh, t.height)
out = Image.new('RGBA', (W, y + rh), (0, 0, 0, 0))
for k, t, x, y, ax, ay in place:
    out.paste(t, (x, y)); frames[k][idx[k]] = [int(x), int(y), t.width, t.height, int(ax), int(ay)]; idx[k] += 1
out.save(os.path.join(OUT, 'wolfB.webp'), lossless=True); json.dump(frames, open(os.path.join(OUT, 'wolfB.json'), 'w'))
art = np.zeros_like(A, dtype=np.uint8); art[artm] = A[artm]
ac = Image.fromarray(art).crop((1056, 100, 1440, 690)); cv = Image.new('RGB', (560, 590), (0, 0, 0)); cv.paste(ac, ((560 - ac.width) // 2, 0))   # 카드 칸(약 1:1)에 잘리지 않게 검은 여백
cv.save(os.path.join(OUT, 'wolfB_art.webp'), quality=92)
print('wolfB', out.size, {k: [(f[2], f[3]) for f in v][:2] for k, v in frames.items()})
bg = Image.new('RGBA', out.size, (70, 60, 90, 255)); bg.alpha_composite(out); bg.save(os.path.join(ROOT, 'build/wolfb_prev.png'))
