"""광기의 가면 성유물 도트 → src/assets/final/relmask.webp (자르기 + 가장자리에서 이어진 어두운 배경 제거 + 정사각 배치만)
사용: python3 relmask_build.py <광기의 가면.png>"""
import sys, os
from PIL import Image, ImageDraw
import numpy as np
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
im = Image.open(sys.argv[1]).convert('RGBA').crop((40, 20, 690, 1010))
a = np.array(im); lum = a[..., :3].max(axis=2)
mask = Image.fromarray(((lum < 34) * 255).astype('uint8'))   # 아주 어두운 곳만 후보
w, h = im.size; fl = Image.new('L', (w, h), 0)
from scipy import ndimage
lab, n = ndimage.label(np.array(mask) > 0)
edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
bg = np.isin(lab, list(edge)); a[..., 3] = np.where(bg, 0, 255)
im = Image.fromarray(a); im = im.crop(im.getchannel('A').getbbox())
S = 320; k = min(S / im.width, S / im.height) * 0.96
im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
c = Image.new('RGBA', (S, S), (0, 0, 0, 0)); c.alpha_composite(im, ((S - im.width) // 2, (S - im.height) // 2))
c.save(os.path.join(ROOT, 'src/assets/final/relmask.webp'), lossless=True)
bgc = Image.new('RGBA', (S, S), (90, 40, 120, 255)); bgc.alpha_composite(c); bgc.save('build/relmask_prev.png')
