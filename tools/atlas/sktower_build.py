"""스켈레톤 마왕 해골 첨탑(사용자 시트, 마젠타 배경) → src/assets/sk/sktower.webp  (배경 제거 · 자르기 · 축소만, 색 수정 없음)
사용: python3 tools/atlas/sktower_build.py <시트.png>"""
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi
src = sys.argv[1] if len(sys.argv) > 1 else '/root/.claude/uploads/6ffacf50-d750-5d30-b287-654ee717bc39/d14f9d02-image.png'
im = Image.open(src).convert('RGBA'); a = np.array(im); r, g, b = [a[..., i].astype(int) for i in range(3)]
mag = (r > 140) & (b > 140) & (g < 120) & (abs(r - b) < 70)
lab, n = ndi.label(mag); border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
bg = np.isin(lab, list(border))
fr = ndi.binary_dilation(bg, iterations=2) & mag   # 가장자리에 남은 마젠타 테두리
pure = (r > 190) & (b > 190) & (g < 100)   # 팔·몸통 사이 틈으로 보이는 배경(테두리와 안 이어진 것)도 지운다
a[bg | fr | pure, 3] = 0
ys, xs = np.nonzero(a[..., 3] > 0); x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
out = Image.fromarray(a).crop((x0, y0, x1, y1)); print(out.size)
H = 380; W = round(out.width * H / out.height); out = out.resize((W, H), Image.BOX); print(out.size)
out.save('src/assets/sk/sktower.webp', lossless=True, method=6)
