"""미믹 시트(사용자 첨부) → src/assets/mimic/mimic.webp + mimic.json  (자르기만, 색 수정 없음)
사용: python3 tools/atlas/mimic_build.py <시트.png>
줄: 0 대기(7) · 1 달리기(7) · 2 혀 휘두르기(6) · 3 피격→쓰러지는 시작(6) · 4 죽음(5). 큰 그림(맨 위)은 안 쓴다."""
import sys, json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
src = sys.argv[1] if len(sys.argv) > 1 else '/root/.claude/uploads/6ffacf50-d750-5d30-b287-654ee717bc39/56ca01d2-image.png'
im = Image.open(src).convert('RGBA'); a = np.array(im); al = a[..., 3]
lab, n = ndi.label(ndi.binary_dilation(al > 40, iterations=6)); objs = ndi.find_objects(lab)
box = []
for i, o in enumerate(objs):
    ys, xs = o; box.append([xs.start, ys.start, xs.stop, ys.stop, int(((lab[o] == i + 1) & (al[o] > 40)).sum())])
big = [b for b in box if b[4] > 4000 and b[1] > 300]; small = [b for b in box if b[4] <= 4000 and b[1] > 300]
for s in small:   # 떨어져 나간 작은 조각(혀 방울)은 x가 겹치는 가장 가까운 큰 그림에 붙인다
    cx = (s[0] + s[2]) / 2; best = min(big, key=lambda b: (0 if b[0] - 6 <= cx <= b[2] + 6 else 9999) + abs(b[1] - s[1]))
    best[0] = min(best[0], s[0]); best[1] = min(best[1], s[1]); best[2] = max(best[2], s[2]); best[3] = max(best[3], s[3])
rows = []
for b in sorted(big, key=lambda b: b[1] + (b[3] - b[1]) / 2):
    cy = (b[1] + b[3]) / 2
    for r in rows:
        if abs(r[0] - cy) < 70: r[1].append(b); break
    else: rows.append([cy, [b]])
rows = [sorted(r[1], key=lambda b: b[0]) for r in rows]
print([len(r) for r in rows])
r_, g_, b_ = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
chest = (al > 200) & (g_ - b_ > 18)   # 갈색·금색 상자 몸통 (혀는 g≈b)
PAD = 2; W = max(sum(b[2] - b[0] + PAD for b in r) for r in rows); H = sum(max(b[3] - b[1] for b in r) + PAD for r in rows)
out = Image.new('RGBA', (W, H), (0, 0, 0, 0)); fr = []; y = 0
for r in rows:
    h = max(b[3] - b[1] for b in r); x = 0; row = []
    for b in r:
        w = b[2] - b[0]; out.paste(im.crop((b[0], b[1], b[2], b[3])), (x, y))
        m = chest[b[1]:b[3], b[0]:b[2]]; ys, xs = np.nonzero(m)
        ax = int((xs.min() + xs.max()) / 2) if len(xs) else w // 2; ay = int(ys.max()) if len(ys) else b[3] - b[1] - 1
        row.append([x, y, w, b[3] - b[1], ax, ay]); x += w + PAD
    fr.append(row); y += h + PAD
out.save('src/assets/mimic/mimic.webp', lossless=True, method=6)
json.dump({'w': W, 'h': H, 'rows': fr}, open('tools/atlas/mimic.json', 'w'), separators=(',', ':'))
print(W, H)
