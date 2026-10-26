"""v9.60 심장 7종(파리지옥·어인왕·백곰·루드라·릴세르카·화염죄수·불구렁이) → heart.webp 9~15번째 줄.
시트 7장(2×2: 레어·에픽·유니크·레전더리, 검은 배경)을 이 순서대로. 첫 장(파리지옥)은 칸마다 액자 테두리선이 있어 안쪽만 쓰고 모서리 장식을 지운다.
배경 제거(테두리에서 이어진 거의 검은 영역 투명화)·자르기·배율 조정만. 사용: python3 heart7_build.py <s1.png> … <s7.png>  (이미 있는 줄은 다시 쓴다)"""
import sys, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
S, FIRST = 256, 8
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
out = os.path.join(root, 'src', 'assets', 'heart', 'heart.webp')
files = sys.argv[1:8]; N = len(files)
base = Image.open(out).convert('RGBA').crop((0, 0, S * 4, S * FIRST))
A = Image.new('RGBA', (S * 4, S * (FIRST + N)), (0, 0, 0, 0)); A.alpha_composite(base, (0, 0))
FRAME = [(20, 18, 616, 603), (637, 18, 1233, 603), (20, 626, 616, 1226), (637, 626, 1233, 1226)]   # 첫 장 칸 안쪽(액자선 제외)
for r, f in enumerate(files):
    im = Image.open(f).convert('RGB'); w, h = im.size; a = np.array(im)
    for c in range(4):
        if r == 0:
            x0, y0, x1, y1 = FRAME[c]; q = a[y0:y1, x0:x1].copy()
            m = 56; q[:m, :m] = 0; q[:m, -m:] = 0; q[-m:, :m] = 0; q[-m:, -m:] = 0   # 모서리 장식
        else:
            x0, y0 = (c % 2) * w // 2, (c // 2) * h // 2; q = a[y0:y0 + h // 2, x0:x0 + w // 2]
        dark = q.max(2) <= 14
        lab, n = ndi.label(dark); edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
        bg = np.isin(lab, list(edge))
        fl, fn = ndi.label(~bg); mxv = ndi.maximum(q.max(2), fl, range(1, fn + 1))   # 배경에 섞인 어두운 잡티(최대 밝기 40 미만 덩어리) 제거
        bg |= np.isin(fl, [i + 1 for i, v in enumerate(mxv) if v < 40])
        im2 = Image.fromarray(np.dstack([q, np.where(bg, 0, 255).astype(np.uint8)]), 'RGBA'); im2 = im2.crop(im2.getchannel('A').getbbox())
        k = (S - 6) / max(im2.size); im2 = im2.resize((max(1, round(im2.width * k)), max(1, round(im2.height * k))), Image.LANCZOS)
        A.alpha_composite(im2, (c * S + (S - im2.width) // 2, (FIRST + r) * S + (S - im2.height) // 2))
A.save(out, quality=92, method=6); print(out, os.path.getsize(out) // 1024, 'KB', A.size)
p = Image.new('RGBA', (S * 4, S * N), (60, 40, 80, 255)); p.alpha_composite(A.crop((0, FIRST * S, S * 4, (FIRST + N) * S)))
p.save(os.path.join(root, 'build', 'h7_prev.png'))
