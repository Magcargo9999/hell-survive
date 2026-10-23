"""이독버섯 마왕 심장(4등급, 가로 1줄 시트) → heart.webp 6번째 줄에 덧붙임. 자르기·배율 조정만. 사용: python3 heart_tox_build.py <시트.png>
(주의: 이미 6줄이면 6번째 줄을 다시 쓴다)"""
import sys, os
from PIL import Image
S = 256
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'src', 'assets', 'heart', 'heart.webp')
base = Image.open(out).convert('RGBA').crop((0, 0, S * 4, S * 5))
A = Image.new('RGBA', (S * 4, S * 6), (0, 0, 0, 0)); A.alpha_composite(base, (0, 0))
im = Image.open(sys.argv[1]).convert('RGBA'); w, h = im.size
import numpy as np
al = np.array(im.getchannel('A')) > 24; cols = al.any(0); runs = []; s = None
for x, v in enumerate(cols):
    if v and s is None: s = x
    if not v and s is not None:
        if x - s > 20: runs.append((s, x))
        s = None
if s is not None: runs.append((s, w))
assert len(runs) == 4, runs
for c, (x0, x1) in enumerate(runs):
    q = im.crop((x0, 0, x1, h)); bb = q.getchannel('A').point(lambda v: 255 if v > 24 else 0).getbbox(); q = q.crop(bb)
    k = (S - 6) / max(q.size); q = q.resize((max(1, round(q.width * k)), max(1, round(q.height * k))), Image.LANCZOS)
    A.alpha_composite(q, (c * S + (S - q.width) // 2, 5 * S + (S - q.height) // 2))
A.save(out, quality=92, method=6); print(out, os.path.getsize(out) // 1024, 'KB', A.size)
