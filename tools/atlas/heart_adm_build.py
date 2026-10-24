"""썩어버린 해군 제독 심장(2×2 시트: 레어·에픽·유니크·레전더리, 검은 배경) → heart.webp 7번째 줄에 덧붙임.
배경 제거(테두리에서 이어진 거의 검은 영역 투명화)·자르기·배율 조정만. 사용: python3 heart_adm_build.py <시트.png>  (이미 7줄이면 7번째 줄을 다시 쓴다)"""
import sys, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
S = 256
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'src', 'assets', 'heart', 'heart.webp')
base = Image.open(out).convert('RGBA').crop((0, 0, S * 4, S * 6))
A = Image.new('RGBA', (S * 4, S * 7), (0, 0, 0, 0)); A.alpha_composite(base, (0, 0))
im = Image.open(sys.argv[1]).convert('RGB'); w, h = im.size; a = np.array(im)
dark = a.max(2) <= 12
lab, n = ndi.label(dark); edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
bg = np.isin(lab, list(edge))
rgba = np.dstack([a, np.where(bg, 0, 255).astype(np.uint8)])
full = Image.fromarray(rgba, 'RGBA')
for c in range(4):
    x0, y0 = (c % 2) * w // 2, (c // 2) * h // 2
    q = full.crop((x0, y0, x0 + w // 2, y0 + h // 2)); bb = q.getchannel('A').getbbox(); q = q.crop(bb)
    k = (S - 6) / max(q.size); q = q.resize((max(1, round(q.width * k)), max(1, round(q.height * k))), Image.LANCZOS)
    A.alpha_composite(q, (c * S + (S - q.width) // 2, 6 * S + (S - q.height) // 2))
A.save(out, quality=92, method=6); print(out, os.path.getsize(out) // 1024, 'KB', A.size)
bgp = Image.new('RGBA', A.size, (60, 40, 80, 255)); bgp.alpha_composite(A.crop((0, 6 * S, S * 4, 7 * S)).resize((1024, 256)) if False else A); bgp.crop((0, 6 * S, S * 4, 7 * S)).save(os.path.join(os.path.dirname(out), '..', '..', '..', 'build', 'adm_heart_prev.png'))
