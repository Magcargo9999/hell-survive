"""타락한 원예의 여왕 심장(1×4 가로 시트: 레어·에픽·유니크·레전더리, 아래 글자, 검은 배경) → heart.webp 8번째 줄.
배경 제거(테두리에서 이어진 거의 검은 영역 투명화)·자르기(아래 글자 줄 제외)·배율 조정만. 사용: python3 heart_qn_build.py <시트.png>"""
import sys, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
S, ROW = 256, 7
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'src', 'assets', 'heart', 'heart.webp')
base = Image.open(out).convert('RGBA').crop((0, 0, S * 4, S * ROW))
A = Image.new('RGBA', (S * 4, S * (ROW + 1)), (0, 0, 0, 0)); A.alpha_composite(base, (0, 0))
im = Image.open(sys.argv[1]).convert('RGB'); w, h = im.size
im = im.crop((0, 0, w, int(h * 0.825))); w, h = im.size   # 아래 'Rare/Epic…' 글자 줄 잘라냄
a = np.array(im)
dark = a.max(2) <= 14
lab, n = ndi.label(dark); edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
bg = np.isin(lab, list(edge))
full = Image.fromarray(np.dstack([a, np.where(bg, 0, 255).astype(np.uint8)]), 'RGBA')
for c in range(4):
    q = full.crop((c * w // 4, 0, (c + 1) * w // 4, h)); q = q.crop(q.getchannel('A').getbbox())
    k = (S - 6) / max(q.size); q = q.resize((max(1, round(q.width * k)), max(1, round(q.height * k))), Image.LANCZOS)
    A.alpha_composite(q, (c * S + (S - q.width) // 2, ROW * S + (S - q.height) // 2))
A.save(out, quality=92, method=6); print(out, os.path.getsize(out) // 1024, 'KB', A.size)
p = Image.new('RGBA', (S * 4, S), (60, 40, 80, 255)); p.alpha_composite(A.crop((0, ROW * S, S * 4, (ROW + 1) * S)))
p.save(os.path.join(os.path.dirname(out), '..', '..', '..', 'build', 'qn_heart_prev.png'))
