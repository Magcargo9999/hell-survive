"""v10.01 지옥의 화염 호랑이 심장 → heart.webp 16번째 줄(15 = 0부터). 시트 1장(2×2: 레어·에픽·유니크·레전더리, 검은 배경).
배경 제거(테두리에서 이어진 거의 검은 영역 투명화)·자르기·배율 조정만. 사용: python3 heart_tig_build.py <시트.png>  (이미 있는 줄은 다시 쓴다)"""
import sys, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
S, ROW = 256, 15
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
out = os.path.join(root, 'src', 'assets', 'heart', 'heart.webp')
base = Image.open(out).convert('RGBA').crop((0, 0, S * 4, S * ROW))
A = Image.new('RGBA', (S * 4, S * (ROW + 1)), (0, 0, 0, 0)); A.alpha_composite(base, (0, 0))
im = Image.open(sys.argv[1]).convert('RGB'); w, h = im.size; a = np.array(im)
for c in range(4):
    x0, y0 = (c % 2) * w // 2, (c // 2) * h // 2; q = a[y0:y0 + h // 2, x0:x0 + w // 2]
    dark = q.max(2) <= 14
    lab, n = ndi.label(dark); edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(edge))
    fl, fn = ndi.label(~bg); mxv = ndi.maximum(q.max(2), fl, range(1, fn + 1))
    bg |= np.isin(fl, [i + 1 for i, v in enumerate(mxv) if v < 40])
    im2 = Image.fromarray(np.dstack([q, np.where(bg, 0, 255).astype(np.uint8)]), 'RGBA'); im2 = im2.crop(im2.getchannel('A').getbbox())
    k = (S - 6) / max(im2.size); im2 = im2.resize((max(1, round(im2.width * k)), max(1, round(im2.height * k))), Image.LANCZOS)
    A.alpha_composite(im2, (c * S + (S - im2.width) // 2, ROW * S + (S - im2.height) // 2))
A.save(out, quality=92, method=6); print(out, os.path.getsize(out) // 1024, 'KB', A.size)
p = Image.new('RGBA', (S * 4, S), (60, 40, 80, 255)); p.alpha_composite(A.crop((0, ROW * S, S * 4, (ROW + 1) * S)))
p.save(os.path.join(root, 'build', 'htig_prev.png'))
